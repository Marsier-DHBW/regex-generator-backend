import csv
import io
import re
from re import Pattern
from typing import Optional, Sequence

common_delimiters = [',', ';', '\t', '|', ':']
LINE_ENDING_PATTERN = r'(?:\r?\n)'


def csv_pattern(string: str) -> Pattern[str]:
    """
    Compiles a regex Pattern from example CSV content that can be used to
    validate whether another CSV has the same structure (same number of columns,
    same header names in the same order, and compatible quoting/delimiters).

    Args:
        string: example CSV content (must contain at least one line).

    Returns:
        re.Pattern compiled with DOTALL.
    """
    regex_pattern = __build_csv_regex(string)
    return re.compile(regex_pattern, re.DOTALL)


def __get_csv_field_pattern(delimiter: str, quotechar: Optional[str]) -> str:
    """
    Returns a regex fragment that matches a single CSV field given the delimiter
    and optional quote character.
    """
    esc_delimiter = re.escape(delimiter)

    if quotechar:
        esc_quotechar = re.escape(quotechar)
        # quoted field: optional surrounding whitespace, quote, any char except
        # quote (or escaped double quote sequences), closing quote, optional ws
        quoted_pattern = (
            rf'\s*{esc_quotechar}'
            rf'(?:[^{esc_quotechar}]|{esc_quotechar}{esc_quotechar})*'
            rf'{esc_quotechar}\s*'
        )
        # unquoted field: cannot contain delimiter or line breaks or quotechar
        unquoted_pattern = rf'\s*[^{esc_delimiter}{esc_quotechar}\r\n]*\s*'

        return rf'(?:{quoted_pattern}|{unquoted_pattern})'
    else:
        # no quotechar: just match up to delimiter or newline
        return rf'\s*[^{esc_delimiter}\r\n]*\s*'


def __get_header_pattern(header: Sequence[str], lock_delimiter: str, generic_field_pattern: str) -> str:
    """
    Builds a header line regex from a parsed header (sequence of field strings).

    For each header field we accept either the exact literal (possibly
    unquoted) or that literal inside single or double quotes. Empty header
    fields use the generic_field_pattern (they accept any valid field).

    The returned pattern is anchored at the start of the string (^).
    """
    # defensive: if header not a sequence, coerce to single-element list
    if not isinstance(header, (list, tuple)):
        header = [header]

    field_patterns = []

    delim = lock_delimiter.replace(r'\s*', '')
    if delim.startswith('\\'):
         delim = delim[1:]

    for value in header:
        if value is None:
            value = ''
        s = str(value)
        if s == '':
            field_patterns.append(generic_field_pattern)
            continue

        if delim and delim in s:
            parts = [part.strip() for part in s.split(delim)]
            escaped_parts = [re.escape(part) for part in parts]

            literal_pattern = lock_delimiter.join(escaped_parts)
            p = rf'(?:\s*"\s*{literal_pattern}\s*"\s*|\s*\'\s*{literal_pattern}\s*\'\s*)'
        else:
            literal_pattern = re.escape(s)
            p = rf'(?:\s*"\s*{literal_pattern}\s*"\s*|\s*\'\s*{literal_pattern}\s*\'\s*|\s*{literal_pattern}\s*)'

        field_patterns.append(p)

    header_row_pattern = lock_delimiter.join(field_patterns)
    return rf'^{header_row_pattern}'


