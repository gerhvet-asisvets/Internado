"""Validador HANDOFF v1.0 local; no red ni integración con servicios.

Python 3.13 / PyYAML 6.0.3. Los datos de entrada son no confiables.
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

import yaml

MAX_BYTES = 65536
MAX_NODES = 2000
MAX_DEPTH = 16
MAX_SEQUENCE = 500
MAX_SCALAR = 8192
FIELDS = frozenset(('handoff_version origen destino actividad_id tipo resumen datos '
                    'fuentes entregables pendientes riesgos estado_aprobacion fecha_generacion').split())
AGENTS = frozenset((
    'AGENTE_00_COORDINADOR', 'AGENTE_01_CHARLAS', 'AGENTE_02_INVESTIGADOR',
    'AGENTE_03_AGENDA', 'AGENTE_04_ASISTENCIAS_ENTREGAS', 'AGENTE_05_TAREAS',
    'AGENTE_06_NORMATIVA', 'AGENTE_07_PROGRAMADOR'))
TYPES = frozenset(('consulta', 'actividad', 'tarea', 'entrega', 'documento', 'recurso'))
STATES = frozenset(('borrador', 'pendiente_revision', 'aprobado', 'registrado',
                    'cerrado', 'rechazado', 'requiere_correccion'))
EVIDENCE_STATES = frozenset(('aprobado', 'registrado', 'cerrado'))
IDENTIFIER = re.compile(r'(?:BORRADOR-SIN-ID|ACT-[0-9]{4}-[0-9]{3})\Z')
INTERNAL_ID = re.compile(r'(?:ACT|TAR|ENT|DOC|PRO)-[0-9]{4}-[0-9]{3}\Z')
DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}\Z')
# Llaves con semántica inequívoca, no todas las cadenas que parecen fechas.
DATE_KEYS = frozenset(('fecha', 'fecha_corte', 'fecha_generacion', 'fecha_limite',
                       'vencimiento', 'fecha_emision', 'fecha_consulta'))
STRING_KEYS = frozenset(('asistencia', 'estado', 'titulo', 'tipo', 'nombre',
                         'prioridad', 'actividad_id', 'tarea_id', 'entrega_id',
                         'documento_id', 'producto_id'))
ID_KEYS = frozenset(('actividad_id', 'tarea_id', 'entrega_id', 'documento_id', 'producto_id'))

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

def _date(value: str) -> bool:
    if type(value) is not str or not DATE.fullmatch(value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False

def _walk(value, *, parent_key=None, depth=0, counts=None):
    if counts is None:
        counts = [0]
    counts[0] += 1
    if counts[0] > MAX_NODES or depth > MAX_DEPTH:
        raise ValidationError('estructura demasiado compleja')
    if isinstance(value, dict):
        if len(value) > MAX_SEQUENCE:
            raise ValidationError('mapa demasiado extenso')
        for key, child in value.items():
            if type(key) is not str or len(key) > MAX_SCALAR:
                raise ValidationError('clave de mapa invalida')
            if key in STRING_KEYS and type(child) is not str:
                raise ValidationError('campo de texto con tipo incorrecto')
            if key in ID_KEYS and type(child) is str:
                if key == 'actividad_id':
                    valid = bool(IDENTIFIER.fullmatch(child))
                else:
                    valid = bool(INTERNAL_ID.fullmatch(child)) and child.startswith({
                        'tarea_id': 'TAR-', 'entrega_id': 'ENT-',
                        'documento_id': 'DOC-', 'producto_id': 'PRO-'}[key])
                if not valid:
                    raise ValidationError('identificador interno invalido')
            if key in DATE_KEYS and not _date(child):
                raise ValidationError('fecha contextual invalida o no textual')
            _walk(child, parent_key=key, depth=depth+1, counts=counts)
    elif isinstance(value, list):
        if len(value) > MAX_SEQUENCE:
            raise ValidationError('lista demasiado extensa')
        for child in value:
            _walk(child, parent_key=parent_key, depth=depth+1, counts=counts)
    elif type(value) is str:
        if len(value) > MAX_SCALAR:
            raise ValidationError('texto demasiado largo')
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValidationError('numero no finito no permitido')
    elif value is None or type(value) in (bool, int):
        pass
    else:
        raise ValidationError('tipo YAML no permitido')

def parse_validate(source: str):
    if type(source) is not str or len(source.encode('utf-8')) > MAX_BYTES:
        raise ValidationError('entrada supera el limite de bytes')
    try:
        loader = BoundedLoader(source)
        try:
            value = loader.get_single_data()  # rechaza documentos multiples
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
    if set(value) != FIELDS:
        raise ValidationError('campos superiores faltantes o adicionales')
    for name in FIELDS - frozenset(('datos', 'fuentes', 'entregables', 'pendientes', 'riesgos')):
        if type(value[name]) is not str:
            raise ValidationError('campo superior con tipo incorrecto')
    if type(value['datos']) is not dict:
        raise ValidationError('datos debe ser un mapa')
    for name in ('fuentes', 'entregables', 'pendientes', 'riesgos'):
        if type(value[name]) is not list:
            raise ValidationError('campo de lista con tipo incorrecto')
    if value['handoff_version'] != '1.0':
        raise ValidationError('version HANDOFF no admitida')
    if value['origen'] not in AGENTS or value['destino'] not in AGENTS:
        raise ValidationError('agente fuera de catalogo')
    if value['tipo'] not in TYPES or value['estado_aprobacion'] not in STATES:
        raise ValidationError('tipo o estado fuera de catalogo')
    if not IDENTIFIER.fullmatch(value['actividad_id']):
        raise ValidationError('actividad_id invalido')
    if not _date(value['fecha_generacion']):
        raise ValidationError('fecha_generacion debe ser cadena ISO de fecha real')
    _walk(value)
    warnings = []
    if value['estado_aprobacion'] in EVIDENCE_STATES:
        warnings.append('estado requiere verificacion de evidencia externa')
    return value, warnings

def fingerprint(data: dict) -> str:
    # sha256 solo de datos normalizados; no se persiste ni se imprime el contenido.
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

class Session:
    """Deteccion local, en memoria: sin persistencia ni conexion remota."""
    def __init__(self):
        self.seen = set()
        self.references = {}

    def validate(self, source: str) -> dict:
        data, warnings = parse_validate(source)
        digest = fingerprint(data)
        duplicate = digest in self.seen
        reference = data['datos'].get('referencia_prueba')
        if type(reference) is str:
            if reference in self.references and digest not in self.references[reference]:
                warnings.append('misma referencia_prueba con contenido diferente')
            self.references.setdefault(reference, set()).add(digest)
        if duplicate:
            warnings.append('paquete identico repetido')
        self.seen.add(digest)
        return {'valido': True, 'duplicado': duplicate,
                'advertencias': warnings, 'huella_sha256': digest}

def main(argv=None):
    parser = argparse.ArgumentParser(description='Validar HANDOFF v1.0 local sin red')
    parser.add_argument('archivo', nargs='?', help='YAML local (sin argumento: stdin)')
    args = parser.parse_args(argv)
    try:
        if args.archivo:
            path = Path(args.archivo)
            if path.stat().st_size > MAX_BYTES:
                raise ValidationError('entrada supera el limite de bytes')
            source = path.read_text(encoding='utf-8')
        else:
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValidationError('entrada supera el limite de bytes')
            source = raw.decode('utf-8')
        result = Session().validate(source)
        # No imprime el paquete recibido ni sus valores internos.
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, UnicodeError, OSError) as exc:
        if isinstance(exc, ValidationError):
            reason = str(exc)
        else:
            reason = 'error de lectura o codificacion'
        print(json.dumps({'valido': False, 'error': reason}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
