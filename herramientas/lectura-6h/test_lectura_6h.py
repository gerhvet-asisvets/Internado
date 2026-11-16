#!/usr/bin/env python3
"""Pruebas del planificador lectura-6h (OT-2026-016). Datos 100 % ficticios.

Cada prueba lleva el código P01-P12 de la solicitud técnica (sección 6) o S0x
para las de seguridad. Lo que no se puede comprobar sin desplegar queda como
prueba omitida (skip) con el motivo, para que figure en el resultado.

    python3 -m unittest -v test_lectura_6h
"""
import copy
import json
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import lectura_6h as L

AQUI = Path(__file__).resolve().parent
SNAP = json.loads((AQUI / "datos_ficticios" / "instantanea_ficticia.json").read_text(encoding="utf-8"))
AHORA = datetime(2099, 3, 10, 0, 7, tzinfo=L.TZ)
REAL = {"dry_run": False}
NO_DESPLEGABLE = "no comprobable sin despliegue"


def snap():
    return copy.deepcopy(SNAP)


def items(plan):
    return {i["ot_id"]: i for i in plan["items"]}


class P01Simulacion(unittest.TestCase):
    def test_p01_enumera_todas_las_ot_y_solo_escribe_simulacion(self):
        entrada = snap()
        original = copy.deepcopy(entrada)
        plan = L.planificar(entrada, {"dry_run": True}, agent_disponible=True, ahora=AHORA)
        self.assertEqual(entrada, original, "la instantánea no debe modificarse")
        self.assertEqual(len(plan["items"]), len(SNAP["cola_tareas"]))
        self.assertEqual({i["ot_id"] for i in plan["items"]}, {o["ot_id"] for o in SNAP["cola_tareas"]})
        self.assertTrue(plan["registros"])
        self.assertTrue(all(r["tipo"] == "bitacora_simulacion" for r in plan["registros"]))
        self.assertTrue(all(d.get("simulado") for d in plan["despachos"]))
        self.assertEqual(plan["informe"]["leidas"], 12)

    def test_p01_clasificacion_esperada(self):
        it = items(L.planificar(snap(), REAL, True, ahora=AHORA))
        esperado = {
            "OT-2099-001": "despachar", "OT-2099-002": "bloquear", "OT-2099-003": "inspeccionar",
            "OT-2099-004": "ignorar", "OT-2099-005": "evaluar", "OT-2099-006": "despachar",
            "OT-2099-007": "ignorar", "OT-2099-008": "bloquear", "OT-2099-009": "bloquear",
            "OT-2099-010": "bloquear", "OT-2099-011": "aplazar", "OT-2099-012": "bloquear",
        }
        self.assertEqual({k: v["accion"] for k, v in it.items()}, esperado)


class P02Programacion(unittest.TestCase):
    def test_p02_cron_00_06_12_18_hora_panama(self):
        expr = L.cron_expresion(7)
        self.assertEqual(expr, "CRON_TZ=America/Panama 7 0,6,12,18 * * *")
        disparos = L.proximos_disparos(expr, datetime(2099, 3, 9, 23, 0, tzinfo=L.TZ), 8)
        self.assertEqual([d.hour for d in disparos], [0, 6, 12, 18, 0, 6, 12, 18])
        self.assertTrue(all(d.minute == 7 for d in disparos))
        utc = [d.astimezone(L.ZoneInfo("UTC")).hour for d in disparos[:4]]
        self.assertEqual(utc, [5, 11, 17, 23], "Panamá es UTC-5 todo el año (sin horario de verano)")

    def test_p02_sin_horario_de_verano(self):
        for mes in range(1, 13):
            self.assertEqual(datetime(2027, mes, 15, 12, tzinfo=L.TZ).utcoffset(), timedelta(hours=-5))

    def test_p02_disparo_tardio_cae_en_su_franja(self):
        self.assertEqual(L.clave_ciclo(datetime(2099, 3, 10, 0, 7, tzinfo=L.TZ)), "CIC-20990310-00")
        self.assertEqual(L.clave_ciclo(datetime(2099, 3, 10, 5, 59, tzinfo=L.TZ)), "CIC-20990310-00")
        self.assertEqual(L.clave_ciclo(datetime(2099, 3, 10, 6, 0, tzinfo=L.TZ)), "CIC-20990310-06")
        utc = datetime(2099, 3, 10, 23, 30, tzinfo=L.ZoneInfo("UTC"))  # 18:30 en Panamá
        self.assertEqual(L.clave_ciclo(utc), "CIC-20990310-18")

    @unittest.skip(NO_DESPLEGABLE + ": la persistencia sin sesión interactiva depende del disparador en la nube; "
                   "se documenta con la documentación pública y se verifica con la primera ejecución registrada")
    def test_p02_persistencia_sin_sesion(self):
        pass