def __infer_column_field_patterns(sample_rows: Sequence[Sequence[str]], num_columns: int,
                                  delimiter: str, quotechar: Optional[str],
                                  generic_field_pattern: str,
                                  header_parsed: Sequence[str], lock_delimiter: str) -> list:
    """
    Infer per-column regex field patterns from sample rows.

    Returns a list of regex fragments (one per column) that should be used
    to match data rows. Numeric-only columns receive a tighter pattern
    (allowing quoted or unquoted numeric values), otherwise the generic_field_pattern
    is used.
    """
    # normalize rows to num_columns (pad missing with empty strings)
    normalized_rows = []
    for r in sample_rows:
        # ensure we operate on a mutable list
        rlist = list(r)
        if len(rlist) < num_columns:
            rlist.extend([''] * (num_columns - len(rlist)))
        elif len(rlist) > num_columns:
            rlist = rlist[:num_columns]
        normalized_rows.append(rlist)

    # helper to detect numeric strings (integers or decimals, optional sign)
    num_re = re.compile(r'^[+-]?\d+(?:\.\d+)?$')

    col_field_patterns: list[str] = []
    esc_quote = re.escape(quotechar) if quotechar else None

    # raw delimiter char for splitting composite fields
    raw_delim = delimiter

    for ci in range(num_columns):
        values = [row[ci].strip() if row[ci] is not None else '' for row in normalized_rows]
        non_empty = [v for v in values if v != '']
        # If header for this column is composite (contains the delimiter),
        # split the cell values by delimiter and infer per-subfield types.
        header_val = header_parsed[ci] if ci < len(header_parsed) else ''
        if header_val and raw_delim in header_val:
            # number of subfields determined by header literal
            sub_count = len([p for p in header_val.split(raw_delim)])

            # collect subfield values per position
            sub_values: list[list[str]] = [[] for _ in range(sub_count)]
            for v in values:
                parts = [p.strip() for p in v.split(raw_delim)] if v != '' else []
                # normalize parts to sub_count
                if len(parts) < sub_count:
                    parts = parts + [''] * (sub_count - len(parts))
                elif len(parts) > sub_count:
                    parts = parts[:sub_count]
                for si, pv in enumerate(parts):
                    sub_values[si].append(pv)

            # infer each subfield type and build subpatterns
            sub_patterns: list[str] = []
            for sv in sub_values:
                non_empty_sub = [x for x in sv if x != '']
                if not non_empty_sub:
                    subtype = 'mixed'
                else:
                    num_count = sum(1 for x in non_empty_sub if num_re.fullmatch(x))
                    if num_count == len(non_empty_sub):
                        subtype = 'numeric'
                    elif num_count == 0:
                        subtype = 'string'
                    else:
                        subtype = 'mixed'

                if subtype == 'numeric':
                    num_inner = r'[+-]?\d+(?:\.\d+)?'
                    # when inside composite, subvalues are not individually quoted,
                    # so use unquoted-style inner that forbids delimiter/newline
                    sub_patterns.append(rf'\s*{num_inner}\s*')
                else:
                    # allow any chars except delimiter/newline for unquoted subvalues
                    esc_delim = re.escape(delimiter)
                    sub_patterns.append(rf'\s*[^{esc_delim}\r\n]*\s*')

            # join subpatterns with lock_delimiter to allow flexible spacing
            inner_pattern = lock_delimiter.join(sub_patterns)

            if esc_quote:
                quoted_pattern = rf'\s*{esc_quote}{inner_pattern}{esc_quote}\s*'
                unquoted_pattern = rf'\s*{inner_pattern}\s*'
                col_field_patterns.append(rf'(?:{quoted_pattern}|{unquoted_pattern})')
            else:
                col_field_patterns.append(rf'\s*{inner_pattern}\s*')
        else:
            # non-composite: infer single-field numeric/string/mixed
            if not non_empty:
                ctype = 'mixed'
            else:
                numeric_count = sum(1 for v in non_empty if num_re.fullmatch(v))
                if numeric_count == len(non_empty):
                    ctype = 'numeric'
                elif numeric_count == 0:
                    ctype = 'string'
                else:
                    ctype = 'mixed'

            if ctype == 'numeric':
                # allow quoted numeric or unquoted numeric (with optional surrounding ws)
                num_inner = r'[+-]?\d+(?:\.\d+)?'
                if esc_quote:
                    quoted_pattern = rf'\s*{esc_quote}{num_inner}{esc_quote}\s*'
                    unquoted_pattern = rf'\s*{num_inner}\s*'
                    col_field_patterns.append(rf'(?:{quoted_pattern}|{unquoted_pattern})')
                else:
                    col_field_patterns.append(rf'\s*{num_inner}\s*')
            else:
                # string or mixed: use the generic field pattern (already allows quoted/unquoted)
                col_field_patterns.append(generic_field_pattern)

    return col_field_patterns


