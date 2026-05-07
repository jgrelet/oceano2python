import argparse
import csv
import re
from pathlib import Path


GLOBAL_TEMPLATE = """[global]
author = "TODO"
codeRoscop = 'code_roscop.csv'
defaultEncoding = "ISO-8859-1"
ASCII = "ascii"
NETCDF = "netcdf"
odv = "odv"
title = ''
history = ''
institution = 'TODO'
source = ''
comment = ''
references = ''

[cruise]
CYCLEMESURE = "TODO"
PLATEFORME = "TODO"
callsign = "TODO"
INSTITUTE = "TODO"
TIMEZONE = "GMT"
BEGINDATE = "TODO"
ENDDATE = "TODO"
PI = "TODO"
CREATOR = "TODO"
"""


VALUE_PATTERNS = {
    "DATETIME_TEXT": re.compile(r"([A-Za-z]{3,})\s+(\d{1,2})\s+(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})"),
    "DATETIME_ISO": re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})[T\s](\d{1,2}):(\d{2}):(\d{2})"),
    "DATE_DMY": re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})"),
    "DATE_YMD": re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"),
    "TIME": re.compile(r"(\d{1,2}):(\d{2}):(\d{2})(?:\.\d+)?"),
    "LAT_DDM_SUFFIX": re.compile(r"(\d{1,3})\s+(\d{1,2}(?:[.,]\d+)?)\s+([NS])"),
    "LON_DDM_SUFFIX": re.compile(r"(\d{1,3})\s+(\d{1,2}(?:[.,]\d+)?)\s+([EW])"),
    "LAT_DDM_PREFIX": re.compile(r"([NS])\s+(\d{1,3})\D+\s*(\d{1,2}(?:[.,]\d+)?)(?:')?"),
    "LON_DDM_PREFIX": re.compile(r"([EW])\s+(\d{1,3})\D+\s*(\d{1,2}(?:[.,]\d+)?)(?:')?"),
    "LAT_DDMM": re.compile(r"(\d{2})(\d{2}\.\d+),([NS])"),
    "LON_DDMM": re.compile(r"(\d{3})(\d{2}\.\d+),([EW])"),
    "LAT_DECIMAL": re.compile(r"([-+]?\d+(?:\.\d+)?)"),
    "LON_DECIMAL": re.compile(r"([-+]?\d+(?:\.\d+)?)"),
}


ROSCOP_ALIASES = [
    ("PRES", ("pressure", "press", "prdm", "dbar")),
    ("DEPTH", ("depth", "depsm", "z")),
    ("TEMP", ("temperature", "temp", "t090c")),
    ("TE01", ("temperature", "temp", "t090c")),
    ("TE02", ("temperature, 2", "temp, 2", "t190c")),
    ("PSAL", ("salinity", "sal00", "sal")),
    ("PSA1", ("salinity", "sal00")),
    ("PSA2", ("salinity, 2", "sal11")),
    ("DENS", ("density", "sigma", "dens")),
    ("SVEL", ("sound velocity", "celerite", "svcm")),
    ("EWCT", ("eastward", "ewct")),
    ("NSCT", ("northward", "nsct")),
    ("DOX2", ("oxygen", "optode")),
    ("FLU2", ("fluorescence", "chlorophyll", "algue verte")),
    ("FLU3", ("fluorescence", "algue bleue", "diatomees")),
    ("TUR3", ("turbid", "seapoint")),
    ("SSJT", ("sbe3s temp", "peak av", "jacket")),
    ("SSTP", ("sbe21 temp", "sbe45 temp", "temp eau", "surface temp")),
    ("SSPS", ("salinite", "salinity", "sbe21 sal", "sbe45 sal")),
    ("WMSP", ("vent vrai", "wind speed")),
    ("WDIR", ("dir. vent vrai", "wind direction")),
    ("ATMS", ("pression", "pression (mbar)", "air pressure")),
    ("RELH", ("humidite",)),
    ("DRYT", ("temp. air", "air temp")),
    ("BOTL", ("bottle", "botl")),
]


def escape_toml_string(value):
    return value.replace("\\", "\\\\").replace("'", "\\'")


def escape_regex_fragment(text):
    escaped = re.escape(text.strip())
    escaped = escaped.replace(r"\ ", r"\s+")
    escaped = escaped.replace(r"\=", r"\s*=\s*")
    escaped = escaped.replace(r"\:", r"\s*:\s*")
    return escaped


