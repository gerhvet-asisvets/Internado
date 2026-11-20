"""Validador HANDOFF v2.1 local; sin red ni integración con servicios.

Formato: CONTRATO_COMUN v2.2, sección 6 (HANDOFF v2.0 + campo opcional
propuesta_skill). Python 3.13 / PyYAML 6.0.3. Los datos de entrada son no
confiables: el validador nunca imprime valores del paquete, solo nombres de
campo. No sustituye a la v1.0 (handoff_validator.py), que sigue validando
los HANDOFF v1.0 archivados.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml

VERSION = '2.1'
MAX_BYTES = 65536
MAX_NODES = 4000
MAX_DEPTH = 16
MAX_SEQUENCE = 500
MAX_SCALAR = 8192

REQUIRED = ('handoff_version', 'handoff_id', 'ot_id', 'actividad_id', 'origen',
            'destino', 'plataforma', 'tipo', 'resumen', 'datos', 'fuentes',
            'entregables', 'pendientes', 'riesgos', 'calidad',
            'estado_aprobacion', 'fecha_generacion')
OPTIONAL = ('propuesta_skill',)
TEXT_FIELDS = ('handoff_version', 'handoff_id', 'ot_id', 'actividad_id', 'origen',
               'destino', 'plataforma', 'tipo', 'resumen', 'estado_aprobacion',
               'fecha_generacion')

# Catálogos: CONTRATO_COMUN v2.2 (secciones 6 y 8) y pestaña CATALOGOS.
AGENTS = frozenset((
    'AGENTE_00_COORDINADOR', 'AGENTE_01_CHARLAS', 'AGENTE_02_INVESTIGADOR',
    'AGENTE_03_AGENDA', 'AGENTE_04_ASISTENCIAS', 'AGENTE_05_TAREAS',
    'AGENTE_06_NORMATIVA', 'AGENTE_07_PROGRAMADOR', 'AGENTE_08_AUDIOVISUAL'))
COORDINATOR = 'AGENTE_00_COORDINADOR'
PLATFORMS = frozenset(('Claude', 'ChatGPT', 'manual'))
TYPES = frozenset(('consulta', 'actividad', 'tarea', 'entrega', 'documento',
                   'recurso', 'audiovisual'))
# 'borrador' lo pone quien emite; el resto son los estados de HANDOFF (sección 8).
STATES = frozenset(('borrador', 'recibido', 'en_evaluacion', 'aprobado',
                    'transferido', 'archivado', 'requiere_correccion'))
EVIDENCE_STATES = frozenset(('aprobado', 'transferido', 'archivado'))
SOURCE_TYPES = frozenset(('oficial', 'cientifica', 'secundaria'))
# Formatos de la plantilla v2.1. Otros formatos (carpeta, py, md, json...)
# aparecen en HANDOFF reales: se avisan y solo se rechazan en modo estricto.
FORMATS = frozenset(('doc', 'slides', 'sheet', 'pdf', 'png', 'mp4', 'mp3'))
QUALITY_KEYS = ('HECHO_VERIFICADO', 'INTERPRETACION', 'HIPOTESIS', 'DATO_FALTANTE')
SOURCE_KEYS = frozenset(('titulo', 'url', 'fecha_consulta', 'tipo', 'verificada'))
DELIVERABLE_KEYS = frozenset(('titulo', 'url', 'formato', 'version'))
PROPOSAL_KEYS = frozenset(('skill', 'tipo', 'texto', 'motivo', 'evidencia'))
PROPOSAL_TYPES = frozenset(('leccion', 'procedimiento', 'checklist', 'nueva_skill'))

HANDOFF_ID = re.compile(r'HO-[0-9]{4}-[0-9]{3}\Z')
OT_ID = re.compile(r'OT-[0-9]{4}-[0-9]{3}\Z')
ACT_ID = re.compile(r'(?:ACT-[0-9]{4}-[0-9]{3})?\Z')      # vacío permitido
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}\Z')
FORMAT = re.compile(r'[a-z0-9]{1,12}\Z')
DOC_VERSION = re.compile(r'v?[0-9]+(?:\.[0-9]+){0,2}\Z')
SKILL_NAME = re.compile(r'(?:nueva:)?[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HOST = re.compile(r'(?=.{4,253}\Z)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\Z')
FORMULA_START = ('=', '+', '-', '@')

# Claves con semántica inequívoca en cualquier nivel (heredado de v1.0).
DATE_KEYS = frozenset(('fecha', 'fecha_corte', 'fecha_generacion', 'fecha_limite',
                       'vencimiento', 'fecha_emision', 'fecha_consulta'))
STRING_KEYS = frozenset(('asistencia', 'estado', 'titulo', 'tipo', 'nombre',
                         'prioridad', 'actividad_id', 'tarea_id', 'entrega_id',
                         'documento_id', 'producto_id', 'handoff_id', 'ot_id'))
ID_PATTERNS = {
    'actividad_id': ACT_ID,
    'handoff_id': HANDOFF_ID,
    'ot_id': OT_ID,
    'tarea_id': re.compile(r'TAR-[0-9]{4}-[0-9]{3}\Z'),
    'entrega_id': re.compile(r'ENT-[0-9]{4}-[0-9]{3}\Z'),
    'documento_id': re.compile(r'DOC-[0-9]{4}-[0-9]{3}\Z'),
    'producto_id': re.compile(r'PRO-[0-9]{4}-[0-9]{3}\Z'),
}


class ValidationError(Exception):
    pass


class BoundedLoader(yaml.SafeLoader):
    """SafeLoader con límites tempranos, sin aliases y sin claves repetidas."""

    def __init__(self, stream):
        super().__init__(stream)
        self.node_count = 0
        self.depth = 0

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValidationError('aliases YAML no permitidos')
        self.node_count += 1
        if self.node_count > MAX_NODES:
            raise ValidationError('limite de nodos superado')
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise ValidationError('limite de profundidad superado')
        try:
            return super().compose_node(parent, index)
        finally:
            self.depth -= 1

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise ValidationError('se esperaba un mapa YAML')
        result = {}
        for key_node, val_node in node.value:
            if key_node.tag != 'tag:yaml.org,2002:str':
                raise ValidationError('las claves deben ser cadenas explicitas')
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ValidationError('clave no textual')
            if key in result:
                raise ValidationError('clave YAML duplicada')
            result[key] = self.construct_object(val_node, deep=deep)
        return result


def _date(value) -> bool:
    if type(value) is not str or not DATE.fullmatch(value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def full_url(value) -> bool:
    """URL absoluta http(s), con dominio real, sin espacios ni truncamientos."""
    if type(value) is not str or not value or len(value) > 2048:
        return False
    if any(c.isspace() for c in value) or '...' in value or '…' in value:
        return False
    if any(c in value for c in '<>"{}|\\^`'):
        return False
    try:
        parts = urlsplit(value)
        port = parts.port   # valida el puerto si lo hay
    except ValueError:
        return False
    del port
    if parts.scheme not in ('https', 'http') or parts.username or parts.password:
        return False
    host = (parts.hostname or '').lower()
    return bool(HOST.fullmatch(host))


def _walk(value, path='', depth=0, counts=None):
    if counts is None:
        counts = [0]
    counts[0] += 1
    if counts[0] > MAX_NODES or depth > MAX_DEPTH:
        raise ValidationError('estructura demasiado compleja')
    if isinstance(value, dict):
        if len(value) > MAX_SEQUENCE:
            raise ValidationError(f'{path or "raiz"}: mapa demasiado extenso')
        for key, child in value.items():
            if type(key) is not str or len(key) > 256:
                raise ValidationError(f'{path or "raiz"}: clave de mapa invalida')
            here = f'{path}.{key}' if path else key
            if key in STRING_KEYS and type(child) is not str:
                raise ValidationError(f'{here}: debe ser texto')
            if key in ID_PATTERNS and not ID_PATTERNS[key].fullmatch(child):
                raise ValidationError(f'{here}: identificador con formato invalido')
            if key in DATE_KEYS and not _date(child):
                raise ValidationError(f'{here}: fecha invalida o no textual (AAAA-MM-DD entre comillas)')
            _walk(child, here, depth + 1, counts)
    elif isinstance(value, list):
        if len(value) > MAX_SEQUENCE:
            raise ValidationError(f'{path}: lista demasiado extensa')
        for i, child in enumerate(value):
            _walk(child, f'{path}[{i}]', depth + 1, counts)
    elif type(value) is str:
        if len(value) > MAX_SCALAR:
            raise ValidationError(f'{path}: texto demasiado largo')
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValidationError(f'{path}: numero no finito no permitido')
    elif value is None or type(value) in (bool, int):
        pass
    else:
        raise ValidationError(f'{path}: tipo YAML no permitido (fechas sin comillas u objetos)')


def _load(source: str):
    if type(source) is not str or len(source.encode('utf-8')) > MAX_BYTES:
        raise ValidationError('entrada supera el limite de bytes')
    try:
        loader = BoundedLoader(source)
        try:
            value = loader.get_single_data()   # rechaza documentos múltiples
        finally:
            loader.dispose()
    except ValidationError:
        raise
    except yaml.YAMLError:
        raise ValidationError('sintaxis YAML invalida o etiqueta no permitida') from None
    except (ValueError, TypeError, RecursionError):
        raise ValidationError('estructura YAML invalida') from None
    if type(value) is not dict:
        raise ValidationError('el documento raiz debe ser un mapa')
    return value


def _nonempty(value) -> bool:
    return type(value) is str and value.strip() != ''


def _check_sources(items, warnings):
    for i, src in enumerate(items):
        where = f'fuentes[{i}]'
        if type(src) is not dict:
            raise ValidationError(f'{where}: cada fuente debe ser un mapa')
        missing = SOURCE_KEYS - set(src)
        if missing:
            raise ValidationError(f'{where}: faltan {", ".join(sorted(missing))}')
        extra = set(src) - SOURCE_KEYS
        if extra:
            warnings.append(f'{where}: campos no previstos ({", ".join(sorted(extra))})')
        if not _nonempty(src['titulo']):
            raise ValidationError(f'{where}.titulo: vacio')
        if src['tipo'] not in SOURCE_TYPES:
            raise ValidationError(f'{where}.tipo: fuera de catalogo (oficial|cientifica|secundaria)')
        if type(src['verificada']) is not bool:
            raise ValidationError(f'{where}.verificada: debe ser true o false')
        if src['url'] == '':
            if src['verificada']:
                raise ValidationError(f'{where}: fuente verificada sin URL')
            warnings.append(f'{where}: fuente sin URL (DATO_FALTANTE)')
        elif not full_url(src['url']):
            raise ValidationError(f'{where}.url: URL incompleta o invalida')


def _check_deliverables(items, tipo, strict_formats, warnings):
    if not items:
        if tipo == 'consulta':
            warnings.append('entregables vacio (aceptado solo en tipo consulta)')
            return
        raise ValidationError('entregables: se requiere al menos un entregable con URL')
    off_catalog = []
    for i, item in enumerate(items):
        where = f'entregables[{i}]'
        if type(item) is not dict:
            raise ValidationError(f'{where}: cada entregable debe ser un mapa')
        missing = DELIVERABLE_KEYS - set(item)
        if missing:
            raise ValidationError(f'{where}: faltan {", ".join(sorted(missing))}')
        extra = set(item) - DELIVERABLE_KEYS
        if extra:
            warnings.append(f'{where}: campos no previstos ({", ".join(sorted(extra))})')
        if not _nonempty(item['titulo']):
            raise ValidationError(f'{where}.titulo: vacio')
        if not full_url(item['url']):
            raise ValidationError(f'{where}.url: URL obligatoria, completa (http/https)')
        fmt = item['formato']
        if type(fmt) is not str or not FORMAT.fullmatch(fmt):
            raise ValidationError(f'{where}.formato: invalido')
        if fmt not in FORMATS:
            if strict_formats:
                raise ValidationError(f'{where}.formato: fuera del catalogo de la plantilla')
            off_catalog.append(str(i))
        if type(item['version']) is not str or not DOC_VERSION.fullmatch(item['version']):
            raise ValidationError(f'{where}.version: debe ser texto tipo \'1.0\'')
    if off_catalog:
        warnings.append('formato fuera del catalogo de la plantilla en entregables '
                        + ', '.join(off_catalog))


def _check_quality(value):
    if type(value) is not dict:
        raise ValidationError('calidad debe ser un mapa')
    if set(value) != set(QUALITY_KEYS):
        raise ValidationError('calidad: debe tener exactamente ' + ', '.join(QUALITY_KEYS))
    for key in QUALITY_KEYS:
        if type(value[key]) is not list:
            raise ValidationError(f'calidad.{key}: debe ser una lista')


def _check_proposals(value, warnings):
    if type(value) is not list:
        raise ValidationError('propuesta_skill debe ser una lista')
    for i, prop in enumerate(value):
        where = f'propuesta_skill[{i}]'
        if type(prop) is not dict:
            raise ValidationError(f'{where}: debe ser un mapa')
        if set(prop) != PROPOSAL_KEYS:
            raise ValidationError(f'{where}: debe tener exactamente skill, tipo, texto, motivo, evidencia')
        for key in PROPOSAL_KEYS:
            if type(prop[key]) is not str:
                raise ValidationError(f'{where}.{key}: debe ser texto')
        if not SKILL_NAME.fullmatch(prop['skill']):
            raise ValidationError(f'{where}.skill: nombre invalido (skill o nueva:<nombre>)')
        if prop['tipo'] not in PROPOSAL_TYPES:
            raise ValidationError(f'{where}.tipo: fuera de catalogo')
        if (prop['tipo'] == 'nueva_skill') != prop['skill'].startswith('nueva:'):
            warnings.append(f'{where}: tipo nueva_skill y prefijo nueva: no coinciden')
        if not _nonempty(prop['texto']):
            raise ValidationError(f'{where}.texto: vacio')
        for key in ('motivo', 'evidencia'):
            if not _nonempty(prop[key]):
                warnings.append(f'{where}.{key} vacio')


def parse_validate(source: str, *, strict_formats: bool = False):
    """Devuelve (datos, advertencias) o lanza ValidationError."""
    value = _load(source)
    keys = set(value)
    missing = [k for k in REQUIRED if k not in keys]
    if missing:
        raise ValidationError('campos obligatorios faltantes: ' + ', '.join(missing))
    extra = sorted(keys - set(REQUIRED) - set(OPTIONAL))
    if extra:
        raise ValidationError('campos superiores no previstos: ' + ', '.join(extra))
    for name in TEXT_FIELDS:
        if type(value[name]) is not str:
            raise ValidationError(f'{name}: debe ser texto (entre comillas)')
    if value['handoff_version'] != VERSION:
        raise ValidationError("handoff_version debe ser '2.1' (para '1.0' usar handoff_validator.py)")
    if not HANDOFF_ID.fullmatch(value['handoff_id']):
        raise ValidationError('handoff_id: formato HO-AAAA-NNN')
    if not OT_ID.fullmatch(value['ot_id']):
        raise ValidationError('ot_id: formato OT-AAAA-NNN')
    if not ACT_ID.fullmatch(value['actividad_id']):
        raise ValidationError('actividad_id: formato ACT-AAAA-NNN o vacio')
    if value['origen'] not in AGENTS:
        raise ValidationError('origen fuera del catalogo de 9 agentes')
    if value['destino'] != COORDINATOR:
        raise ValidationError('destino debe ser AGENTE_00_COORDINADOR')
    if value['plataforma'] not in PLATFORMS:
        raise ValidationError('plataforma fuera de catalogo (Claude|ChatGPT|manual)')
    if value['tipo'] not in TYPES:
        raise ValidationError('tipo fuera de catalogo')
    if value['estado_aprobacion'] not in STATES:
        raise ValidationError('estado_aprobacion fuera de catalogo')
    if not _nonempty(value['resumen']):
        raise ValidationError('resumen vacio')
    if not _date(value['fecha_generacion']):
        raise ValidationError('fecha_generacion debe ser cadena ISO de fecha real')
    if type(value['datos']) is not dict:
        raise ValidationError('datos debe ser un mapa')
    for name in ('fuentes', 'entregables', 'pendientes', 'riesgos'):
        if type(value[name]) is not list:
            raise ValidationError(f'{name} debe ser una lista')
    _walk(value)

    warnings = []
    _check_sources(value['fuentes'], warnings)
    _check_deliverables(value['entregables'], value['tipo'], strict_formats, warnings)
    _check_quality(value['calidad'])
    if 'propuesta_skill' in value:
        _check_proposals(value['propuesta_skill'], warnings)

    if value['origen'] == COORDINATOR:
        warnings.append('origen y destino son el Coordinador: revisar independencia')
    if value['estado_aprobacion'] != 'borrador':
        warnings.append('quien emite deja estado_aprobacion en borrador; el estado lo lleva HANDOFFS')
    if value['estado_aprobacion'] in EVIDENCE_STATES:
        warnings.append('estado requiere verificacion de evidencia externa')
    years = {value['handoff_id'][3:7], value['ot_id'][3:7], value['fecha_generacion'][:4]}
    if value['actividad_id']:
        years.add(value['actividad_id'][4:8])
    if len(years) > 1:
        warnings.append('los anios de handoff_id, ot_id, actividad_id y fecha_generacion no coinciden')
    if value['resumen'].lstrip().startswith(FORMULA_START):
        warnings.append('resumen empieza como formula de hoja de calculo: escapar al copiarlo a Sheets')
    return value, warnings


def fingerprint(data: dict) -> str:
    # sha256 de los datos normalizados; no se persiste ni se imprime el contenido.
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class Session:
    """Detección de repetidos en memoria: sin persistencia ni conexión remota."""

    def __init__(self, *, strict_formats: bool = False):
        self.strict_formats = strict_formats
        self.seen = set()
        self.by_id = {}

    def validate(self, source: str) -> dict:
        data, warnings = parse_validate(source, strict_formats=self.strict_formats)
        digest = fingerprint(data)
        duplicate = digest in self.seen
        hid = data['handoff_id']
        if hid in self.by_id and digest not in self.by_id[hid]:
            warnings.append('mismo handoff_id con contenido diferente')
        self.by_id.setdefault(hid, set()).add(digest)
        if duplicate:
            warnings.append('paquete identico repetido')
        self.seen.add(digest)
        return {'valido': True, 'handoff_version': VERSION, 'handoff_id': hid,
                'duplicado': duplicate, 'advertencias': warnings,
                'huella_sha256': digest}


def _read(path_arg):
    if path_arg == '-':
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    else:
        path = Path(path_arg)
        if path.stat().st_size > MAX_BYTES:
            raise ValidationError('entrada supera el limite de bytes')
        raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValidationError('entrada supera el limite de bytes')
    return raw.decode('utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validar HANDOFF v2.1 local sin red')
    parser.add_argument('archivos', nargs='*', default=['-'],
                        help="YAML locales; '-' o nada: entrada estandar")
    parser.add_argument('--estricto-formato', action='store_true',
                        help='rechazar formatos de entregable fuera de la plantilla')
    args = parser.parse_args(argv)
    session = Session(strict_formats=args.estricto_formato)
    results, code = [], 0
    for name in args.archivos:
        try:
            result = session.validate(_read(name))
        except (ValidationError, UnicodeError, OSError) as exc:
            reason = str(exc) if isinstance(exc, ValidationError) else 'error de lectura o codificacion'
            result = {'valido': False, 'error': reason}
            code = 1
        result = {'archivo': name, **result}
        results.append(result)
    # No imprime el contenido del paquete, solo nombres de campo y la huella.
    out = results[0] if len(results) == 1 else results
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