def __build_csv_regex(example_csv_content: str) -> str:
    """
    Create a regex that matches CSV files with the same header and column count
    as `example_csv_content`.

    Strategy:
    - Use csv.Sniffer to detect delimiter/quotechar where possible.
    - Parse the first row (header) using csv.reader to obtain header names.
    - Build a generic field pattern and a header-specific pattern, then build
      a row pattern for subsequent data rows.
    """
    if example_csv_content is None:
        raise ValueError("example_csv_content must not be None")

    stripped_content = example_csv_content.strip()
    if not stripped_content:
        raise ValueError("Input CSV content cannot be empty.")

    lines = stripped_content.splitlines()
    sample = '\n'.join(lines[:2]) if len(lines) >= 2 else lines[0]

    # detect dialect
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=''.join(common_delimiters))
        delimiter = dialect.delimiter
        quotechar = dialect.quotechar if dialect.quoting != csv.QUOTE_NONE else None
    except Exception:
        # fallback: try sniffing only first line
        try:
            delimiter = csv.Sniffer().sniff(lines[0], delimiters=''.join(common_delimiters)).delimiter
            quotechar = '"'
        except Exception:
            delimiter = ','
            quotechar = '"'

    if delimiter not in stripped_content:
        # If sniff failed and delimiter not actually in content, fallback to comma
        delimiter = ','

    # Parse header
    reader = csv.reader(io.StringIO(stripped_content), delimiter=delimiter, quotechar=quotechar,
                        doublequote=True, skipinitialspace=True)

    header_parsed = None
    try:
        header_parsed = next(reader)
        num_columns = len(header_parsed)
    except (StopIteration, csv.Error):
        # fallback: count delimiter occurrences
        try:
            first_line = stripped_content.splitlines()[0]
            num_columns = first_line.count(delimiter) + 1
        except Exception:
            return ""

    if num_columns == 0:
        return ""

    if header_parsed is None:
        # create generic header placeholders
        header_parsed = [''] * num_columns

    # lock_delimiter matches the delimiter with optional surrounding whitespace
    lock_delimiter = rf'\s*{re.escape(delimiter)}\s*'

    generic_field_pattern = __get_csv_field_pattern(delimiter, quotechar)

    header_row_pattern_content = lock_delimiter.join([generic_field_pattern] * num_columns)

    header_pattern = __get_header_pattern(header_parsed, lock_delimiter, generic_field_pattern)

    # Collect sample rows (remaining rows from reader) to infer column types
    sample_rows = []
    try:
        for r in reader:
            sample_rows.append(r)
    except csv.Error:
        # if parsing later rows fails, proceed with whatever we have
        pass

    # infer per-column patterns using helper
    col_field_patterns = __infer_column_field_patterns(sample_rows, num_columns,
                                                      delimiter, quotechar,
                                                      generic_field_pattern,
                                                      header_parsed, lock_delimiter)

    # build row pattern using per-column patterns for data rows
    data_row_pattern_content = lock_delimiter.join(col_field_patterns)
    row_pattern = rf'\s*{data_row_pattern_content}\s*'

    final_regex = (
        f'{header_pattern}'
        f'(?:{LINE_ENDING_PATTERN}{row_pattern})*'
        f'(?:{LINE_ENDING_PATTERN})?$'
    )

    return final_regex


# quick manual test when run directly
if __name__ == '__main__':
    source_text = 'ID,"Name, Titel",Age\n1,"Max Mustermann, CEO",30'
    structure_regex_complex = __build_csv_regex(source_text)
    print('Generated regex:')
    print(structure_regex_complex)
    # example match
    matching_text = 'ID,"Name, Titel",Age\n2,"Erika Mustermann, CTO",45'
    compiled = csv_pattern(source_text)
    print('Matches example structure:', bool(compiled.fullmatch(matching_text)))