def is_number(token):
    token = token.strip()
    if not token:
        return False
    token = token.replace(",", ".")
    try:
        float(token)
        return True
    except ValueError:
        return False


def split_line(line, separator):
    if separator is None:
        return line.strip().split()
    return [item.strip() for item in line.rstrip("\n").split(separator)]


def read_roscop_codes(path):
    codes = set()
    with open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            code = row["key"]
            if code and code != "string":
                codes.add(code)
    return codes


def detect_separator(lines):
    data_like_lines = [line for line in lines if looks_like_data_row(line, None)]
    if data_like_lines:
        sample = data_like_lines[0]
        if sample.count("\t") >= 2:
            return "\t"
        if sample.count(",") >= 2:
            return ","
        if sample.count(";") >= 2:
            return ";"
        return None
    if any(line.count("\t") >= 2 for line in lines):
        return "\t"
    comma_scores = [line.count(",") for line in lines if line.strip()]
    semi_scores = [line.count(";") for line in lines if line.strip()]
    if comma_scores and max(comma_scores) >= 2:
        return ","
    if semi_scores and max(semi_scores) >= 2:
        return ";"
    return None


def detect_separator_from_line(line):
    if line.count("\t") >= 2:
        return "\t"
    if line.count(",") >= 2:
        return ","
    if line.count(";") >= 2:
        return ";"
    return None


def looks_like_data_row(line, separator):
    tokens = split_line(line, separator)
    if len(tokens) < 2:
        return False
    numeric_count = sum(1 for token in tokens if is_number(token))
    return numeric_count / len(tokens) >= 0.6


def detect_data_start(lines, separator):
    for index, line in enumerate(lines):
        if looks_like_data_row(line, separator):
            return index
    return None


def detect_table_header_line(lines, separator, data_start_index):
    if data_start_index is None:
        return None
    candidate_index = data_start_index - 1
    while candidate_index >= 0 and not lines[candidate_index].strip():
        candidate_index -= 1
    if candidate_index < 0:
        return None
    candidate_tokens = split_line(lines[candidate_index], separator)
    if not candidate_tokens:
        return None
    if all(not is_number(token) for token in candidate_tokens) and len(candidate_tokens) == len(split_line(lines[data_start_index], separator)):
        if candidate_index - 1 >= 0:
            previous_tokens = split_line(lines[candidate_index - 1], separator)
            if previous_tokens and len(previous_tokens) == len(candidate_tokens) and all(not is_number(token) for token in previous_tokens):
                return candidate_index - 1
        return candidate_index
    return None


def detect_end_header_line(lines, data_start_index):
    if data_start_index is None:
        return None
    for index in range(max(0, data_start_index - 6), data_start_index):
        stripped = lines[index].strip()
        if not stripped:
            continue
        if "END_OF_HEADER" in stripped or stripped == "*END*" or stripped.startswith("Columns"):
            return index
    return None


def find_explicit_end_header(lines):
    for index, line in enumerate(lines):
        stripped = line.strip()
        if "END_OF_HEADER" in stripped or stripped == "*END*" or stripped.startswith("Columns"):
            return index
    return None


