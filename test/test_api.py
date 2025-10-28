import sys, os
# Projektroot zum Pythonpfad hinzufügen (wie im Original)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import re
# Angenommen, das Modul 'logic' existiert und ist importierbar
from backend import logic
from backend.enums.FileType import FileType

# ============================================================
# Tests für logic.match
# ============================================================

class TestMatch:
    @pytest.mark.parametrize("regex_str, text, expected", [
        # 1. Partielle Übereinstimmung (Anfang)
        (r"Hello", "HelloWorld", False),

        # 2. Partielle Übereinstimmung (Ende)
        (r"World", "HelloWorld", False),

        # 3. Exakter Match (nur Ziffern)
        (r"^\d+$", "12345", True),

        # 4. Fehlerhafte Ziffernfolge (zu lang, wenn \d{3} impliziert ist)
        (r"\d{3}", "12345", False),

        # 5. Führender Whitespace (schlägt fehl, da er nicht im Regex ist)
        (r"Test", " Test", False),

        # 6. Nachgestellter Whitespace (schlägt fehl, da er nicht im Regex ist)
        (r"Test", "Test ", False),

        # 7. Match, das Whitespace am Ende explizit erlaubt (muss True sein)
        (r"Test\s*", "Test ", True),

        # 8. Match mit Literal-Sonderzeichen (Punkt muss escaped werden)
        (r"file\.txt", "file.txt", True),

        # 9. Case Sensitivity (sollte fehlschlagen, da H und h unterschiedlich sind)
        (r"HTTP", "http", False),

        # 10. Komplexerer Full Match
        (r"(\w+-\d{4})$", "Project-2024", True),
    ])
    def test_match_extended_cases(self, regex_str, text, expected):
        """
        Testet die stricte Voll-Match-Anforderung:
        Die gesamte 'text'-Zeichenkette muss dem 'regex_str' entsprechen.
        (Simuliert re.fullmatch oder implizite ^/$ Anker).
        """
        try:
            regex = re.compile(regex_str)
            assert logic.match(regex, text) is expected
        except re.error as e:
            # Für den unwahrscheinlichen Fall, dass der Test-Regex nicht kompiliert.
            pytest.fail(f"Regex-Kompilierungsfehler für '{regex_str}': {e}")


# ============================================================
# Tests für logic.generate_regex - Fokus: Strukturprüfung
# ============================================================

