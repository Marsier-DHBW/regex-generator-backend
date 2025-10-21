import random
import string
import csv


def random_string(length=None):
    """Erzeugt zufällige Kleinbuchstaben-Strings"""
    if length is None:
        length = random.randint(1, 7)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_attributes(num_attrs=None):
    """Erzeugt zufällige HTML-Attribute"""
    if num_attrs is None:
        num_attrs = random.randint(0, 2)
    attrs = []
    for _ in range(num_attrs):
        key = random.choice(["id", "class", random_string(random.randint(2, 6))])
        val = random_string(random.randint(2, 8))
        attrs.append(f'{key}="{val}"')
    return " " + " ".join(attrs) if attrs else ""

def random_tag():
    """Zufällige HTML-Tags"""
    base_tags = [
        "div", "span", "p", "a", "ul", "li", "section",
        "article", "header", "footer", "main", "em", "strong",
        "h1", "h2", "h3", "table", "tr", "td", "nav"
    ]
    return random.choice(base_tags)

def generate_nested_html(tag_name="html", max_depth=3, current_depth=1):
    max_depth = max_depth - 1
    """Generiert HTML mit Tiefe 2–3, Attributen, Listen und Text."""
    html = f"<{tag_name}{random_attributes()}>"

    num_children = random.randint(2, 6)

    for _ in range(num_children):
        tag = random_tag()
        element_type = random.choice(["text", "child", "list"])

        # Einfacher Textinhalt
        if element_type == "text" or current_depth >= max_depth:
            html += f"<{tag}{random_attributes()}>{random_string(random.randint(5, 15))}</{tag}>"

        # Rekursive Verschachtelung (child)
        elif element_type == "child":
            html += generate_nested_html(tag, max_depth=max_depth, current_depth=current_depth + 1)

        # Liste (ul/li oder divs)
        elif element_type == "list" and current_depth < max_depth:
            list_tag = random.choice(["ul", "div", "section"])
            item_tag = random.choice(["li", "p", "span"])
            num_items = random.randint(3, 6)
            html += f"<{list_tag}{random_attributes()}>"
            for _ in range(num_items):
                html += f"<{item_tag}{random_attributes()}>{random_string(random.randint(3, 12))}</{item_tag}>"
            html += f"</{list_tag}>"

    html += f"</{tag_name}>"
    return html

num_samples = 5000  # Anzahl HTML-Beispiele
data = []

for _ in range(num_samples):
    html_str = generate_nested_html("html", max_depth=random.choice([2, 3]))
    data.append((html_str, 3))  # Label 3 = HTML

csv_path = "html_dataset.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["text", "label"])
    writer.writerows(data)

print(f"Datei '{csv_path}' erfolgreich erstellt ({len(data)} Beispiele).")