import json
import random
import string
import csv
from datasets import load_dataset

def random_string(length=5):
    """Erzeugt zufällige Kleinbuchstaben-Strings"""
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_nested_json(max_depth=3, current_depth=1):
    """Erzeugt ein JSON-Objekt mit variabler Verschachtelungstiefe (max_depth)"""
    max_depth = max_depth - 1
    obj = {}
    num_keys = random.randint(2, 5)

    for _ in range(num_keys):
        key = random_string(random.randint(1, 7))
        value_type = random.choice(['int', 'str', 'list', 'object'])

        if value_type == 'int':
            obj[key] = random.randint(0, 100)
        elif value_type == 'str':
            obj[key] = random_string(random.randint(1, 7))
        elif value_type == 'list':
            # Listen enthalten primitive Werte oder einfache Dicts
            if random.random() < 0.5:
                obj[key] = [random.randint(0, 10) for _ in range(random.randint(2, 5))]
            else:
                obj[key] = [{random_string(random.randint(1, 7)): random.randint(0, 50)} for _ in range(random.randint(2, 4))]
        elif value_type == 'object' and current_depth < max_depth:
            obj[key] = generate_nested_json(max_depth=max_depth, current_depth=current_depth + 1)
        else:
            # Falls maximale Tiefe erreicht
            obj[key] = random.randint(0, 100)

    return obj

num_samples = 5000  # Anzahl JSON-Beispiele
data = []

for _ in range(num_samples):
    json_obj = generate_nested_json(max_depth=random.choice([1, 3]))
    json_str = json.dumps(json_obj)
    data.append((json_str, 0))  # Label 0 = JSON

csv_path = "json_dataset.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["text", "label"])  # Header
    writer.writerows(data)

print(f"Datei '{csv_path}' erfolgreich erstellt ({len(data)}) Beispiele.")