class TestGenerateRegex:

    @pytest.mark.parametrize("filetype, source_text, matching_text, non_matching_text", [
        # JSON: Objektstruktur muss erhalten bleiben
        (
                FileType.JSON,
                '{"name": "Alice", "age": 30}',
                '{"name": "Bob", "age": 99}',
                '{"name": "Bob", "height": 99}'
        ),

        # CSV: Header und die Anzahl der Felder pro Zeile müssen passen
        (
                FileType.CSV,
                "ID,Date,Value\n1,2024-01-01,test",
                "ID,Date,Value\n10,2025-05-15,ne",
                "ID,Date\n1,2024-01-01,100"
        ),

        # XML: Tags und die geschlossene Hierarchie müssen passen
        (
                FileType.XML,
                "<user><id>123</id><name>Max</name></user>",
                "<user><id>999</id><name>Leo</name></user>",
                "<user><id>123</id><phone>555</phone></user>"
        ),

        # HTML: Das Vorhandensein spezifischer Tags und Attribute muss passen
        (
                FileType.HTML,
                '<h1>Title</h1><p class="intro">Text</p>',
                '<h1>New Title</h1><p class="intro">Different text</p>',
                '<h1>Title</h1><div class="intro">Text</div>'
        ),
    ])
    def test_generated_regex_matches_correct_structure(self, filetype, source_text, matching_text, non_matching_text):
        """
        Generiert ein Regex aus 'source_text' und testet, ob es:
        1. Den 'matching_text' (gleiche Struktur) erfolgreich matched (True).
        2. Den 'non_matching_text' (abweichende Struktur) nicht matched (False).
        """

        # 1. Generiere das Regex basierend auf dem Quell-String
        try:
            generated_regex_str = logic.generate_regex(filetype=filetype, string=source_text)
            generated_regex = re.compile(generated_regex_str)
        except Exception as e:
            pytest.fail(f"Fehler bei der Regex-Generierung für {filetype.name}: {e}")

        # Wichtiger Schritt: Überprüfe, ob die generierte Regex die richtige Struktur erkennt
        # Wir verwenden logic.match, welches (wie in der vorherigen Antwort bestätigt)
        # den gesamten String überprüfen soll (Full Match).

        # 2. Test gegen den passenden String
        match_result = logic.match(generated_regex, matching_text)
        assert match_result is True, (
            f"FEHLGESCHLAGEN: Generated Regex:\n'{generated_regex_str}' "
            f"\n\tsollte matchen:\n'{matching_text}'"
        )

        # 3. Test gegen den NICHT passenden String
        non_match_result = logic.match(generated_regex, non_matching_text)
        assert non_match_result is False, (
            f"FEHLGESCHLAGEN: Generated Regex:\n'{generated_regex_str}' "
            f"\n\tsollte NICHT matchen:\n'{non_matching_text}'"
        )

    def test_generate_regex_csv_quoted_fields_structure(self):
        """
        Spezialfall CSV: Prüfen, ob das Regex korrekt mit Anführungszeichen umgehen kann,
        wenn die Daten variieren.
        """
        source_text = 'ID,"Name, Titel",Age\n1,"Max Mustermann, CEO",30'
        matching_text = 'ID,"Name, Titel",Age\n2,"Erika Mustermann, CTO",45'
        non_matching_text = 'ID,"Name, Titel",Age\n2,"Erika Mustermann",45'  # Fehler: 2 Felder im Anführungszeichen statt 3

        generated_regex_str = logic.generate_regex(filetype=FileType.CSV, string=source_text)
        generated_regex = re.compile(generated_regex_str)

        # Test 1: Match
        assert logic.match(generated_regex, matching_text) is True

        # Test 2: Non-Match (Strukturfehler in der Anzahl der Felder)
        assert logic.match(generated_regex, non_matching_text) is False

    def test_generate_regex_large_input_still_matches(self):
        """
        Stellt sicher, dass auch bei großen Eingaben das resultierende Regex
        noch funktioniert und die Struktur beibehält.
        """
        source_text = "<data>" + "x" * 1000 + "</data>"
        matching_text = "<data>" + "y" * 500 + "</data>"  # Unterschiedliche Länge, aber gleiche Tags

        generated_regex_str = logic.generate_regex(filetype=FileType.XML, string=source_text)
        generated_regex = re.compile(generated_regex_str)

        # Das generierte Regex sollte es erlauben, dass der Inhalt zwischen den <data> Tags variiert.
        assert logic.match(generated_regex, matching_text) is True

    def test_generate_regex_invalid_filetype(self):
        with pytest.raises(Exception):
            logic.generate_regex(filetype=FileType.UNSUPPORTED, string="test")

    @pytest.mark.parametrize("filetype", [
        FileType.JSON,
        FileType.CSV,
        FileType.XML,
        FileType.HTML,
    ])
    def test_generate_regex_empty_text_all_types(self, filetype):
        """
        Stellt sicher, dass für alle unterstützten Dateitypen eine Exception ausgelöst wird,
        wenn der Eingabestring leer ist.
        """
        with pytest.raises(Exception):
            logic.generate_regex(filetype=filetype, string="")

# ============================================================
# Tests für logic.detect_filetype
# ============================================================

