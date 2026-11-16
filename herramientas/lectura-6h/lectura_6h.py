#!/usr/bin/env python3
"""Planificador de la lectura de COLA_TAREAS cada 6 horas (prototipo, OT-2026-016).

Estado: PROTOTIPO SIN DESPLEGAR. Programado y funcionando: NO.

Qué hace
- Recibe una instantánea JSON de la hoja de bitácora (COLA_TAREAS, HANDOFFS,
  PERMISOS y la pestaña CICLOS propuesta), que el Coordinador lee con los
  conectores de Google, y devuelve un plan de ciclo determinista: qué OT
  despachar, inspeccionar, evaluar o bloquear, con el motivo de cada una.
- Calcula la clave de ciclo, el lock con lease y la clave de despacho para la
  idempotencia, y prepara las filas de BITACORA y de CICLOS que el Coordinador
  escribiría. Nunca escribe en Google: no tiene credenciales ni las necesita.

Qué NO hace
- No llama a la herramienta Agent. Despachar es exclusivo del hilo principal
  de Claude Code (CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1).
- No evalúa entregas: solo prepara la lista de archivos que el Coordinador
  debe abrir completos antes de evaluar.
- No contiene enlaces ni IDs de Drive o Sheets. La configuración opcional se
  lee de un archivo externo (LECTURA6H_CONFIG) o de la variable LECTURA6H_CONFIG_JSON.

Uso
    python3 lectura_6h.py cron
    python3 lectura_6h.py planificar --snapshot instantanea.json \
        [--config cfg.json] [--agent-disponible] [--sesion ID] [--ahora ISO]

Solo usa la biblioteca estándar de Python 3.9 o posterior.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

VERSION = "0.1.0"
TZ = ZoneInfo("America/Panama")
HORAS_CICLO = (0, 6, 12, 18)

# Correspondencia entre el nombre del catálogo y el subagent_type de .claude/agents/.
SUBAGENTES = {
    "AGENTE_01_CHARLAS": "agente-01-charlas",
    "AGENTE_02_INVESTIGADOR": "agente-02-investigador",
    "AGENTE_03_AGENDA": "agente-03-agenda",
    "AGENTE_04_ASISTENCIAS": "agente-04-asistencias",
    "AGENTE_05_TAREAS": "agente-05-tareas",
    "AGENTE_06_NORMATIVA": "agente-06-normativa",
    "AGENTE_07_PROGRAMADOR": "agente-07-programador",
    "AGENTE_08_AUDIOVISUAL": "agente-08-audiovisual",
}

ESTADOS_DESPACHABLES = {"asignada", "requiere_correccion"}
ESTADOS_DEP_OK = {"aprobada", "cerrada"}
ESTADOS_SIN_ACCION = {"aprobada", "cerrada", "cancelada", "en_evaluacion", "bloqueada"}
PRIORIDAD = {"alta": 0, "media": 1, "baja": 2}

# Palabras que señalan una acción L3 del contrato (sección 4). Detección
# conservadora: ante la duda, la OT se bloquea hasta que haya un permiso L3
# específico del SUPERVISOR en PERMISOS.
PATRON_L3 = re.compile(
    r"\b(borrar|eliminar|papelera|compartir|publicar|enviar a terceros|"
    r"cambiar permisos|modificar (el )?contrato|modificar (las )?fichas|"
    r"desplegar|despliegue|instalar|producto final|marcar como final)\b",
    re.IGNORECASE,
)
PATRON_OT = re.compile(r"\bOT-\d{4}-\d{3}\b")
PATRON_PENDIENTE = re.compile(r"pendiente de (transferencia|aprobaci)", re.IGNORECASE)
RECURSO_INTERRUPTOR = "LECTURA_6H"

CONFIG_DEFECTO = {
    "dry_run": True,
    "max_trabajos_por_ciclo": 2,
    "max_duracion_min": 90,
    "lease_min": 120,
    "max_reintentos_despacho": 1,
    "umbral_en_curso_h": 24,
    "bloque_bit": ["BIT-2026-0900", "BIT-2026-0949"],
    "minuto_disparo": 7,
}


class ErrorPlan(Exception):
    """Error de datos de entrada que impide planificar el ciclo."""


# ---------------------------------------------------------------- tiempo
def ahora_panama() -> datetime:
    return datetime.now(TZ)


def a_panama(valor: str | datetime) -> datetime:
    if isinstance(valor, datetime):
        dt = valor
    else:
        dt = datetime.fromisoformat(valor)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def parse_fecha_hoja(texto: str) -> datetime | None:
    """Fechas de la hoja: 'AAAA-MM-DD', 'AAAA-MM-DD H:MM' o 'AAAA-MM-DD HH:MM', hora de Panamá."""
    texto = (texto or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt).replace(tzinfo=TZ)
        except ValueError:
            continue
    return None


def fmt_hoja(dt: datetime) -> str:
    return a_panama(dt).strftime("%Y-%m-%d %H:%M")


def clave_ciclo(dt: datetime) -> str:
    """Franja de 6 h a la que pertenece un disparo (los disparos tardíos caen en la misma)."""
    p = a_panama(dt)
    hora = max(h for h in HORAS_CICLO if h <= p.hour)
    return f"CIC-{p:%Y%m%d}-{hora:02d}"


def cron_expresion(minuto: int = 7) -> str:
    if not 0 <= minuto <= 59:
        raise ValueError("minuto fuera de rango")
    horas = ",".join(str(h) for h in HORAS_CICLO)
    return f"CRON_TZ=America/Panama {minuto} {horas} * * *"


def proximos_disparos(expresion: str, desde: datetime, n: int = 4) -> list[datetime]:
    """Interpreta solo la forma que genera cron_expresion (minuto fijo, lista de horas)."""
    m = re.fullmatch(r"CRON_TZ=(\S+) (\d{1,2}) ([\d,]+) \* \* \*", expresion)
    if not m:
        raise ValueError("expresión no soportada por el prototipo")
    tz = ZoneInfo(m.group(1))
    minuto = int(m.group(2))
    horas = sorted(int(h) for h in m.group(3).split(","))
    t = desde.astimezone(tz).replace(second=0, microsecond=0)
    salida: list[datetime] = []
    dia = t.replace(hour=0, minute=0)
    while len(salida) < n:
        for h in horas:
            cand = dia.replace(hour=h, minute=minuto)
            if cand > t and len(salida) < n:
                salida.append(cand)
        dia = (dia + timedelta(days=1)).replace(hour=0, minute=0)
    return salida


# ---------------------------------------------------------------- utilidades
def texto_seguro(valor) -> str:
    """Evita la inyección de fórmulas en celdas (=, +, -, @) y recorta espacios."""
    s = "" if valor is None else str(valor).strip()
    if s and s[0] in "=+-@":
        s = "'" + s
    return s


class AsignadorIds:
    """Asigna IDs BIT consecutivos dentro del bloque reservado, sin repetir los existentes."""

    def __init__(self, bloque: list[str], existentes: list[str]):
        ini, fin = bloque
        self.prefijo = ini.rsplit("-", 1)[0]
        self.actual = int(ini.rsplit("-", 1)[1])
        self.fin = int(fin.rsplit("-", 1)[1])
        self.ancho = len(ini.rsplit("-", 1)[1])
        self.usados = set(existentes)

    def siguiente(self) -> str:
        while self.actual <= self.fin:
            cand = f"{self.prefijo}-{self.actual:0{self.ancho}d}"
            self.actual += 1
            if cand not in self.usados:
                self.usados.add(cand)
                return cand
        raise ErrorPlan("bloque de IDs de bitácora agotado")


def fila_bitacora(registro_id, ahora, accion, recurso, detalle, ot_id="",
                  valor_anterior="", valor_nuevo="", recurso_url="",
                  actividad_id="", autorizado_por="") -> list[str]:
    """Fila de 13 columnas de BITACORA (docs/ESQUEMA_HOJAS.md)."""
    return [texto_seguro(v) for v in (
        registro_id, fmt_hoja(ahora), "AGENTE_00_COORDINADOR", "Claude", actividad_id,
        ot_id, accion, recurso, recurso_url, detalle, valor_anterior, valor_nuevo,
        autorizado_por)]


# ---------------------------------------------------------------- reglas
def dependencias(ot: dict) -> list[str]:
    texto = " ".join(ot.get(c, "") for c in ("descripcion", "entradas_urls"))
    return sorted({x for x in PATRON_OT.findall(texto) if x != ot.get("ot_id")})


def requiere_l3(ot: dict) -> bool:
    texto = " ".join(ot.get(c, "") for c in ("descripcion", "criterios_aceptacion"))
    return bool(PATRON_L3.search(texto))


def permiso_l3_especifico(ot_id: str, permisos: list[dict], hoy: datetime) -> bool:
    for p in permisos:
        if (p.get("nivel", "").startswith("L3")
                and p.get("otorgado_por") == "SUPERVISOR"
                and p.get("estado") == "vigente"
                and ot_id in p.get("alcance", "")
                and vigencia_ok(p.get("vigencia", ""), hoy)):
            return True
    return False


def vigencia_ok(vigencia: str, hoy: datetime) -> bool:
    v = (vigencia or "").strip().lower()
    if v == "indefinida":
        return True
    fecha = parse_fecha_hoja(v)
    return bool(fecha and fecha.date() >= a_panama(hoy).date())


def interruptor(permisos: list[dict], hoy: datetime) -> str:
    """ACTIVO: puede despachar. SOLO_LECTURA: sin autorización. PARADO: interruptor de parada.

    El interruptor es una fila de PERMISOS con recurso LECTURA_6H, nivel L3 y
    otorgado_por SUPERVISOR. Estado 'vigente' activa; 'parado' detiene el ciclo;
    cualquier otro valor, o ninguna fila, deja el ciclo en solo lectura.
    La última fila con ese recurso es la que manda.
    """
    filas = [p for p in permisos if p.get("recurso", "").strip().upper() == RECURSO_INTERRUPTOR]
    if not filas:
        return "SOLO_LECTURA"
    p = filas[-1]
    if p.get("estado") == "parado":
        return "PARADO"
    if (p.get("estado") == "vigente" and p.get("otorgado_por") == "SUPERVISOR"
            and p.get("nivel", "").startswith("L3") and vigencia_ok(p.get("vigencia", ""), hoy)):
        return "ACTIVO"
    return "SOLO_LECTURA"


def clave_despacho(ot: dict) -> str:
    return f"{ot['ot_id']}|{ot.get('estado', '')}|{ot.get('ultima_actualizacion', '')}"


# ---------------------------------------------------------------- lock (pestaña CICLOS propuesta)
@dataclass
class EstadoLock:
    activos: list[dict] = field(default_factory=list)
    caducados: list[dict] = field(default_factory=list)
    completados: set[str] = field(default_factory=set)


def estado_lock(eventos: list[dict], ahora: datetime) -> EstadoLock:
    """Deriva el lock de un registro solo de anexado (adquirir / latido / liberar).

    El orden de las filas es el orden de llegada. Un titular sigue activo
    mientras no haya 'liberar' y su lease (renovado con 'latido') no haya caducado.
    """
    titulares: dict[tuple[str, str], dict] = {}
    est = EstadoLock()
    for i, e in enumerate(eventos):
        k = (e.get("clave_ciclo", ""), e.get("sesion", ""))
        tipo = e.get("evento")
        if tipo == "adquirir":
            titulares[k] = {"fila": i, "clave_ciclo": k[0], "sesion": k[1],
                            "lease_hasta": a_panama(e["lease_hasta"])}
        elif tipo == "latido" and k in titulares:
            titulares[k]["lease_hasta"] = a_panama(e["lease_hasta"])
        elif tipo == "liberar" and k in titulares:
            t = titulares.pop(k)
            if e.get("resultado") == "completado":
                est.completados.add(t["clave_ciclo"])
    for t in sorted(titulares.values(), key=lambda x: x["fila"]):
        (est.activos if t["lease_hasta"] > ahora else est.caducados).append(t)
    return est


def adquirir_lock(almacen, clave: str, sesion: str, ahora: datetime, lease_min: int) -> dict:
    """Protocolo anexar y releer. `almacen` debe ofrecer leer() y anexar(evento).

    1. Si la franja ya se completó, no se repite (disparo duplicado o tardío).
    2. Si hay otro titular con lease vigente, se aborta sin escribir.
    3. Se anexa 'adquirir' y se relee: gana la primera fila activa. Si no es la
       propia, se anexa 'liberar' con resultado 'perdido' y se aborta.
    """
    previo = estado_lock(almacen.leer(), ahora)
    if clave in previo.completados:
        return {"ok": False, "motivo": "ciclo_ya_completado", "caducados": previo.caducados}
    if any(t["sesion"] != sesion for t in previo.activos):
        return {"ok": False, "motivo": "lock_ocupado", "titular": previo.activos[0],
                "caducados": previo.caducados}
    almacen.anexar({"evento": "adquirir", "clave_ciclo": clave, "sesion": sesion,
                    "fecha_hora": ahora.isoformat(),
                    "lease_hasta": (ahora + timedelta(minutes=lease_min)).isoformat()})
    despues = estado_lock(almacen.leer(), ahora)
    ganador = despues.activos[0] if despues.activos else None
    if not ganador or ganador["sesion"] != sesion or ganador["clave_ciclo"] != clave:
        almacen.anexar({"evento": "liberar", "clave_ciclo": clave, "sesion": sesion,
                        "fecha_hora": ahora.isoformat(), "resultado": "perdido"})
        return {"ok": False, "motivo": "carrera_perdida", "titular": ganador,
                "caducados": despues.caducados}
    return {"ok": True, "motivo": "adquirido", "caducados": despues.caducados}


class AlmacenMemoria:
    """Almacén de eventos en memoria para pruebas y dry-run."""

    def __init__(self, eventos: list[dict] | None = None, fallar_en: int | None = None):
        self.eventos = list(eventos or [])
        self.fallar_en = fallar_en  # número de anexado que falla (inyección de fallos)
        self.anexados = 0

    def leer(self) -> list[dict]:
        return list(self.eventos)

    def anexar(self, evento: dict) -> None:
        self.anexados += 1
        if self.fallar_en is not None and self.anexados == self.fallar_en:
            raise IOError("fallo simulado de escritura en Sheets")
        self.eventos.append(dict(evento))


# ---------------------------------------------------------------- planificación
def normalizar(fila: dict) -> dict:
    return {k: (v if isinstance(v, str) else ("" if v is None else str(v))).strip()
            for k, v in fila.items()}


def clasificar(ot: dict, por_id: dict, permisos: list, eventos: list, ahora: datetime,
               cfg: dict) -> dict:
    """Devuelve {'accion': ..., 'motivo': ...} para una OT."""
    estado = ot.get("estado", "")
    agente = ot.get("asignado_a", "")
    base = {"ot_id": ot.get("ot_id", ""), "estado": estado, "asignado_a": agente}

    if estado == "pendiente_aprobacion":
        return {**base, "accion": "ignorar", "motivo": "pendiente_aprobacion: nunca se ejecuta"}
    if estado in ESTADOS_SIN_ACCION:
        return {**base, "accion": "ignorar", "motivo": f"estado {estado}: sin acción del ciclo"}
    if estado == "en_curso":
        ua = parse_fecha_hoja(ot.get("ultima_actualizacion", ""))
        horas = round((ahora - ua).total_seconds() / 3600, 1) if ua else None
        alerta = horas is None or horas > cfg["umbral_en_curso_h"]
        motivo = "en_curso: se inspecciona, nunca se relanza"
        if horas is not None and horas < -0.25:
            alerta = True
            motivo += "; marca de tiempo futura (posible hora UTC anotada como hora de Panamá)"
        return {**base, "accion": "inspeccionar", "horas_sin_cambio": horas,
                "alerta_estancada": alerta, "motivo": motivo}
    if estado == "entregada":
        urls = [u.strip() for u in ot.get("salida_urls", "").split(";") if u.strip()]
        return {**base, "accion": "evaluar", "handoff_id": ot.get("handoff_id", ""),
                "archivos_a_abrir": urls,
                "motivo": "entregada: evaluación independiente por el Coordinador tras abrir todos los archivos"}
    if estado not in ESTADOS_DESPACHABLES:
        return {**base, "accion": "bloquear", "motivo": f"estado desconocido '{estado}'"}

    # asignada o requiere_correccion
    if agente not in SUBAGENTES:
        return {**base, "accion": "bloquear", "motivo": "sin propietario válido (no es un especialista del catálogo)"}
    if not ot.get("entradas_urls") or not ot.get("criterios_aceptacion"):
        return {**base, "accion": "bloquear", "motivo": "sin entradas o sin criterios de aceptación"}
    if PATRON_PENDIENTE.search(ot.get("entradas_urls", "")):
        return {**base, "accion": "bloquear", "motivo": "entradas pendientes de transferencia"}
    faltan = []
    for dep in dependencias(ot):
        d = por_id.get(dep)
        if not d or d.get("estado") not in ESTADOS_DEP_OK:
            faltan.append(f"{dep} no aprobada")
        elif not d.get("handoff_id") or d["handoff_id"] not in ot.get("entradas_urls", ""):
            faltan.append(f"{dep}: su HANDOFF no figura en entradas_urls (sin transferencia)")
    if faltan:
        return {**base, "accion": "bloquear", "motivo": "dependencias no satisfechas: " + "; ".join(faltan)}
    if requiere_l3(ot) and not permiso_l3_especifico(ot["ot_id"], permisos, ahora):
        return {**base, "accion": "bloquear", "motivo": "requiere L3 sin permiso específico del SUPERVISOR en PERMISOS"}

    clave = clave_despacho(ot)
    previos = [e for e in eventos if e.get("evento") == "despacho" and e.get("ot_id") == ot["ot_id"]]
    if any(e.get("clave_despacho") == clave for e in previos):
        if len(previos) > cfg["max_reintentos_despacho"]:
            return {**base, "accion": "bloquear", "clave_despacho": clave,
                    "motivo": "despacho previo sin efecto y reintentos agotados: avisar al SUPERVISOR"}
        return {**base, "accion": "despachar", "reintento": len(previos),
                "clave_despacho": f"{clave}#r{len(previos)}",
                "subagent_type": SUBAGENTES[agente],
                "esperado": {"estado": estado, "ultima_actualizacion": ot.get("ultima_actualizacion", "")},
                "motivo": "despacho previo sin efecto: reintento limitado"}
    return {**base, "accion": "despachar", "reintento": 0, "clave_despacho": clave,
            "subagent_type": SUBAGENTES[agente],
            "esperado": {"estado": estado, "ultima_actualizacion": ot.get("ultima_actualizacion", "")},
            "motivo": "elegible"}


def planificar(snapshot: dict, cfg: dict | None = None, agent_disponible: bool = False,
               sesion: str = "sesion-local", ahora: datetime | None = None,
               almacen=None) -> dict:
    """Plan completo de un ciclo. No modifica la instantánea de entrada."""
    cfg = {**CONFIG_DEFECTO, **(cfg or {})}
    ahora = a_panama(ahora) if ahora else ahora_panama()
    snap = copy.deepcopy(snapshot)
    cola = [normalizar(f) for f in snap.get("cola_tareas", [])]
    if not cola:
        raise ErrorPlan("COLA_TAREAS vacía o no leída: no se planifica a ciegas")
    ids = [o.get("ot_id") for o in cola]
    duplicados = sorted({i for i in ids if ids.count(i) > 1})
    permisos = [normalizar(p) for p in snap.get("permisos", [])]
    almacen = almacen if almacen is not None else AlmacenMemoria(snap.get("ciclos", []))
    clave = clave_ciclo(ahora)
    modo = interruptor(permisos, ahora)
    simulacion = bool(cfg["dry_run"])
    registros: list[dict] = []   # escrituras que haría el Coordinador
    ids_bit = AsignadorIds(cfg["bloque_bit"], snap.get("bitacora_ids", []))

    def registrar(accion, recurso, detalle, **kw):
        tipo = "bitacora_simulacion" if simulacion else "bitacora"
        registros.append({"tipo": tipo, "fila": fila_bitacora(ids_bit.siguiente(), ahora, accion,
                                                               recurso, detalle, **kw)})

    plan = {"version_planificador": VERSION, "clave_ciclo": clave, "sesion": sesion,
            "ahora": fmt_hoja(ahora), "modo": modo, "dry_run": simulacion,
            "agent_disponible": agent_disponible, "lock": None, "items": [],
            "despachos": [], "registros": registros, "errores": []}

    if modo == "PARADO":
        registrar("lectura", "Lectura 6 h", f"Ciclo {clave}: interruptor de parada activo; no se lee ni se despacha")
        plan["informe"] = informe(plan, cola)
        return plan

    if duplicados:
        plan["errores"].append(f"ot_id duplicados en COLA_TAREAS: {', '.join(duplicados)}")

    lock = {"ok": True, "motivo": "dry_run_sin_lock_real", "caducados": []}
    if not simulacion:
        try:
            lock = adquirir_lock(almacen, clave, sesion, ahora, cfg["lease_min"])
        except IOError as exc:
            plan["errores"].append(f"no se pudo escribir el lock: {exc}")
            lock = {"ok": False, "motivo": "error_lock", "caducados": []}
    plan["lock"] = {k: v for k, v in lock.items() if k != "titular"}
    for t in lock.get("caducados", []):
        plan["errores"].append(f"lease caducado de {t['clave_ciclo']} ({t['sesion']}): revisar sus despachos antes de seguir")
    if not lock["ok"]:
        registrar("lectura", "Lectura 6 h", f"Ciclo {clave}: no se ejecuta ({lock['motivo']})")
        plan["informe"] = informe(plan, cola)
        return plan

    por_id = {o["ot_id"]: o for o in cola}
    eventos = almacen.leer()
    items = [clasificar(o, por_id, permisos, eventos, ahora, cfg) for o in cola]
    for o in items:
        if o["ot_id"] in duplicados and o["accion"] == "despachar":
            o.update(accion="bloquear", motivo="ot_id duplicado: reconciliación por el Coordinador")
    candidatos = sorted((i for i in items if i["accion"] == "despachar"),
                        key=lambda i: (PRIORIDAD.get(por_id[i["ot_id"]].get("prioridad", ""), 9),
                                       por_id[i["ot_id"]].get("fecha_limite", "") or "9999",
                                       i["ot_id"]))
    for n, it in enumerate(candidatos):
        if n >= cfg["max_trabajos_por_ciclo"]:
            it.update(accion="aplazar", motivo="límite de trabajos por ciclo alcanzado")
        elif modo != "ACTIVO":
            it.update(accion="aplazar", motivo="sin autorización de ejecución (interruptor en SOLO_LECTURA)")
        elif not agent_disponible:
            it.update(accion="bloquear", motivo="herramienta Agent no disponible en el hilo principal: no se simulan agentes")
        elif simulacion:
            it["simulado"] = True
            plan["despachos"].append(it)
        else:
            plan["despachos"].append(it)
            registros.append({"tipo": "ciclos", "evento": {
                "evento": "despacho", "clave_ciclo": clave, "sesion": sesion,
                "ot_id": it["ot_id"], "clave_despacho": it["clave_despacho"],
                "fecha_hora": ahora.isoformat()}})
    plan["items"] = items
    if not agent_disponible and any(i["accion"] == "bloquear" and "Agent" in i["motivo"] for i in items):
        registrar("error", "Lectura 6 h", f"Ciclo {clave}: herramienta Agent no disponible; aviso al SUPERVISOR")
    registrar("lectura", "COLA_TAREAS (lectura 6 h)",
              f"Ciclo {clave} modo {modo}{' (dry-run)' if simulacion else ''}: {len(cola)} OT leídas, "
              f"{len(plan['despachos'])} a despachar")
    plan["informe"] = informe(plan, cola)
    return plan


def registrar_despacho_previo(almacen, item: dict, clave: str, sesion: str, ahora: datetime) -> None:
    """Escritura anticipada: el evento 'despacho' se anexa ANTES de llamar a Agent.

    Si la sesión cae después del despacho, el ciclo siguiente ve el evento y no
    repite el despacho (P03 y P08).
    """
    almacen.anexar({"evento": "despacho", "clave_ciclo": clave, "sesion": sesion,
                    "ot_id": item["ot_id"], "clave_despacho": item["clave_despacho"],
                    "fecha_hora": ahora.isoformat()})


def latido(almacen, clave: str, sesion: str, ahora: datetime, lease_min: int) -> None:
    almacen.anexar({"evento": "latido", "clave_ciclo": clave, "sesion": sesion,
                    "fecha_hora": ahora.isoformat(),
                    "lease_hasta": (ahora + timedelta(minutes=lease_min)).isoformat()})


def liberar(almacen, clave: str, sesion: str, ahora: datetime, resultado: str = "completado") -> None:
    almacen.anexar({"evento": "liberar", "clave_ciclo": clave, "sesion": sesion,
                    "fecha_hora": ahora.isoformat(), "resultado": resultado})


# ---------------------------------------------------------------- verificaciones del Coordinador
def verificar_antes_de_despachar(item: dict, ot_releida: dict) -> tuple[bool, str]:
    """Relectura de la fila justo antes del despacho: el estado y la marca de tiempo no cambiaron."""
    ot = normalizar(ot_releida)
    esp = item["esperado"]
    if ot.get("estado") != esp["estado"]:
        return False, f"estado cambió de {esp['estado']} a {ot.get('estado')}"
    if ot.get("ultima_actualizacion") != esp["ultima_actualizacion"]:
        return False, "ultima_actualizacion cambió desde la lectura del ciclo"
    return True, "sin cambios"


def verificar_entrega(ot_releida: dict, handoffs: list[dict]) -> tuple[bool, str]:
    """Comprueba que la entrega la hizo el especialista asignado (no el Coordinador)."""
    ot = normalizar(ot_releida)
    if ot.get("estado") != "entregada" or not ot.get("handoff_id"):
        return False, "la OT no figura entregada con handoff_id"
    filas = [normalizar(h) for h in handoffs if h.get("handoff_id") == ot["handoff_id"]]
    if not filas:
        return False, "HANDOFF sin fila en HANDOFFS"
    h = filas[-1]
    if h.get("ot_id") != ot["ot_id"]:
        return False, "la fila de HANDOFFS es de otra OT"
    if h.get("origen") != ot.get("asignado_a"):
        return False, f"origen {h.get('origen')} distinto del especialista asignado"
    if "Coordinador actuando como" in h.get("observacion", ""):
        return False, "producido por el Coordinador: evaluación no independiente"
    if not h.get("archivo_url"):
        return False, "HANDOFF sin archivo_url"
    return True, "entrega del especialista verificada"


def verificar_evaluacion(item: dict, urls_abiertas: list[str], handoff_url: str = "") -> tuple[bool, list[str]]:
    """El Coordinador solo evalúa si abrió todos los archivos de salida y el HANDOFF."""
    requeridos = list(item.get("archivos_a_abrir", [])) + ([handoff_url] if handoff_url else [])
    faltan = [u for u in requeridos if u not in set(urls_abiertas)]
    if not requeridos:
        faltan = ["la OT entregada no tiene salida_urls"]
    return (not faltan), faltan


def recuperar(ot: dict, handoffs: list[dict], eventos: list[dict], archivos_handoff_drive: list[str]) -> dict:
    """Diagnóstico tras un fallo parcial entre Drive y Sheets (P08). Nunca redespacha."""
    ot = normalizar(ot)
    oid = ot["ot_id"]
    despachada = any(e.get("evento") == "despacho" and e.get("ot_id") == oid for e in eventos)
    fila_ho = [h for h in handoffs if h.get("ot_id") == oid]
    en_drive = [a for a in archivos_handoff_drive if oid in a or (ot.get("handoff_id") and ot["handoff_id"] in a)]
    if fila_ho and ot.get("estado") == "entregada":
        return {"diagnostico": "completo", "accion": "evaluar"}
    if en_drive and not fila_ho:
        return {"diagnostico": "registro_incompleto", "accion": "reconciliar (Coordinador, L2-C): HANDOFF en Drive sin fila en HANDOFFS; no redespachar"}
    if fila_ho and ot.get("estado") != "entregada":
        return {"diagnostico": "estado_sin_actualizar", "accion": "reconciliar: fila en HANDOFFS pero la OT no está entregada; no redespachar"}
    if despachada and ot.get("estado") == "en_curso":
        return {"diagnostico": "en_curso_sin_entrega", "accion": "inspeccionar; no redespachar"}
    if despachada:
        return {"diagnostico": "despacho_sin_efecto", "accion": "reintento limitado o aviso al SUPERVISOR"}
    return {"diagnostico": "sin_despacho", "accion": "seguir las reglas normales del ciclo"}


# ---------------------------------------------------------------- informe
def informe(plan: dict, cola: list[dict]) -> dict:
    por_estado: dict[str, int] = {}
    for o in cola:
        por_estado[o.get("estado", "")] = por_estado.get(o.get("estado", ""), 0) + 1
    items = plan.get("items", [])
    def lista(accion):
        return [{"ot_id": i["ot_id"], "motivo": i["motivo"]} for i in items if i["accion"] == accion]
    return {
        "clave_ciclo": plan["clave_ciclo"], "modo": plan["modo"], "dry_run": plan["dry_run"],
        "lock": (plan.get("lock") or {}).get("motivo"),
        "leidas": len(cola), "por_estado": por_estado,
        "despachadas": [{"ot_id": d["ot_id"], "subagent_type": d["subagent_type"],
                         "simulado": d.get("simulado", False)} for d in plan.get("despachos", [])],
        "aplazadas": lista("aplazar"), "bloqueadas": lista("bloquear"),
        "inspeccionadas": [{"ot_id": i["ot_id"], "horas_sin_cambio": i.get("horas_sin_cambio"),
                            "alerta_estancada": i.get("alerta_estancada")}
                           for i in items if i["accion"] == "inspeccionar"],
        "a_evaluar": [{"ot_id": i["ot_id"], "handoff_id": i.get("handoff_id"),
                       "archivos": len(i.get("archivos_a_abrir", []))}
                      for i in items if i["accion"] == "evaluar"],
        "ignoradas": len(lista("ignorar")),
        "errores": list(plan.get("errores", [])),
    }


def informe_markdown(inf: dict) -> str:
    lineas = [f"# Informe de ciclo {inf['clave_ciclo']}", "",
              f"- Modo: {inf['modo']}{' (dry-run)' if inf['dry_run'] else ''}; lock: {inf['lock']}",
              f"- OT leídas: {inf['leidas']} ({', '.join(f'{k}={v}' for k, v in sorted(inf['por_estado'].items()))})",
              f"- Despachadas{' (SIMULADO, sin llamada a Agent)' if inf['dry_run'] else ''}: "
              f"{', '.join(d['ot_id'] for d in inf['despachadas']) or 'ninguna'}",
              f"- A evaluar: {', '.join(e['ot_id'] for e in inf['a_evaluar']) or 'ninguna'}",
              f"- Inspeccionadas (en_curso): {', '.join(i['ot_id'] for i in inf['inspeccionadas']) or 'ninguna'}",
              f"- Ignoradas: {inf['ignoradas']}", ""]
    if inf["aplazadas"] or inf["bloqueadas"]:
        lineas.append("## Aplazadas y bloqueadas")
        for x in inf["aplazadas"] + inf["bloqueadas"]:
            lineas.append(f"- {x['ot_id']}: {x['motivo']}")
        lineas.append("")
    lineas.append("## Errores")
    lineas += [f"- {e}" for e in inf["errores"]] or ["- ninguno"]
    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------------- CLI
def cargar_config(ruta: str | None) -> dict:
    """Configuración sin secretos, por este orden: --config, LECTURA6H_CONFIG (ruta a un
    archivo fuera del repositorio) o LECTURA6H_CONFIG_JSON (JSON en línea, pensado como
    variable de entorno del entorno de nube). Sin ninguna, valen los valores por defecto."""
    ruta = ruta or os.environ.get("LECTURA6H_CONFIG")
    if ruta:
        with open(ruta, encoding="utf-8") as f:
            cfg = json.load(f)
    elif os.environ.get("LECTURA6H_CONFIG_JSON"):
        cfg = json.loads(os.environ["LECTURA6H_CONFIG_JSON"])
    else:
        return {}
    if not isinstance(cfg, dict):
        raise ErrorPlan("la configuración debe ser un objeto JSON")
    desconocidas = set(cfg) - set(CONFIG_DEFECTO)
    if desconocidas:
        raise ErrorPlan(f"claves de configuración desconocidas: {sorted(desconocidas)}")
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cron", help="expresión cron propuesta")
    c.add_argument("--minuto", type=int, default=CONFIG_DEFECTO["minuto_disparo"])
    p = sub.add_parser("planificar", help="plan de un ciclo a partir de una instantánea")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--config")
    p.add_argument("--agent-disponible", action="store_true")
    p.add_argument("--sesion", default="sesion-local")
    p.add_argument("--ahora")
    p.add_argument("--markdown", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "cron":
        expr = cron_expresion(a.minuto)
        print(expr)
        for d in proximos_disparos(expr, ahora_panama()):
            print(" ", d.isoformat())
        return 0
    try:
        with open(a.snapshot, encoding="utf-8") as f:
            snap = json.load(f)
        plan = planificar(snap, cargar_config(a.config), a.agent_disponible, a.sesion,
                          a_panama(a.ahora) if a.ahora else None)
    except (ErrorPlan, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(informe_markdown(plan["informe"]) if a.markdown else json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
