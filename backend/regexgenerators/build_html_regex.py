import re
from re import Pattern

def html_pattern(string: str) -> Pattern[str]:
    regex_pattern = __build_html_regex(string)
    return re.compile(regex_pattern, re.DOTALL)

def __build_html_regex(example_html: str) -> str:
    """
    Erstellt ein Regex, das die Struktur des übergebenen HTML-Snippets abbildet.
    Funktioniert am besten für einfache, wiederholte Strukturen wie Tabellen oder Listen.
    """
    # Entferne führende/trailing Whitespaces
    html = example_html.strip()

    # Extrahiere alle Tags in Reihenfolge
    tags = re.findall(r'<(/?)(\w+)[^>]*>', html)
    if not tags:
        return re.escape(html)

    # Erstelle eine Liste der Tag-Struktur
    tag_stack = []
    structure = []
    for slash, tag in tags:
        if not slash:
            tag_stack.append(tag)
            structure.append(f"<{tag}[^>]*>")
        else:
            if tag_stack and tag_stack[-1] == tag:
                tag_stack.pop()
                structure.append(f"</{tag}>")

    # Ersetze Inhalte zwischen Tags durch ein allgemeines Pattern
    # (z.B. für Tabellenzellen oder Listeneinträge)
    content_pattern = r"[^<]*"
    regex = ""
    last_end = 0
    for match in re.finditer(r'<[^>]+>', html):
        start, end = match.span()
        # Füge Pattern für Inhalt zwischen Tags ein
        if start > last_end:
            regex += content_pattern
        regex += re.escape(html[start:end])
        last_end = end
    if last_end < len(html):
        regex += content_pattern

    # Optional: Versuche, wiederholte Strukturen zu erkennen (z.B. <tr>...</tr>)
    # und fasse sie als Gruppe mit * oder + zusammen
    # (Hier nur für einfache Tabellenzeilen demonstriert)
    regex = re.sub(
        r'(' + re.escape('<tr>') + content_pattern + re.escape('</tr>') + r')+',
        r'(' + re.escape('<tr>') + content_pattern + re.escape('</tr>') + r')+',
        regex
    )

    # Regex soll den gesamten String matchen
    return f"^{regex}$"