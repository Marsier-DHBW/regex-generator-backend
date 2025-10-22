from re import Pattern
import re
import csv
import io

class CsvRegexGenerator:
    """
    Generiert ein Regex aus einer Beispiel-CSV-Datei, um die strukturelle Integrität
    anderer CSV-Dateien zu validieren.
    """

    def __init__(self, delimiter: str = ','):
        """
        Initialisiert den Generator.

        :param delimiter: Das in der CSV-Datei verwendete Trennzeichen.
        """
        self.delimiter = delimiter

    def _infer_column_pattern(self, column_data: list[str]) -> str:
        """
        Leitet aus einer Liste von Spaltenwerten ein passendes Regex-Pattern ab.
        """
        # Prüft, ob alle Werte ganze Zahlen sind
        if all(re.fullmatch(r'\d+', item) for item in column_data if item):
            return r'\d+'

        # Prüft, ob alle Werte Zahlen sind (Ganzzahlen oder Dezimalzahlen)
        if all(re.fullmatch(r'\d+(\.\d+)?', item) for item in column_data if item):
            return r'\d+(\.\d+)?'

        # Standard-Pattern für allgemeinen Text (alles außer dem Trennzeichen)
        # Erlaubt auch leere Felder
        return f'[^{self.delimiter}]*'

    def generate_regex(self, example_csv_content: str) -> str:
        """
        Erstellt ein Regex, das die Struktur der übergebenen CSV-Daten abbildet.

        :param example_csv_content: Ein String, der den Inhalt der Beispiel-CSV darstellt.
        :return: Ein Regex-String zur Validierung der CSV-Struktur.
        """
        if not example_csv_content:
            return ""

        reader = csv.reader(io.StringIO(example_csv_content), delimiter=self.delimiter)

        try:
            header = next(reader)
            data_rows = list(reader)
        except StopIteration:
            # CSV ist leer oder hat nur einen Header
            return ""

        if not data_rows:
            # Wenn es keine Datenzeilen gibt, kann keine Struktur abgeleitet werden.
            # Wir können nur auf den Header prüfen.
            header_pattern = self.delimiter.join([re.escape(h) for h in header])
            return f'^{header_pattern}\r?\n?$'

        num_columns = len(header)
        columns_data = [[] for _ in range(num_columns)]

        for row in data_rows:
            # Stellt sicher, dass die Zeile die erwartete Anzahl von Spalten hat
            if len(row) == num_columns:
                for i, cell in enumerate(row):
                    columns_data[i].append(cell)

        # Leitet für jede Spalte ein Pattern ab
        column_patterns = [self._infer_column_pattern(col) for col in columns_data]

        # Baut das Regex für eine einzelne Datenzeile
        row_pattern = self.delimiter.join(column_patterns)

        # Baut das finale Regex
        # 1. Header (exakter Match)
        # 2. Newline
        # 3. Eine oder mehrere Datenzeilen, die dem abgeleiteten Muster entsprechen
        header_pattern = self.delimiter.join([re.escape(h) for h in header])

        # Das Regex prüft den Header und dann beliebig viele passende Datenzeilen
        final_regex = f'^{header_pattern}\r?\n({row_pattern}\r?\n)*{row_pattern}?$'

        return final_regex

# Beispiel für die Verwendung
if __name__ == '__main__':
    # Beispiel-CSV-Daten
    csv_content = """id,name,value
1,product_a,19.99
2,product_b,25.50
3,product_c,10
"""

    # Generator erstellen und Regex generieren
    csv_regex_builder = CsvRegexGenerator(delimiter=',')
    structure_regex = csv_regex_builder.generate_regex(csv_content)

    print(f"Generiertes Regex:\n{structure_regex}\n")

    # Eine weitere CSV-Datei zum Testen
    test_csv_valid = """id,name,value
10,test_1,100.1
11,test_2,200
"""

    test_csv_invalid_structure = """id,name,value
10,test_1,100.1
11,test_2,should_be_a_number
"""

    test_csv_invalid_columns = """id,name
10,test_1
"""

    # Validierung
    print("--- Validierung ---")
    print(f"Test 1 (Valide): {bool(re.fullmatch(structure_regex, test_csv_valid.strip()))}")
    print(f"Test 2 (Invalide Daten): {bool(re.fullmatch(structure_regex, test_csv_invalid_structure.strip()))}")
    print(f"Test 3 (Invalide Spalten): {bool(re.fullmatch(structure_regex, test_csv_invalid_columns.strip()))}")


def csv(string: str) -> Pattern[str]:
    return None