def find_labeled_match(lines, field_name):
    detectors = {
        "DATETIME": ("DATETIME_TEXT", "DATETIME_ISO"),
        "DATE": ("DATE_DMY", "DATE_YMD"),
        "TIME": ("TIME",),
        "LATITUDE": ("LAT_DDM_SUFFIX", "LAT_DDM_PREFIX", "LAT_DDMM", "LAT_DECIMAL"),
        "LONGITUDE": ("LON_DDM_SUFFIX", "LON_DDM_PREFIX", "LON_DDMM", "LON_DECIMAL"),
        "station": (),
        "BATH": (),
    }
    if field_name == "station":
        for line in lines:
            if re.search(r"station", line, re.IGNORECASE):
                return r"Station\s*:\s*\D*(\d*)"
        return None
    if field_name == "BATH":
        for line in lines:
            if re.search(r"bottom depth|sonde", line, re.IGNORECASE):
                return r"Bottom\s+Depth\s*\(?(?:m)?\)?\s*[:=]\s*(\d*\.?\d+)"
        return None

    for line in lines:
        for pattern_name in detectors[field_name]:
            match = VALUE_PATTERNS[pattern_name].search(line)
            if not match:
                continue
            prefix = line[:match.start()]
            prefix = re.sub(r"^[^A-Za-z0-9]+", "", prefix)
            if field_name == "TIME" and not re.search(r"time|heure|hour", prefix, re.IGNORECASE):
                continue
            if field_name in ("LATITUDE", "LONGITUDE") and not re.search(field_name[:3], prefix, re.IGNORECASE):
                if pattern_name in ("LAT_DECIMAL", "LON_DECIMAL"):
                    continue
            if not prefix and field_name != "TIME":
                continue
            prefix_regex = escape_regex_fragment(prefix)
            if pattern_name == "DATETIME_TEXT":
                return f"{prefix_regex}(\\w+)\\s+(\\d+)\\s+(\\d+)\\s+(\\d+):(\\d+):(\\d+)"
            if pattern_name == "DATETIME_ISO":
                return f"{prefix_regex}(\\d+)-(\\d+)-(\\d+)[T\\s](\\d+):(\\d+):(\\d+)"
            if pattern_name == "DATE_DMY":
                return f"{prefix_regex}(\\d+)/(\\d+)/(\\d+)"
            if pattern_name == "DATE_YMD":
                separator = "-" if "-" in match.group(0) else "/"
                return f"{prefix_regex}(\\d+){re.escape(separator)}(\\d+){re.escape(separator)}(\\d+)"
            if pattern_name == "TIME":
                return f"{prefix_regex}(\\d+)[:hH](\\d+):(\\d+)"
            if pattern_name in ("LAT_DDM_SUFFIX", "LON_DDM_SUFFIX"):
                return f"{prefix_regex}(\\d+)\\s+(\\d+[\\.,]\\d+)\\s+(\\w)"
            if pattern_name in ("LAT_DDM_PREFIX", "LON_DDM_PREFIX"):
                return f"{prefix_regex}([NSEW])\\s+(\\d+)\\D+\\s*(\\d+[\\.,]\\d+)"
            if pattern_name == "LAT_DDMM":
                return f"{prefix_regex}(\\d{{2}})(\\d{{2}}\\.\\d+),(\\w)"
            if pattern_name == "LON_DDMM":
                return f"{prefix_regex}(\\d{{3}})(\\d{{2}}\\.\\d+),(\\w)"
            if pattern_name in ("LAT_DECIMAL", "LON_DECIMAL"):
                return f"{prefix_regex}([-+]?\\d+\\.\\d+)"
    return None


def find_value_pattern(value, field_name):
    ordered_patterns = {
        "DATE": ("DATE_YMD", "DATE_DMY"),
        "TIME": ("TIME",),
        "LATITUDE": ("LAT_DDM_PREFIX", "LAT_DDM_SUFFIX", "LAT_DDMM", "LAT_DECIMAL"),
        "LONGITUDE": ("LON_DDM_PREFIX", "LON_DDM_SUFFIX", "LON_DDMM", "LON_DECIMAL"),
    }
    for pattern_name in ordered_patterns[field_name]:
        match = VALUE_PATTERNS[pattern_name].fullmatch(value.strip())
        if not match:
            continue
        if pattern_name == "DATE_YMD":
            separator = "-" if "-" in value else "/"
            return f"(\\d+){re.escape(separator)}(\\d+){re.escape(separator)}(\\d+)", "%Y-%m-%d %H:%M:%S"
        if pattern_name == "DATE_DMY":
            return r"(\d+)/(\d+)/(\d+)", "%d/%m/%Y %H:%M:%S"
        if pattern_name == "TIME":
            return r"(\d+):(\d+):(\d+)", None
        if pattern_name in ("LAT_DDM_PREFIX", "LON_DDM_PREFIX"):
            symbol = "°" if "°" in value else r"\D+"
            return rf"([NSEW])\s+(\d+){symbol}\s*(\d+[\,\.]\d+)'?", None
        if pattern_name in ("LAT_DDM_SUFFIX", "LON_DDM_SUFFIX"):
            return r"(\d+)\s+(\d+\.\d+)\s+(\w)", None
        if pattern_name == "LAT_DDMM":
            return r"(\d{2})(\d{2}\.\d+),(\w)", None
        if pattern_name == "LON_DDMM":
            return r"(\d{3})(\d{2}\.\d+),(\w)", None
        if pattern_name in ("LAT_DECIMAL", "LON_DECIMAL"):
            return r"([-+]?\d+\.\d+)", None
    return None, None


def station_regex_from_filenames(paths):
    stems = [Path(path).stem for path in paths]
    if not stems:
        return r"(\d+)"
    stem = stems[0]
    match = re.search(r"(.*?)(\d{3})$", stem)
    if match:
        prefix = re.escape(match.group(1))
        return f"{prefix}(\\d{{3}})"
    match = re.search(r"(.*?)(\d+)$", stem)
    if match:
        prefix = re.escape(match.group(1))
        return f"{prefix}(\\d+)"
    return r"(\d+)"