class P03Duplicados(unittest.TestCase):
    def test_p03_mismo_ciclo_dos_veces_no_despacha_dos_veces(self):
        alm = L.AlmacenMemoria()
        plan1 = L.planificar(snap(), REAL, True, "sesion-A", AHORA, alm)
        self.assertTrue(plan1["lock"]["ok"])
        for d in plan1["despachos"]:
            L.registrar_despacho_previo(alm, d, plan1["clave_ciclo"], "sesion-A", AHORA)
        L.liberar(alm, plan1["clave_ciclo"], "sesion-A", AHORA)
        plan2 = L.planificar(snap(), REAL, True, "sesion-A", AHORA + timedelta(minutes=30), alm)
        self.assertFalse(plan2["lock"]["ok"])
        self.assertEqual(plan2["lock"]["motivo"], "ciclo_ya_completado")
        self.assertEqual(plan2["despachos"], [])

    def test_p03_dos_hosts_a_la_vez_solo_gana_uno(self):
        alm = L.AlmacenMemoria()
        a = L.adquirir_lock(alm, "CIC-20990310-00", "host-A", AHORA, 120)
        b = L.adquirir_lock(alm, "CIC-20990310-00", "host-B", AHORA, 120)
        self.assertTrue(a["ok"])
        self.assertFalse(b["ok"])
        self.assertEqual(b["motivo"], "lock_ocupado")

    def test_p03_carrera_con_lectura_simultanea(self):
        """Los dos leen antes de que ninguno anexe: gana la primera fila; el otro se retira."""
        alm = L.AlmacenMemoria()

        class LecturaVieja:
            def __init__(self):
                self.primera = True

            def leer(self):
                if self.primera:
                    self.primera = False
                    return []
                return alm.leer()

            def anexar(self, e):
                alm.anexar(e)

        L.adquirir_lock(alm, "CIC-20990310-00", "host-A", AHORA, 120)
        b = L.adquirir_lock(LecturaVieja(), "CIC-20990310-00", "host-B", AHORA, 120)
        self.assertFalse(b["ok"])
        self.assertEqual(b["motivo"], "carrera_perdida")
        estado = L.estado_lock(alm.leer(), AHORA)
        self.assertEqual([t["sesion"] for t in estado.activos], ["host-A"])

    def test_p03_despacho_registrado_no_se_repite_en_otro_ciclo(self):
        alm = L.AlmacenMemoria()
        p1 = L.planificar(snap(), REAL, True, "s1", AHORA, alm)
        for d in p1["despachos"]:
            L.registrar_despacho_previo(alm, d, p1["clave_ciclo"], "s1", AHORA)
        L.liberar(alm, p1["clave_ciclo"], "s1", AHORA)
        # El especialista no llegó a cambiar la OT: siguiente franja, mismo estado.
        p2 = L.planificar(snap(), {**REAL, "max_reintentos_despacho": 0}, True, "s2",
                          AHORA + timedelta(hours=6), alm)
        it = items(p2)
        self.assertEqual(it["OT-2099-001"]["accion"], "bloquear")
        self.assertIn("reintentos agotados", it["OT-2099-001"]["motivo"])

    def test_p03_verificacion_previa_al_despacho(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA)
        item = plan["despachos"][0]
        fila = next(o for o in SNAP["cola_tareas"] if o["ot_id"] == item["ot_id"])
        self.assertTrue(L.verificar_antes_de_despachar(item, fila)[0])
        cambiada = {**fila, "estado": "en_curso"}
        self.assertFalse(L.verificar_antes_de_despachar(item, cambiada)[0])
        tocada = {**fila, "ultima_actualizacion": "2099-03-10 00:05"}
        self.assertFalse(L.verificar_antes_de_despachar(item, tocada)[0])


