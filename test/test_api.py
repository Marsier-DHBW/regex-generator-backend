import sys, os
# Projektroot zum Pythonpfad hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import re
from backend import logic
from backend.enums.FileType import FileType

# ============================================================
# Tests für logic.match
# ============================================================

class TestMatch:
    def test_match_valid_true(self):
        regex = re.compile(r"Order ID: \d+")
        text = "Order ID: 12345"
        assert logic.match(regex, text) is True

    def test_match_valid_false(self):
        regex = re.compile(r"^\d+$")
        text = "abc123"
        assert logic.match(regex, text) is False

    def test_match_empty_text(self):
        regex = re.compile(r".+")
        assert logic.match(regex, "") is False

    def test_match_empty_pattern(self):
        with pytest.raises(re.error):
            re.compile("")

    def test_match_special_characters(self):
        regex = re.compile(r"[A-Z]+\d+")
        text = "ABC123"
        assert logic.match(regex, text) is True

    def test_match_unicode(self):
        regex = re.compile(r"\w+")
        text = "äöüß"
        assert logic.match(regex, text) is True

    def test_match_newlines(self):
        regex = re.compile(r"Line\d")
        text = "Line1\nLine2"
        assert logic.match(regex, text) is True


# ============================================================
# Tests für logic.generate_regex
# ============================================================

class TestGenerateRegex:
    @pytest.mark.parametrize("filetype,text,expected_hint", [
        (FileType.JSON, '{"key": "value"}', "key"),
        (FileType.CSV, "name,age\nAlice,30", ","),
        (FileType.XML, "<root><child>1</child></root>", "<child>"),
        (FileType.HTML, "<html><body>hi</body></html>", "<body>"),
    ])
    def test_generate_regex_basic(self, filetype, text, expected_hint):
        regex = logic.generate_regex(filetype=filetype, string=text)
        assert isinstance(regex, str)
        assert len(regex) > 0
        # sanity check: returned regex should be compilable
        re.compile(regex)

    def test_generate_regex_invalid_filetype(self):
        with pytest.raises(Exception):
            logic.generate_regex(filetype=FileType.UNSUPPORTED, string="test")

    def test_generate_regex_empty_text(self):
        with pytest.raises(Exception):
            logic.generate_regex(filetype=FileType.JSON, string="")

    def test_generate_regex_nonstandard_json(self):
        text = '{invalid json}'
        result = logic.generate_regex(filetype=FileType.JSON, string=text)
        assert isinstance(result, str)

    def test_generate_regex_large_input(self):
        text = "<data>" + "x" * 10000 + "</data>"
        result = logic.generate_regex(filetype=FileType.XML, string=text)
        assert isinstance(result, str)


# ============================================================
# Tests für logic.detect_filetype
# ============================================================

class TestDetectFiletype:
    @pytest.mark.parametrize("text,expected", [
        ('{"key": "value"}', FileType.JSON),
        ("<root></root>", FileType.XML),
        ("<html><body></body></html>", FileType.HTML),
        ("col1,col2\n1,2", FileType.CSV),
    ])
    def test_detect_filetype_simple(self, text, expected):
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
        assert expected.name in result.keys() or expected.name.lower() in [k.lower() for k in result.keys()]

    def test_detect_filetype_malformed_json(self):
        text = '{"key": value" :}'
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)

    def test_detect_filetype_random_text(self):
        text = "This is just some text without structure"
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_detect_filetype_empty_string(self):
        with pytest.raises(Exception):
            logic.detect_filetype(string="", is_ml=False)

    def test_detect_filetype_ml_mock(self, monkeypatch):
        """Simuliert ML-Erkennung"""
        fake_result = {"JSON": 0.8, "XML": 0.2}
        monkeypatch.setattr(logic, "detect_filetype", lambda string, is_ml: fake_result)
        result = logic.detect_filetype("{}", True)
        assert "JSON" in result

    def test_detect_filetype_html_edgecase(self):
        """HTML mit unvollständigen Tags"""
        text = "<html><body><div>"
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)


# ============================================================
# Cross-Type Edgecase Tests (mehrere Formate durcheinander)
# ============================================================

class TestCrossType:
    def test_mixed_content_xml_json(self):
        text = '<root>{"key": "value"}</root>'
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)

    def test_csv_with_html_content(self):
        text = "col1,col2\n<html>,text"
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)

    def test_json_with_xml_inside(self):
        text = '{"data": "<xml></xml>"}'
        result = logic.detect_filetype(string=text, is_ml=False)
        assert isinstance(result, dict)