class TestDetectFiletype:
    @pytest.mark.parametrize("text,expected", [
        ('{"key": "value"}', FileType.JSON),
        ("<root></root>", FileType.XML),
        ("<html><body></body></html>", FileType.HTML),
        ("col1,col2\n1,2", FileType.CSV),
        # Neuer Test: CSV mit Semikolon (abweichender Delimiter)
        ("col1;col2\n1;2", FileType.CSV),
        # Neuer Test: Nur JSON Array
        ("[\n  1,\n  2,\n  3\n]", FileType.JSON),
        # Neuer Test: XML mit viel Whitespace
        ("""
        <root>
            <item/>
        </root>
        """, FileType.XML),
    ])
    def test_detect_filetype_simple_and_enhanced(self, text, expected):
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
        # Überprüft, ob der erwartete Typ in den Wahrscheinlichkeiten vorkommt
        assert any(expected.name.lower() == k.lower() for k in result.keys())

    def test_detect_filetype_malformed_json(self):
        text = '{"key": value" :}'
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
        # Es sollte immer noch eine hohe Wahrscheinlichkeit für JSON geben
        # (Dies hängt von der Implementierung ab, ist aber ein sinnvoller Test)

    def test_detect_filetype_csv_only_header(self):
        # Edge Case: CSV nur mit Kopfzeile, keine Daten
        text = "Header1,Header2,Header3"
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
        # Erwartet hohe CSV-Wahrscheinlichkeit
        assert any(FileType.CSV.name.lower() == k.lower() for k in result.keys())

    def test_detect_filetype_empty_string(self):
        with pytest.raises(Exception):
            logic.detect_filetype(string="", is_ml=False)

    # Die ML-Mock-Tests sind im Original bereits gut und werden hier ausgelassen.

# ============================================================
# Tests für logic.generate_regex - Extreme Edge Cases (Tiefe & Strenge)
# ============================================================