class P04Intactas(unittest.TestCase):
    def test_p04_pendiente_aprobacion_y_dependencias(self):
        it = items(L.planificar(snap(), REAL, True, ahora=AHORA))
        self.assertEqual(it["OT-2099-004"]["accion"], "ignorar")
        self.assertIn("nunca se ejecuta", it["OT-2099-004"]["motivo"])
        self.assertEqual(it["OT-2099-002"]["accion"], "bloquear")
        self.assertIn("OT-2099-003 no aprobada", it["OT-2099-002"]["motivo"])
        self.assertIn("pendientes de transferencia", it["OT-2099-008"]["motivo"])

    def test_p04_dependencia_aprobada_sin_transferencia(self):
        s = snap()
        ot6 = next(o for o in s["cola_tareas"] if o["ot_id"] == "OT-2099-006")
        ot6["entradas_urls"] = "https://ejemplo.invalid/doc/E6"   # sin el HO de OT-2099-007
        it = items(L.planificar(s, REAL, True, ahora=AHORA))
        self.assertEqual(it["OT-2099-006"]["accion"], "bloquear")
        self.assertIn("sin transferencia", it["OT-2099-006"]["motivo"])

    def test_p04_ningun_registro_cambia_estados(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA)
        for r in plan["registros"]:
            if r["tipo"].startswith("bitacora"):
                self.assertNotIn("COLA_TAREAS!K", r["fila"][7])


class P05Despacho(unittest.TestCase):
    def test_p05_sin_agent_no_se_despacha_ni_se_simula(self):
        plan = L.planificar(snap(), REAL, agent_disponible=False, ahora=AHORA)
        self.assertEqual(plan["despachos"], [])
        it = items(plan)
        self.assertIn("Agent no disponible", it["OT-2099-001"]["motivo"])
        self.assertTrue(any(r["fila"][6] == "error" for r in plan["registros"]))

    def test_p05_con_agent_usa_el_subagente_del_especialista(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA)
        tipos = {d["ot_id"]: d["subagent_type"] for d in plan["despachos"]}
        self.assertEqual(tipos, {"OT-2099-001": "agente-06-normativa",
                                 "OT-2099-006": "agente-02-investigador"})

    def test_p05_entrega_atribuida_al_especialista(self):
        fila = {**next(o for o in SNAP["cola_tareas"] if o["ot_id"] == "OT-2099-005")}
        self.assertTrue(L.verificar_entrega(fila, SNAP["handoffs"])[0])
        malo = [{**SNAP["handoffs"][0], "origen": "AGENTE_00_COORDINADOR"}]
        self.assertFalse(L.verificar_entrega(fila, malo)[0])
        autoeval = [{**SNAP["handoffs"][0], "observacion": "Ejecutado por la sesión del Coordinador actuando como AGENTE_01"}]
        self.assertFalse(L.verificar_entrega(fila, autoeval)[0])

    @unittest.skip(NO_DESPLEGABLE + ": la llamada real a Agent la hace el hilo principal de Claude Code, no el script")
    def test_p05_llamada_real_agent(self):
        pass


class P06EnCurso(unittest.TestCase):
    def test_p06_en_curso_no_se_relanza(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA)
        self.assertNotIn("OT-2099-003", [d["ot_id"] for d in plan["despachos"]])
        ins = items(plan)["OT-2099-003"]
        self.assertEqual(ins["accion"], "inspeccionar")
        self.assertEqual(ins["horas_sin_cambio"], 4.1)
        self.assertFalse(ins["alerta_estancada"])

    def test_p06_marca_de_tiempo_futura(self):
        s = snap()
        next(o for o in s["cola_tareas"] if o["ot_id"] == "OT-2099-003")["ultima_actualizacion"] = "2099-03-10 05:07"
        ins = items(L.planificar(s, REAL, True, ahora=AHORA))["OT-2099-003"]
        self.assertTrue(ins["alerta_estancada"])
        self.assertIn("marca de tiempo futura", ins["motivo"])
        self.assertEqual(ins["accion"], "inspeccionar")

    def test_p06_en_curso_estancada_alerta(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA + timedelta(days=2))
        self.assertTrue(items(plan)["OT-2099-003"]["alerta_estancada"])


class P07Evaluacion(unittest.TestCase):
    def test_p07_evaluar_solo_con_todos_los_archivos_abiertos(self):
        it = items(L.planificar(snap(), REAL, True, ahora=AHORA))["OT-2099-005"]
        self.assertEqual(len(it["archivos_a_abrir"]), 2)
        ho = "https://ejemplo.invalid/ho/H5"
        ok, faltan = L.verificar_evaluacion(it, ["https://ejemplo.invalid/doc/S5a"], ho)
        self.assertFalse(ok)
        self.assertEqual(set(faltan), {"https://ejemplo.invalid/doc/S5b", ho})
        ok, _ = L.verificar_evaluacion(it, it["archivos_a_abrir"] + [ho], ho)
        self.assertTrue(ok)

    def test_p07_entregada_sin_salidas_no_es_evaluable(self):
        ok, faltan = L.verificar_evaluacion({"archivos_a_abrir": []}, [])
        self.assertFalse(ok)
        self.assertTrue(faltan)