def find_column_definitions(lines):
    definitions = []
    for line in lines:
        match = re.search(r"name\s+(\d+)\s*=\s*([^:]+):\s*(.*)", line, re.IGNORECASE)
        if match:
            index = int(match.group(1))
            short_name = match.group(2).strip()
            description = match.group(3).strip()
            definitions.append((index, short_name, description))
    return definitions


def score_alias(label):
    normalized = re.sub(r"[^a-z0-9]+", " ", label.lower()).strip()
    matches = []
    exact_tokens = set(normalized.split())
    if exact_tokens == {"u"}:
        return ["EWCT"]
    if exact_tokens == {"v"}:
        return ["NSCT"]
    if exact_tokens == {"z"}:
        return ["DEPTH"]
    for key, aliases in ROSCOP_ALIASES:
        if any(alias in normalized for alias in aliases):
            matches.append(key)
    return matches


def suggest_split_entries(column_candidates, known_codes):
    assignments = []
    comments = []
    review_items = []
    used = set()

    for index, label in column_candidates:
        suggestions = [code for code in score_alias(label) if code in known_codes]
        suggestions = [code for code in suggestions if code not in ("LATITUDE", "LONGITUDE", "TIME", "DAYD")]
        unique_suggestions = []
        for code in suggestions:
            if code not in unique_suggestions:
                unique_suggestions.append(code)
        if len(unique_suggestions) == 1 and unique_suggestions[0] not in used:
            code = unique_suggestions[0]
            assignments.append((code, index))
            used.add(code)
        elif unique_suggestions:
            choices = ", ".join(unique_suggestions)
            comments.append(f"# {index} = {label} -> possible: {choices}")
            review_items.append(
                {"index": index, "label": label, "suggestions": unique_suggestions}
            )
        else:
            comments.append(f"# {index} = {label}")
    return assignments, comments, review_items


def interactive_review_split_entries(
    assignments,
    review_items,
    known_codes,
    input_fn=input,
    output_fn=print,
):
    chosen = list(assignments)
    assigned_codes = {code for code, _ in chosen}

    if review_items:
        output_fn("Interactive split review:")
        output_fn("Press Enter or type 's' to skip, or enter a ROSCOP code to keep.")

    for item in review_items:
        suggestions = ", ".join(item["suggestions"])
        prompt = f"Column {item['index']} = {item['label']} [{suggestions}] : "
        while True:
            response = input_fn(prompt).strip().upper()
            if response in ("", "S", "SKIP"):
                break
            if response not in known_codes:
                output_fn(f"Unknown ROSCOP code: {response}")
                continue
            if response in assigned_codes:
                output_fn(f"{response} is already assigned. Choose another code or skip.")
                continue
            chosen.append((response, item["index"]))
            assigned_codes.add(response)
            break

    output_fn("Optional manual mappings: type '<column_index> <ROSCOP_CODE>' or press Enter to finish.")
    while True:
        response = input_fn("Add mapping: ").strip()
        if not response:
            break
        parts = response.split()
        if len(parts) != 2:
            output_fn("Expected format: <column_index> <ROSCOP_CODE>")
            continue
        index_text, code = parts
        code = code.upper()
        if not index_text.isdigit():
            output_fn("Column index must be an integer.")
            continue
        if code not in known_codes:
            output_fn(f"Unknown ROSCOP code: {code}")
            continue
        if code in assigned_codes:
            output_fn(f"{code} is already assigned.")
            continue
        chosen.append((code, int(index_text)))
        assigned_codes.add(code)

    return sorted(chosen, key=lambda item: item[1])


