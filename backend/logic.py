import re
import os
from .FileType import FileType as ft
import ml.transformer as transformer
import json
import csv
from io import StringIO
from xml.etree import ElementTree as ET
from .regexgenerator import RegexGenerator

def match(pattern: str, string: str) -> bool:
    if string is None:
        return False
    else:
        return bool(re.match(pattern=pattern, string=string))



def build_regex(filetype: ft, string: str) -> str:
    regex: re.Pattern[str]
    match filetype:
        case ft.JSON:
            regex = RegexGenerator.json(string)
        case ft.XML:
            regex = RegexGenerator.xml(string)
        case ft.HTML:
            regex = RegexGenerator.html(string)
        case ft.CSV:
            regex = RegexGenerator.csv(string)
        case _:
            raise Exception(f"Unsupported file type: {filetype}")
    return str(regex.pattern)


def detect_filetype(string: str, is_file: bool, is_ml: bool) -> ft:
    filetype: type(ft) = ft.UNSUPPORTED
    if is_file:
        pass
        # easy logic
    else:
        if is_ml:
            pred, probs = transformer.predict(string)
            filetype = ft[pred]
        else:
            # Flo logic
            data_string = string.strip()
            if not data_string:
                return "EMPTY"

            # 1. JSON-Prüfung
            # JSON startet fast immer mit '{' (Objekt) oder '[' (Array)
            if data_string.startswith(('{', '[')):
                try:
                    json.loads(data_string)
                    return "JSON"
                except json.JSONDecodeError:
                    pass

            # 2. XML / HTML-Prüfung
            # XML und HTML beginnen typischerweise mit '<'
            if data_string.startswith('<'):
                try:
                    # Versuche, es als XML zu parsen
                    # (auch die meisten HTML-Dokumente können rudimentär geparst werden)
                    ET.fromstring(data_string)

                    # Spezifische HTML-Prüfung (optional, verbessert die Unterscheidung)
                    if data_string.lower().startswith('<!doctype html>') or '<html' in data_string.lower():
                        return "HTML"

                    # Wenn erfolgreich geparst, aber kein offensichtliches HTML
                    return "XML"

                except ET.ParseError:
                    # Wenn das Parsing fehlschlägt, ist es kein gültiges XML/HTML
                    pass

            # 3. CSV-Prüfung
            # CSVs haben keine spezifischen Anfangszeichen, daher prüfen wir zuletzt.
            # Wir verwenden csv.Sniffer, um den Delimiter zu erraten
            # und prüfen, ob die ersten Zeilen konsistente Felder aufweisen.
            try:
                # StringIO wird verwendet, um den String wie eine Datei zu behandeln
                f = StringIO(data_string)

                # Lese die ersten paar Zeilen, um den Sniffer zu füttern
                sample = f.read(1024)
                f.seek(0)

                # Prüfe, ob der String überhaupt Zeilenumbrüche enthält,
                # sonst ist es unwahrscheinlich ein sinnvolles CSV.
                if '\n' not in sample and len(data_string.split(',')) <= 1:
                    return "TEXT"  # Wahrscheinlich nur eine Textzeile

                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(f, dialect)

                # Überprüfe die ersten 3 Zeilen auf Konsistenz (Heuristik)
                rows = [next(reader) for _ in range(3)]

                if not rows:
                    return "TEXT"  # Nur eine leere Datei oder so

                first_len = len(rows[0])

                # Es ist wahrscheinlich ein CSV, wenn die ersten Zeilen die gleiche Anzahl Spalten haben
                if all(len(row) == first_len for row in rows):
                    if first_len > 1 or (first_len == 1 and dialect.delimiter != ''):
                        return "CSV"

            except (csv.Error, StopIteration):
                # Der csv.Sniffer oder Reader konnte das Format nicht verarbeiten
                pass
            except IndexError:
                # Weniger als 3 Zeilen
                if first_len > 1:
                    return "CSV"
                pass

            # 4. Fallback
            # Wenn alle Prüfungen fehlschlagen
            return "UNKNOWN"

    return filetype