class P08Recuperacion(unittest.TestCase):
    def test_p08_handoff_en_drive_sin_fila_en_sheets(self):
        ot = {**next(o for o in SNAP["cola_tareas"] if o["ot_id"] == "OT-2099-001"), "estado": "en_curso"}
        eventos = [{"evento": "despacho", "ot_id": "OT-2099-001"}]
        r = L.recuperar(ot, [], eventos, ["HO-2099-020_ACT-2099-001_AGENTE_06.yaml OT-2099-001"])
        self.assertEqual(r["diagnostico"], "registro_incompleto")
        self.assertIn("no redespachar", r["accion"])

    def test_p08_fila_handoff_sin_estado_entregada(self):
        ot = {**next(o for o in SNAP["cola_tareas"] if o["ot_id"] == "OT-2099-001"), "estado": "en_curso"}
        r = L.recuperar(ot, [{"handoff_id": "HO-2099-020", "ot_id": "OT-2099-001"}], [], [])
        self.assertEqual(r["diagnostico"], "estado_sin_actualizar")

    def test_p08_fallo_al_escribir_el_lock(self):
        alm = L.AlmacenMemoria(fallar_en=1)
        plan = L.planificar(snap(), REAL, True, "s1", AHORA, alm)
        self.assertFalse(plan["lock"]["ok"])
        self.assertEqual(plan["despachos"], [])
        self.assertTrue(any("no se pudo escribir el lock" in e for e in plan["errores"]))

    def test_p08_caida_con_lock_tomado_y_lease_caducado(self):
        alm = L.AlmacenMemoria()
        p1 = L.planificar(snap(), REAL, True, "s1", AHORA, alm)
        L.registrar_despacho_previo(alm, p1["despachos"][0], p1["clave_ciclo"], "s1", AHORA)
        # s1 cae sin liberar. Durante el lease, nadie entra.
        p_mismo = L.planificar(snap(), REAL, True, "s2", AHORA + timedelta(minutes=60), alm)
        self.assertEqual(p_mismo["lock"]["motivo"], "lock_ocupado")
        # Tras caducar el lease, el ciclo siguiente entra, avisa y no repite el despacho previo.
        p2 = L.planificar(snap(), {**REAL, "max_reintentos_despacho": 0}, True, "s3",
                          AHORA + timedelta(hours=6), alm)
        self.assertTrue(p2["lock"]["ok"])
        self.assertTrue(any("lease caducado" in e for e in p2["errores"]))
        self.assertNotIn(p1["despachos"][0]["ot_id"], [d["ot_id"] for d in p2["despachos"]])


class P09L3(unittest.TestCase):
    def test_p09_ot_con_accion_l3_bloqueada_sin_permiso(self):
        it = items(L.planificar(snap(), REAL, True, ahora=AHORA))["OT-2099-009"]
        self.assertEqual(it["accion"], "bloquear")
        self.assertIn("L3", it["motivo"])

    def test_p09_permiso_l3_especifico_lo_habilita(self):
        s = snap()
        s["permisos"].append({"permiso_id": "PER-2099-009", "agente": "AGENTE_07_PROGRAMADOR",
                              "recurso": "Programador", "nivel": "L3_accion_aprobada_por_supervisor",
                              "alcance": "OT-2099-009 instalación", "otorgado_por": "SUPERVISOR",
                              "fecha": "2099-03-09", "vigencia": "2099-03-31", "estado": "vigente"})
        s["cola_tareas"] = [o for o in s["cola_tareas"] if o["ot_id"] in ("OT-2099-009",)]
        it = items(L.planificar(s, REAL, True, ahora=AHORA))["OT-2099-009"]
        self.assertEqual(it["accion"], "despachar")

    def test_p09_permiso_generico_o_de_otro_no_basta(self):
        s = snap()
        s["permisos"].append({"recurso": "Acciones L3", "nivel": "L3_accion_aprobada_por_supervisor",
                              "alcance": "caso por caso", "otorgado_por": "SUPERVISOR",
                              "vigencia": "por acción", "estado": "vigente"})
        s["permisos"].append({"recurso": "x", "nivel": "L3_accion", "alcance": "OT-2099-009",
                              "otorgado_por": "AGENTE_00_COORDINADOR", "vigencia": "indefinida",
                              "estado": "vigente"})
        it = items(L.planificar(s, REAL, True, ahora=AHORA))["OT-2099-009"]
        self.assertEqual(it["accion"], "bloquear")

    def test_p09_sin_autorizacion_del_supervisor_solo_lectura(self):
        s = snap()
        s["permisos"] = [p for p in s["permisos"] if p["recurso"] != "LECTURA_6H"]
        plan = L.planificar(s, REAL, True, ahora=AHORA)
        self.assertEqual(plan["modo"], "SOLO_LECTURA")
        self.assertEqual(plan["despachos"], [])

    def test_p09_autorizacion_caducada(self):
        plan = L.planificar(snap(), REAL, True, ahora=datetime(2099, 4, 2, 6, 7, tzinfo=L.TZ))
        self.assertEqual(plan["modo"], "SOLO_LECTURA")


