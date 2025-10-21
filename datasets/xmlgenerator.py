import random
import string
import csv

def random_string(length=None):
    """Erzeugt zufällige Kleinbuchstaben-Strings mit Länge 1–7 (Standard)"""
    if length is None:
        length = random.randint(1, 7)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_attributes(num_attrs=None):
    """Erzeugt zufällige XML-Attribute"""
    if num_attrs is None:
        num_attrs = random.randint(0, 2)  # 0–3 Attribute pro Tag
    attrs = []
    for _ in range(num_attrs):
        key = random_string(random.randint(1, 5))
        val = random_string(random.randint(2, 8))
        attrs.append(f'{key}="{val}"')
    return " " + " ".join(attrs) if attrs else ""


def generate_nested_xml(tag_name="root", max_depth=3, current_depth=1):
    max_depth = max_depth - 1
    """Erzeugt verschachtelte XML-Struktur mit Attributen, Listen und mehreren Kindern."""
    xml = f"<{tag_name}{random_attributes()}>"

    # Anzahl Kinder
    num_children = random.randint(1, 6)

    for _ in range(num_children):
        tag = random_string()
        element_type = random.choice(["text", "child", "list"])

        # Textinhalt
        if element_type == "text" or current_depth >= max_depth:
            xml += f"<{tag}{random_attributes()}>{random_string(random.randint(3,8))}</{tag}>"

        # Rekursive Verschachtelung (child)
        elif element_type == "child":
            xml += generate_nested_xml(tag, max_depth=max_depth, current_depth=current_depth + 1)

        # Liste (mehrere gleichnamige Kinder)
        elif element_type == "list" and current_depth < max_depth:
            list_tag = random_string()
            num_items = random.randint(2, 5)
            xml += f"<{tag}>"
            for _ in range(num_items):
                xml += f"<{list_tag}{random_attributes()}>{random_string(random.randint(2, 8))}</{list_tag}>"
            xml += f"</{tag}>"

    xml += f"</{tag_name}>"
    return xml

num_samples = 5000  # Anzahl XML-Beispiele
data = []

for _ in range(num_samples):
    xml_str = generate_nested_xml(max_depth=random.choice([1, 3]))
    data.append((xml_str, 1))  # Label 1 = XML

# -----------------------
# In CSV-Datei speichern
# -----------------------

csv_path = "xml_dataset.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["text", "label"])
    writer.writerows(data)

print(f"Datei '{csv_path}' erfolgreich erstellt ({len(data)} Beispiele).")