class TestGenerateRegexExtremeEdgeCases:

    @pytest.mark.parametrize("filetype, source_text, matching_text, non_matching_text", [
        # JSON (Tiefe 3): Prüft das Hinzufügen eines unnötigen Keys auf der tiefsten Ebene
        (
            FileType.JSON,
            '{"user": {"address": {"city": "Berlin"}}}',
            '{"user": {"address": {"city": "Hamburg"}}}',
            '{"user": {"address": {"city": "Berlin", "extra": "data"}}}'
        ),
        # XML (Tiefe 3 mit Attributen): Prüft das Hinzufügen eines Tags auf der tiefsten Ebene
        (
            FileType.XML,
            '<root><section type="doc"><item id="1"/></section></root>',
            '<root><section type="guide"><item id="99"/></section></root>',
            '<root><section type="doc"><item id="1"><sub-item/></item></section></root>' # Extra Tag auf Ebene 3
        ),
        # CSV (Komplexes Escaping): Prüft, ob das Regex korrekt erkennt, wenn Quoting-Regeln verletzt werden
        (
            FileType.CSV,
            'Col1,"Col2, Quoted",Col3\nVal1,"Value, with comma",Val3',
            'Col1,"Col2, Quoted",Col3\nValA,"Another, value",ValB',
            'Col1,"Col2, Quoted",Col3\nValA,Another value,ValB'
        ),
        # HTML (Sibling Tags): Prüft, ob die Reihenfolge und Art der Geschwister-Elemente fixiert ist
        (
            FileType.HTML,
            '<div><p>Text</p><span>Link</span></div>',
            '<div><p>New Text</p><span>New Link</span></div>',
            '<div><span>Link</span><p>Text</p></div>'
        ),
    ])
    def test_generated_regex_nested_and_strict(self, filetype, source_text, matching_text, non_matching_text):
        """
        Testet erweiterte Edge Cases: Tiefe Verschachtelung (Tiefe >= 3) und strikte
        Erkennung von minimalen Strukturverletzungen auf den inneren Ebenen.
        """

        # 1. Generiere das Regex basierend auf dem Quell-String
        try:
            generated_regex_str = logic.generate_regex(filetype=filetype, string=source_text)
            generated_regex = re.compile(generated_regex_str)
        except Exception as e:
            pytest.fail(f"Fehler bei der Regex-Generierung für {filetype.name} (Nested Test): {e}")

        # Wichtiger Schritt: Überprüfe, ob die generierte Regex die richtige Struktur erkennt
        # Wir verwenden logic.match, welches (wie in der vorherigen Antwort bestätigt)
        # den gesamten String überprüfen soll (Full Match).

        # 2. Test gegen den passenden String (Struktur intakt)
        match_result = logic.match(generated_regex, matching_text)
        assert match_result is True, (
            f"FEHLGESCHLAGEN (Nested Match): Generated Regex:\n'{generated_regex_str}' "
            f"\n\tsollte matchen:\n'{matching_text}'"
        )

        # 3. Test gegen den NICHT passenden String (Struktur verletzt)
        non_match_result = logic.match(generated_regex, non_matching_text)
        assert non_match_result is False, (
            f"FEHLGESCHLAGEN (Nested Non-Match): Generated Regex:\n'{generated_regex_str}' "
            f"\n\tsollte NICHT matchen:\n'{non_matching_text}'"
        )


    @pytest.mark.parametrize(
    "filetype, source_text, matching_text_flexible, matching_text_whitespace, non_matching_text_invalid_tag", [
        # XML/HTML Flexibilität: Beliebige Attribute und Whitespace erlaubt
        (
                FileType.XML,
                '<user name="Max">1</user>',
                '<user id="123" name="Leo" data-info="test">99</user>',
                '< user \n id = "123" \n > \n 99 \n </ user >',
                '<user_tag id="123">1</user_tag>'
        ),
        # JSON Whitespace Flexibilität: Beliebige Leerzeichen erlaubt, Struktur fixiert
        (
                FileType.JSON,
                '{"attr1": [1, 2], "val": "a"}',
                '',
                '{   "attr1"  :  [ 99 , 88 ]  , "val" : "b" }',
                '{"attr1": [1, 2], "val_extra": "a"}'
        ),
        # CSV Whitespace Flexibilität: Beliebige Leerzeichen um Trennzeichen erlaubt
        (
                FileType.CSV,
                'col1,col2,col3\n1,2,3',
                '',
                ' col1 , col2 , col3 \n 1 , 2 , 3 ',
                'col1;col2;col3\n1;2;3'
        ),
        # HTML Flexibilität: Beliebige Attribute und Whitespace erlaubt
        (
                FileType.HTML,
                '<a href="/home">Home</a>',
                '<a id="link1" class="nav" href="/about" target="_blank">About Us</a>',
                '< a \n href = " /home " \n > \n Home \n </ a >',
                '<about href="/home">Home</about>'
        ),
        # XML (Kommentare und Processing Instructions): Sollte ignoriert werden
        (
                FileType.XML,
                '<!-- Comment --><root><item/></root>',
                '<?xml-stylesheet type="text/xsl" href="style.xsl"?><root><item/></root>',
                '< root > < item > ssd   </  item >    </  root >',
                '<root><item><extra/></item></root>'
        )
    ])
    def test_generated_regex_attribute_and_whitespace_flexibility(self, filetype, source_text, matching_text_flexible,
                                                              matching_text_whitespace, non_matching_text_invalid_tag):
        """
        Testet die Toleranz des generierten Regex:
        1. Bei XML/HTML: Akzeptanz beliebiger zusätzlicher Attribute.
        2. Bei allen: Toleranz gegenüber beliebigen Whitespace-Mengen.
        3. Ablehnung bei ungültigen Tag-Namen (XML/HTML) oder Keys (JSON).
        """

        # 1. Generiere das Regex
        try:
            generated_regex_str = logic.generate_regex(filetype=filetype, string=source_text)
            generated_regex = re.compile(generated_regex_str)
        except Exception as e:
            pytest.fail(f"Fehler bei der Regex-Generierung für {filetype.name} (Flexibility Test): {e}")

        # Test A: Flexible Attribute (Relevant für XML/HTML)
        # Wenn JSON, wird der Test übersprungen, da JSON keine Attribute hat.
        if filetype in [FileType.XML, FileType.HTML]:
            match_result_flex = logic.match(generated_regex, matching_text_flexible)
            assert match_result_flex is True, (
                f"FEHLGESCHLAGEN (Flex. Attributes): Regex sollte mit zusätzlichen Attributen matchen."
            )

        # Test B: Whitespace Flexibilität (Relevant für JSON, XML, HTML)
        match_result_ws = logic.match(generated_regex, matching_text_whitespace)
        assert match_result_ws is True, (
            f"FEHLGESCHLAGEN (Whitespace): Regex sollte mit variablem Whitespace matchen."
        )

        # Test C: Ungültige Struktur
        non_match_invalid_struct = logic.match(generated_regex, non_matching_text_invalid_tag)
        assert non_match_invalid_struct is False, (
            f"FEHLGESCHLAGEN (Invalid JSON Key): Regex sollte ungültigen Key ablehnen."
        )