class P10Bitacora(unittest.TestCase):
    def test_p10_filas_completas_ids_unicos_y_hora_panama(self):
        plan = L.planificar(snap(), REAL, False, ahora=AHORA.astimezone(L.ZoneInfo("UTC")))
        filas = [r["fila"] for r in plan["registros"] if r["tipo"].startswith("bitacora")]
        self.assertTrue(filas)
        ids = [f[0] for f in filas]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(ids).isdisjoint(SNAP["bitacora_ids"]))
        for f in filas:
            self.assertEqual(len(f), 13)
            self.assertRegex(f[0], r"^BIT-2026-09\d\d$")
            self.assertEqual(f[1], "2099-03-10 00:07", "hora de Panamá aunque el reloj llegue en UTC")
            self.assertIn(f[6], {"lectura", "error", "modificacion", "inicio_sesion", "cierre_sesion"})

    def test_p10_bloque_agotado(self):
        a = L.AsignadorIds(["BIT-2026-0900", "BIT-2026-0901"], ["BIT-2026-0900"])
        self.assertEqual(a.siguiente(), "BIT-2026-0901")
        with self.assertRaises(L.ErrorPlan):
            a.siguiente()

    def test_p10_fila_de_modificacion_con_antes_y_despues(self):
        f = L.fila_bitacora("BIT-2026-0910", AHORA, "modificacion", "COLA_TAREAS!K2", "cambio",
                            ot_id="OT-2099-001", valor_anterior="asignada", valor_nuevo="en_curso")
        self.assertEqual((f[10], f[11]), ("asignada", "en_curso"))


class P11Informe(unittest.TestCase):
    def test_p11_informe_de_ciclo(self):
        plan = L.planificar(snap(), REAL, True, ahora=AHORA)
        inf = plan["informe"]
        for clave in ("leidas", "por_estado", "despachadas", "bloqueadas", "aplazadas",
                      "inspeccionadas", "a_evaluar", "errores", "clave_ciclo", "modo"):
            self.assertIn(clave, inf)
        self.assertEqual(inf["leidas"], 12)
        self.assertEqual(len(inf["despachadas"]), 2)
        self.assertEqual(inf["a_evaluar"][0]["handoff_id"], "HO-2099-005")
        md = L.informe_markdown(inf)
        self.assertIn("# Informe de ciclo CIC-20990310-00", md)
        self.assertIn("OT-2099-011: límite de trabajos por ciclo alcanzado", md)

    def test_p11_limite_de_trabajos(self):
        plan = L.planificar(snap(), {**REAL, "max_trabajos_por_ciclo": 1}, True, ahora=AHORA)
        self.assertEqual([d["ot_id"] for d in plan["despachos"]], ["OT-2099-001"])


class P12Apagado(unittest.TestCase):
    def test_p12_interruptor_de_parada(self):
        s = snap()
        s["permisos"].append({**s["permisos"][1], "estado": "parado"})
        plan = L.planificar(s, REAL, True, ahora=AHORA)
        self.assertEqual(plan["modo"], "PARADO")
        self.assertEqual(plan["items"], [])
        self.assertEqual(plan["despachos"], [])
        self.assertEqual(len(plan["registros"]), 1)

    def test_p12_reactivacion_tras_parada(self):
        s = snap()
        s["permisos"].append({**s["permisos"][1], "estado": "parado"})
        s["permisos"].append({**s["permisos"][1], "estado": "vigente"})
        self.assertEqual(L.planificar(s, REAL, True, ahora=AHORA)["modo"], "ACTIVO")

    def test_p12_parada_por_supervisor_no_requiere_codigo(self):
        """Revocar (cualquier estado distinto de vigente) deja el ciclo en solo lectura."""
        s = snap()
        s["permisos"].append({**s["permisos"][1], "estado": "revocado"})
        self.assertEqual(L.planificar(s, REAL, True, ahora=AHORA)["modo"], "SOLO_LECTURA")

    @unittest.skip(NO_DESPLEGABLE + ": pausar o eliminar el disparador real (update_trigger enabled=false) "
                   "y revertir el commit son operaciones L3 sobre la infraestructura")
    def test_p12_apagado_real_del_disparador(self):
        pass


