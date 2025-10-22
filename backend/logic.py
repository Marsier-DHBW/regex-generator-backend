import csv
import json
import re
from io import StringIO
from xml.etree import ElementTree as ET

import ml.transformer
import ml.transformer as transformer
from backend.enums.FileType import FileType as ft
from backend.regexgenerators import build_json_regex, build_xml_regex, build_html_regex, build_csv_regex


def match(pattern: re.Pattern[str], string: str) -> bool:
    if string is None or len(string) == 0 or pattern is None:
        return False
    else:
        return bool(pattern.match(string))


def generate_regex(filetype: ft, string: str) -> str:
    regex: re.Pattern[str]
    match filetype:
        case ft.JSON:
            regex = build_json_regex.json_pattern(string)
        case ft.XML:
            regex = build_xml_regex.xml_pattern(string)
        case ft.HTML:
            regex = build_html_regex.html_pattern(string)
        case ft.CSV:
            regex = build_csv_regex.csv_pattern(string)
        case _:
            raise Exception(f"Unsupported file type: {filetype}")
    return str(regex.pattern)


def detect_filetype(string: str, is_file: bool, is_ml: bool) -> type(ft):
    """
    Erkennt den Dateityp eines Strings anhand seines Inhalts.
    Kann optional ML-Vorhersage verwenden.
    """
    filetype: type(ft) = ft.UNSUPPORTED
    if is_file:
        # Platzhalter für File-Erkennung (z. B. MIME-Typ oder Dateiendung)
        pass
    else:
        if is_ml:
            pred, probs = transformer.predict(string)
            filetype = ft[pred]
        else:
            data_string = string.strip()
            if not data_string:
                return ft.UNSUPPORTED

            # 1. JSON
            if is_json(data_string):
                return ft.JSON

            # 2. HTML
            if is_html(data_string):
                return ft.HTML

            # 3. XML
            if is_xml(data_string):
                return ft.XML

            # 4. CSV
            if is_csv(data_string):
                return ft.CSV

            # 5. Fallback
            return ft.UNSUPPORTED

    return filetype

def is_json(data_string: str) -> bool:
    """Prüft, ob der String gültiges JSON ist."""
    if not data_string or not data_string.strip().startswith(('{', '[')):
        return False
    try:
        json.loads(data_string)
        return True
    except json.JSONDecodeError:
        return False


def is_html(data_string: str) -> bool:
    """Prüft, ob der String HTML-Struktur enthält."""
    lower = data_string.lower().strip()
    if not lower.startswith('<'):
        return False
    if '<html' in lower or '<div' in lower or lower.startswith('<!doctype html>'):
        return True
    return False


def is_xml(data_string: str) -> bool:
    """Prüft, ob der String wohlgeformtes XML ist (aber kein HTML)."""
    if not data_string.strip().startswith('<'):
        return False
    try:
        ET.fromstring(data_string)
        # Ausschließen, falls HTML-Tags enthalten sind
        lower = data_string.lower()
        if '<html' in lower or '<div' in lower:
            return False
        return True
    except ET.ParseError:
        return False


def is_csv(data_string: str) -> bool:
    """Prüft, ob der String CSV- oder TSV-artige Struktur hat."""
    data_string = data_string.strip()
    if not data_string:
        return False

    # Häufige Trennzeichen in CSV/TSV-Dateien
    common_delimiters = [',', ';', '\t', '|', ':']

    # Mindeststruktur: mehrere Zeilen oder mehrere Trennzeichen
    if '\n' not in data_string and not any(data_string.count(d) >= 1 for d in common_delimiters):
        return False

    try:
        sample = data_string[:4096]  # Größerer Sample-Bereich
        f = StringIO(sample)

        # csv.Sniffer versucht automatisch, das richtige Trennzeichen zu erkennen
        dialect = csv.Sniffer().sniff(sample, delimiters=common_delimiters)
        f.seek(0)
        reader = csv.reader(f, dialect)

        rows = []
        for _ in range(5):  # bis zu 5 Zeilen prüfen
            try:
                row = next(reader)
                rows.append(row)
            except StopIteration:
                break

        # mindestens 2 Zeilen mit konsistenter Spaltenstruktur
        if len(rows) < 2:
            return False

        col_count = len(rows[0])
        if col_count < 2:
            return False

        return all(len(r) == col_count for r in rows)

    except csv.Error:
        return False


if __name__ == '__main__':
    ml.transformer.prepare_model()