class ConfigTemplateBuilder:
    def __init__(
        self,
        paths,
        instrument,
        roscop_path="code_roscop.csv",
        interactive=False,
        input_fn=input,
        output_fn=print,
    ):
        self.paths = [str(path) for path in paths]
        self.instrument = instrument.lower()
        self.known_codes = read_roscop_codes(roscop_path)
        self.interactive = interactive
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.lines = self._read_lines(self.paths[0])
        explicit_end_header_index = find_explicit_end_header(self.lines)
        if explicit_end_header_index is not None:
            trailing_lines = self.lines[explicit_end_header_index + 1 :]
            relative_index = detect_data_start(trailing_lines, None)
            if relative_index is not None:
                self.data_start_index = explicit_end_header_index + 1 + relative_index
            else:
                self.data_start_index = detect_data_start(self.lines, None)
        else:
            self.data_start_index = detect_data_start(self.lines, None)
        self.separator = None
        if self.data_start_index is not None:
            self.separator = detect_separator_from_line(self.lines[self.data_start_index])
            if self.separator is not None:
                self.data_start_index = detect_data_start(self.lines, self.separator)
        if self.separator is None and self.data_start_index is None:
            self.separator = detect_separator(self.lines)
        self.table_header_index = detect_table_header_line(self.lines, self.separator, self.data_start_index)
        self.end_header_index = detect_end_header_line(self.lines, self.data_start_index)
        self.header_lines = self.lines[: self.data_start_index] if self.data_start_index is not None else self.lines
        self.data_line = self.lines[self.data_start_index] if self.data_start_index is not None else ""
        self.comments = []

    def _read_lines(self, path):
        with open(path, "rt", encoding="ISO-8859-1") as handle:
            return handle.readlines()[:800]

    def _detect_date_time_format(self):
        sample_lines = self.header_lines + ([self.data_line] if self.data_line else [])
        for line in sample_lines:
            if VALUE_PATTERNS["DATETIME_ISO"].search(line):
                return "%Y-%m-%d %H:%M:%S"
            if VALUE_PATTERNS["DATE_DMY"].search(line):
                return "%d/%m/%Y %H:%M:%S"
            if VALUE_PATTERNS["DATE_YMD"].search(line):
                return "%Y/%m/%d %H:%M:%S"
            if VALUE_PATTERNS["DATETIME_TEXT"].search(line):
                return "%d/%b/%Y %H:%M:%S"
        return None

    def _render_header_section(self):
        lines = [f"\t[{self.instrument}.header]"]
        header_search_lines = self.header_lines
        if self.table_header_index == 0:
            header_search_lines = []
        if self.end_header_index is not None:
            end_header = self.lines[self.end_header_index].strip()
            if end_header == "*END*":
                lines.append("\tendHeader = '^[*]END[*]'")
            else:
                lines.append(f"\tendHeader = '^{escape_toml_string(re.escape(end_header))}$'")
        else:
            if any(line.lstrip().startswith(("*", "#")) for line in header_search_lines):
                lines.append("\tisHeader = '^[*#]+\\s+'")
            is_data_marker = self._detect_is_data_marker()
            if is_data_marker:
                lines.append(f"\tisData = '{escape_toml_string(is_data_marker)}'")
        header_keys = ["station", "DATETIME", "DATE", "TIME", "LATITUDE", "LONGITUDE", "BATH"]
        if find_labeled_match(header_search_lines, "DATETIME"):
            header_keys = [key for key in header_keys if key not in ("DATE", "TIME")]
        for key in header_keys:
            regex = find_labeled_match(header_search_lines, key)
            if regex:
                lines.append(f"\t{key} = '{escape_toml_string(regex)}'")
        return lines

    def _detect_is_data_marker(self):
        if self.table_header_index != 0 or self.data_start_index is None:
            return None
        header_tokens = split_line(self.lines[self.table_header_index], self.separator)
        data_tokens = split_line(self.lines[self.data_start_index], self.separator)
        for index, token in enumerate(header_tokens):
            if index >= len(data_tokens):
                continue
            if token.strip().lower() == "type":
                value = data_tokens[index].strip()
                if re.fullmatch(r"[A-Z0-9_+-]{4,}", value):
                    return re.escape(value)
        return None

    def _render_format_section(self):
        if self.table_header_index is None:
            return []
        header_tokens = split_line(self.lines[self.table_header_index], self.separator)
        data_tokens = split_line(self.lines[self.data_start_index], self.separator)
        format_lines = [f"\t[{self.instrument}.format]"]
        date_time_format = None
        datetime_index = None
        for index, token in enumerate(header_tokens):
            normalized = token.lower().strip()
            if normalized == "date" and index < len(data_tokens):
                if VALUE_PATTERNS["DATETIME_ISO"].fullmatch(data_tokens[index].strip()):
                    datetime_index = index
                    break
        if datetime_index is not None:
            format_lines.append("\tDATE = '(\\d+)-(\\d+)-(\\d+)'")
            format_lines.append("\tTIME = '(\\d+):(\\d+):(\\d+)'")
            date_time_format = "%Y-%m-%d %H:%M:%S"
        for field_name, matcher in (("DATE", ("date",)), ("TIME", ("time",)), ("LATITUDE", ("lat",)), ("LONGITUDE", ("lon",))):
            if field_name in ("DATE", "TIME") and datetime_index is not None:
                continue
            field_index = None
            for index, token in enumerate(header_tokens):
                if any(hint in token.lower() for hint in matcher):
                    field_index = index
                    break
            if field_index is None or field_index >= len(data_tokens):
                continue
            regex, suggested_format = find_value_pattern(data_tokens[field_index], field_name)
            if regex:
                format_lines.append(f"\t{field_name} = '{escape_toml_string(regex)}'")
            if suggested_format and date_time_format is None:
                date_time_format = suggested_format
        if len(format_lines) == 1:
            return []
        return format_lines, date_time_format

    def _column_candidates(self):
        definitions = find_column_definitions(self.header_lines)
        if definitions:
            candidates = [(index, f"{short_name}: {description}") for index, short_name, description in definitions]
            return candidates
        if self.table_header_index is not None:
            header_tokens = split_line(self.lines[self.table_header_index], self.separator)
            return list(enumerate(header_tokens))
        if self.end_header_index is not None and self.end_header_index >= 0:
            maybe_columns = self.lines[self.end_header_index].strip()
            if ":" in maybe_columns and "Columns" in maybe_columns:
                tokens = maybe_columns.split("=", 1)[1].split(":")
                return list(enumerate(token.strip() for token in tokens))
        return []

    def build(self):
        output = [
            "# Generated template from sample file(s).",
            "# Review every regex and split index before using this configuration in production.",
            f"# Sample files: {', '.join(Path(path).name for path in self.paths)}",
            "",
            GLOBAL_TEMPLATE.rstrip(),
            "",
            f"[{self.instrument}]",
            f"station = '{escape_toml_string(station_regex_from_filenames(self.paths))}'",
            'titleSummary = "TODO"',
            'typeInstrument = "TODO"',
            'instrumentNumber = "TODO"',
        ]

        if self.separator == "\t":
            output.append('separator = "\\t"')
        elif self.separator in (",", ";"):
            output.append(f'separator = "{self.separator}"')

        detected_date_time_format = self._detect_date_time_format()
        if detected_date_time_format:
            output.append(f'dateTimeFormat = "{detected_date_time_format}"')

        output.append("")
        output.extend(self._render_header_section())

        format_result = self._render_format_section()
        if format_result:
            format_lines, format_date_time = format_result
            if format_date_time and not detected_date_time_format:
                insert_at = output.index("")
                output.insert(insert_at, f'dateTimeFormat = "{format_date_time}"')
            output.append("")
            output.extend(format_lines)

        column_candidates = self._column_candidates()
        assignments, comments, review_items = suggest_split_entries(column_candidates, self.known_codes)
        if self.interactive:
            assignments = interactive_review_split_entries(
                assignments,
                review_items,
                self.known_codes,
                self.input_fn,
                self.output_fn,
            )
        output.append("")
        output.append(f"\t[{self.instrument}.split]")
        output.append("\t# column start at 0")
        for comment in comments:
            output.append(f"\t{comment}")
        for key, index in assignments:
            output.append(f"\t{key} = {index}")

        if not assignments:
            output.append("\t# TODO: map one or more data columns to ROSCOP variables.")

        output.append("")
        return "\n".join(output)


def build_template(
    paths,
    instrument,
    roscop_path="code_roscop.csv",
    interactive=False,
    input_fn=input,
    output_fn=print,
):
    builder = ConfigTemplateBuilder(
        paths,
        instrument,
        roscop_path,
        interactive=interactive,
        input_fn=input_fn,
        output_fn=output_fn,
    )
    return builder.build()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a commented TOML template from one or more sample ASCII files."
    )
    parser.add_argument("files", nargs="+", help="Sample file(s) used to infer a TOML template")
    parser.add_argument("-i", "--instrument", required=True, help="Instrument name, for example CTD or CASINO")
    parser.add_argument("-r", "--roscop", default="code_roscop.csv", help="ROSCOP CSV file")
    parser.add_argument("-o", "--output", help="Write the template to this file instead of stdout")
    parser.add_argument("--interactive", action="store_true", help="Review ambiguous split suggestions interactively")
    args = parser.parse_args()

    template = build_template(
        args.files,
        args.instrument,
        args.roscop,
        interactive=args.interactive,
    )
    if args.output:
        Path(args.output).write_text(template, encoding="utf-8")
    else:
        print(template)


if __name__ == "__main__":
    main()