class S01Seguridad(unittest.TestCase):
    def test_s01_sin_ids_ni_enlaces_de_drive_en_el_codigo(self):
        # Enlaces de Google, enlaces a commits, o cadenas con aspecto de ID de Drive:
        # 25 o más caracteres con al menos 3 dígitos, 3 mayúsculas y 3 minúsculas.
        # Los nombres de funciones, variables y valores de catálogo no cumplen eso.
        enlace = re.compile(r"docs\.google\.com|drive\.google\.com|github\.com/\S+/commit")

        def parece_id(tok):
            return (sum(c.isdigit() for c in tok) >= 3 and sum(c.isupper() for c in tok) >= 3
                    and sum(c.islower() for c in tok) >= 3)

        for nombre in ("lectura_6h.py", "test_lectura_6h.py", "README.md", "config.ejemplo.json",
                       "datos_ficticios/instantanea_ficticia.json"):
            ruta = AQUI / nombre
            if ruta.exists():
                texto = ruta.read_text(encoding="utf-8")
                self.assertIsNone(enlace.search(texto), f"enlace en {nombre}")
                ids = [t for t in re.findall(r"[A-Za-z0-9_-]{25,}", texto) if parece_id(t)]
                self.assertEqual(ids, [], f"posible ID en {nombre}")

    def test_s01b_el_detector_reconoce_un_id_de_drive(self):
        # Inventado y troceado para que el propio archivo no contenga la cadena completa.
        tok = "1AbCdEfGh2IjK" + "lMnOp3QrStUvWx4Yz"
        self.assertGreaterEqual(len(tok), 25)
        self.assertTrue(sum(c.isdigit() for c in tok) >= 3 and sum(c.isupper() for c in tok) >= 3
                        and sum(c.islower() for c in tok) >= 3)

    def test_s02_texto_seguro_contra_formulas(self):
        self.assertEqual(L.texto_seguro("=IMPORTXML(x)"), "'=IMPORTXML(x)")
        self.assertEqual(L.texto_seguro("+1"), "'+1")
        self.assertEqual(L.texto_seguro("normal"), "normal")

    def test_s03_cola_vacia_no_se_planifica(self):
        with self.assertRaises(L.ErrorPlan):
            L.planificar({"cola_tareas": []}, REAL, True, ahora=AHORA)

    def test_s04_ot_duplicada_no_se_despacha(self):
        s = snap()
        s["cola_tareas"].append(copy.deepcopy(s["cola_tareas"][0]))
        plan = L.planificar(s, REAL, True, ahora=AHORA)
        self.assertNotIn("OT-2099-001", [d["ot_id"] for d in plan["despachos"]])
        self.assertTrue(any("duplicados" in e for e in plan["errores"]))

    def test_s05_config_con_claves_desconocidas(self):
        ruta = AQUI / "datos_ficticios" / "_cfg_tmp.json"
        ruta.write_text(json.dumps({"token": "x"}), encoding="utf-8")
        try:
            with self.assertRaises(L.ErrorPlan):
                L.cargar_config(str(ruta))
        finally:
            ruta.unlink()


    def test_s06_config_desde_variable_de_entorno(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"LECTURA6H_CONFIG_JSON": '{"dry_run": false, "max_trabajos_por_ciclo": 1}'}, clear=False):
            os.environ.pop("LECTURA6H_CONFIG", None)
            self.assertEqual(L.cargar_config(None), {"dry_run": False, "max_trabajos_por_ciclo": 1})
        with mock.patch.dict(os.environ, {"LECTURA6H_CONFIG_JSON": '{"clave": "x"}'}, clear=False):
            os.environ.pop("LECTURA6H_CONFIG", None)
            with self.assertRaises(L.ErrorPlan):
                L.cargar_config(None)

if __name__ == "__main__":
    unittest.main(verbosity=2)
