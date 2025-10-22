import random
import string
import csv

def random_string(length=None):
    """Erzeugt zufällige Kleinbuchstaben-Strings"""
    if length is None:
        length = random.randint(3, 8)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_column_values(num_rows, col_type):
    """Erzeugt Werte für eine Spalte, entweder alle Strings oder alle Zahlen"""
    values = []
    if col_type == "int":
        for _ in range(num_rows):
            values.append(str(random.randint(0, 100)))
    else:  # string
        for _ in range(num_rows):
            values.append(random_string(random.randint(2, 8)))
    return values

def generate_csv_example():
    """Erzeugt einen CSV-Text mit 2–6 Spalten, 2–6 Zeilen, konsistente Typen pro Spalte"""
    num_columns = random.randint(2, 6)
    num_rows = random.randint(2, 30)

    # Spaltennamen
    headers = [random_string(random.randint(1,7)) for _ in range(num_columns)]

    # Bestimme zufällig Typ jeder Spalte
    col_types = [random.choice(["int", "string"]) for _ in range(num_columns)]

    # Trennzeichen zufällig auswählen
    delimiter = random.choice([",", ";"])

    # CSV-Text aufbauen
    columns = [random_column_values(num_rows, col_type) for col_type in col_types]

    # Zeilen zusammenbauen
    lines = [delimiter.join(headers)]
    for i in range(num_rows):
        row = [columns[j][i] for j in range(num_columns)]
        lines.append(delimiter.join(row))

    return "\n".join(lines)

def generate(rows=5000):  # Anzahl CSV-Beispiele
    data = []

    for _ in range(rows):
        csv_text = generate_csv_example()
        data.append((csv_text, 2))  # Label 2 = CSV

    csv_path = "csv_dataset.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["text", "label"])
        writer.writerows(data)

    print(f"Datei '{csv_path}' erfolgreich erstellt ({len(data)} Beispiele).")
