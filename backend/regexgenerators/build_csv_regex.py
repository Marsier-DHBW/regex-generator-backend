import csv
import io
import re
from re import Pattern

# Berücksichtigte Trennzeichen
common_delimiters = [',', ';', '\t', '|', ':']


def csv_pattern(string: str) -> Pattern[str]:
    regex_pattern = build_csv_regex(string)
    return re.compile(regex_pattern)


def __infer_column_pattern(column_data: list[str], delimiter: str) -> str:
    """
    Leitet aus einer Liste von Spaltenwerten ein passendes Regex-Pattern ab.
    """
    # Prüft, ob alle Werte ganze Zahlen sind
    if all(re.fullmatch(r'\d+', item) for item in column_data if item):
        return r'\d+'

    # Prüft, ob alle Werte Zahlen sind (Ganzzahlen oder Dezimalzahlen)
    if all(re.fullmatch(r'\d+(?:\.\d+)?', item) for item in column_data if item):
        return r'\d+(?:\.\d+)?'

    # Standard-Pattern für allgemeinen Text (alles außer dem Trennzeichen)
    return f'[^{re.escape(delimiter)}]*'


def build_csv_regex(example_csv_content: str) -> str:
    """
    Erstellt ein Regex, das die Struktur der übergebenen CSV-Daten abbildet.
    Das Trennzeichen wird automatisch aus der Liste common_delimiters erkannt.

    :param example_csv_content: Ein String, der den Inhalt der Beispiel-CSV darstellt.
    :return: Ein Regex-String zur Validierung der CSV-Struktur.
    """
    if not example_csv_content.strip():
        return ""

    # Trennzeichen automatisch erkennen
    try:
        # Sniffer analysiert eine Probe der Daten, um das Format zu erkennen
        sample = '\n'.join(example_csv_content.splitlines()[:5])
        dialect = csv.Sniffer().sniff(sample, delimiters=''.join(common_delimiters))
        delimiter = dialect.delimiter
    except (csv.Error, IndexError):
        # Fallback, wenn Sniffer fehlschlägt oder der Inhalt zu klein ist
        try:
            first_line = example_csv_content.splitlines()[0]
            counts = {d: first_line.count(d) for d in common_delimiters}
            delimiter = max(counts, key=counts.get)
            if counts[delimiter] == 0:
                delimiter = ','  # Standard-Trennzeichen
        except IndexError:
            return ""  # Leerer Inhalt

    reader = csv.reader(io.StringIO(example_csv_content), delimiter=delimiter)

    try:
        header = next(reader)
        # Filtere leere Zeilen und Zeilen mit falscher Spaltenanzahl sofort
        num_columns = len(header)
        data_rows = [row for row in reader if row and len(row) == num_columns]
    except StopIteration:
        return ""  # Leere CSV

    header_pattern = re.escape(delimiter).join([re.escape(h) for h in header])
    line_ending_pattern = r'(?:\r?\n)'

    # Wenn es keine validen Datenzeilen gibt, nur auf den Header prüfen
    if not data_rows:
        return f'^{header_pattern}(?:{line_ending_pattern})?$'

    columns_data = [[] for _ in range(num_columns)]
    for row in data_rows:
        for i, cell in enumerate(row):
            columns_data[i].append(cell)

    column_patterns = [__infer_column_pattern(col, delimiter) for col in columns_data]
    row_pattern = re.escape(delimiter).join(column_patterns)

    # Finales Regex:
    # 1. ^(header)
    # 2. (?:\r?\n(row_pattern))*  -> Null oder mehr Datenzeilen
    # 3. (?:\r?\n)?$             -> Optionaler abschließender Zeilenumbruch
    final_regex = f'^{header_pattern}(?:{line_ending_pattern}{row_pattern})*(?:{line_ending_pattern})?$'

    return final_regex


# Beispiel für die Verwendung
if __name__ == '__main__':
    # Beispiel 1: Komma als Trennzeichen
    csv_content_comma = """ id,name,value
                            1,product_a,19.99
                            2,product_b,25.50
                            3,product_c,10
                        """
    print("--- Beispiel 1: Komma-getrennt ---")
    structure_regex_comma = build_csv_regex(csv_content_comma)
    print(f"Generiertes Regex:\n{structure_regex_comma}\n")

    test_csv_valid = """    
                        id,name,value
                        10,test_1,100.1
                        11,test_2,200
                    """

    test_csv_invalid_data = """id,name,value
10,test_1,not_a_number"""

    print(f"Test 1 (Valide): {bool(re.fullmatch(structure_regex_comma, test_csv_valid))}")
    print(f"Test 2 (Invalide Daten): {bool(re.fullmatch(structure_regex_comma, test_csv_invalid_data))}")

    # Beispiel 2: Pipe als Trennzeichen
    csv_content_pipe = """id|name|value
1|product_a|19.99
"""
    print("\n--- Beispiel 2: Pipe-getrennt ---")
    structure_regex_pipe = build_csv_regex(csv_content_pipe)
    print(f"Generiertes Regex:\n{structure_regex_pipe}\n")

    test_csv_pipe_valid = """id|name|value
10|test_1|100.1"""

    test_csv_pipe_invalid_structure = """id|name|value|extra
10|test_1|100.1|fail"""

    print(f"Test 3 (Valide): {bool(re.fullmatch(structure_regex_pipe, test_csv_pipe_valid))}")
    print(f"Test 4 (Invalide Struktur): {bool(re.fullmatch(structure_regex_pipe, test_csv_pipe_invalid_structure))}")
