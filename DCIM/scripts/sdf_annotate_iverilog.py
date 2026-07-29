#!/usr/bin/env python3
"""Convert SDF back-annotation into Verilog that Icarus Verilog can simulate.

This tool performs static source-level back-annotation:

1. Parse an SDF file.
2. Clone every elaborated design-module occurrence so hierarchical instances can
   receive different delays without changing their visible instance names.
3. Clone every SDF-covered leaf cell and replace its specify block with the
   corresponding IOPATH delays.
4. Insert one delayed continuous assignment for every INTERCONNECT destination.
5. Strip the default specify blocks from the base libraries, so only delays
   explicitly supplied by the SDF remain active.

The generated netlist keeps the original top-module name and instance hierarchy,
which is important because OpenSTA reads VCD activity under testbench/dut.

Timing checks (SETUP/HOLD/WIDTH) are counted and reported but deliberately not
implemented. OpenSTA remains responsible for checking timing constraints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Iterator, Sequence


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def fail(message: str) -> "NoReturn":
    """Terminate with a clear command-line error."""

    raise SystemExit(f"ERROR: {message}")


def read_text(path: Path) -> str:
    """Read UTF-8 text and produce a friendly error if the file is missing."""

    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")


def write_text(path: Path, text: str) -> None:
    """Create parent directories and write UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def safe_identifier(text: str, limit: int = 48) -> str:
    """Convert a hierarchy path into a compact legal Verilog identifier tail."""

    body = re.sub(r"[^A-Za-z0-9_$]", "_", text).strip("_") or "root"
    if len(body) <= limit:
        return body
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{body[: limit - 11]}_{digest}"


def apply_replacements(text: str, replacements: Sequence[tuple[int, int, str]]) -> str:
    """Apply non-overlapping source replacements from right to left."""

    result = text
    for start, end, replacement in sorted(replacements, reverse=True):
        result = result[:start] + replacement + result[end:]
    return result


# ---------------------------------------------------------------------------
# S-expression parser for the subset of SDF used by OpenACM
# ---------------------------------------------------------------------------


SExpr = str | list["SExpr"]


_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<lpar>\()|"
    r"(?P<rpar>\))|"
    r'(?P<string>"(?:\\.|[^"\\])*")|'
    r"(?P<atom>[^\s()]+)"
    r")",
    re.DOTALL,
)


def tokenize_sexpr(text: str) -> Iterator[str]:
    """Yield parentheses, strings and atoms from an S-expression file."""

    position = 0
    length = len(text)
    while position < length:
        if text[position:].strip() == "":
            break
        match = _TOKEN_RE.match(text, position)
        if not match:
            tail = text[position : position + 80]
            fail(f"cannot tokenize SDF near: {tail!r}")
        position = match.end()
        token = match.group("lpar") or match.group("rpar") or match.group("string") or match.group("atom")
        if token is not None:
            yield token


def parse_sexpr(text: str) -> SExpr:
    """Parse a complete S-expression document into nested Python lists."""

    stack: list[list[SExpr]] = []
    roots: list[SExpr] = []
    for token in tokenize_sexpr(text):
        if token == "(":
            node: list[SExpr] = []
            if stack:
                stack[-1].append(node)
            else:
                roots.append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                fail("unexpected ')' while parsing SDF")
            stack.pop()
        else:
            value = token[1:-1] if token.startswith('"') and token.endswith('"') else token
            if stack:
                stack[-1].append(value)
            else:
                roots.append(value)
    if stack:
        fail("unterminated '(' while parsing SDF")
    if len(roots) != 1:
        fail(f"expected one SDF root expression, found {len(roots)}")
    return roots[0]


def node_head(node: SExpr) -> str | None:
    """Return the first atom of a list node."""

    if isinstance(node, list) and node and isinstance(node[0], str):
        return node[0]
    return None


def child_nodes(node: SExpr, head: str) -> list[list[SExpr]]:
    """Return direct list children whose first atom equals *head*."""

    if not isinstance(node, list):
        return []
    return [child for child in node[1:] if isinstance(child, list) and node_head(child) == head]


def first_child(node: SExpr, head: str) -> list[SExpr] | None:
    """Return the first direct child with the requested head."""

    matches = child_nodes(node, head)
    return matches[0] if matches else None


def render_sexpr(node: SExpr) -> str:
    """Render a condition subtree back into legal Verilog-like text."""

    if isinstance(node, str):
        return node
    return "(" + " ".join(render_sexpr(item) for item in node) + ")"


# ---------------------------------------------------------------------------
# SDF model and delay conversion
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DelayPair:
    rise_ns: Decimal
    fall_ns: Decimal


@dataclass(frozen=True)
class Iopath:
    source: str
    destination: str
    delay: DelayPair
    condition: str | None = None


@dataclass
class CellAnnotation:
    cell_type: str
    instance_path: str
    iopaths: list[Iopath] = field(default_factory=list)
    timing_check_count: int = 0


@dataclass(frozen=True)
class Interconnect:
    source: str
    destination: str
    delay: DelayPair


@dataclass
class SdfModel:
    design: str
    timescale: str
    cells: dict[str, CellAnnotation]
    interconnects: list[Interconnect]
    timing_check_count: int
    unsupported_heads: dict[str, int]


_TIME_UNIT_TO_NS = {
    "s": Decimal("1e9"),
    "ms": Decimal("1e6"),
    "us": Decimal("1e3"),
    "ns": Decimal("1"),
    "ps": Decimal("1e-3"),
    "fs": Decimal("1e-6"),
}


def timescale_factor_to_ns(timescale: str) -> Decimal:
    """Return the multiplier that converts one SDF time unit to nanoseconds."""

    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([a-zA-Z]+)", timescale.strip())
    if not match:
        fail(f"unsupported SDF TIMESCALE {timescale!r}")
    magnitude = Decimal(match.group(1))
    unit = match.group(2).lower()
    if unit not in _TIME_UNIT_TO_NS:
        fail(f"unsupported SDF time unit {unit!r}")
    return magnitude * _TIME_UNIT_TO_NS[unit]


def select_mtm(atom: str, corner: str) -> Decimal:
    """Select min/typ/max from an SDF scalar such as 0.01::0.03."""

    fields = atom.split(":")
    if len(fields) == 1:
        candidates = [fields[0]] * 3
    elif len(fields) == 3:
        candidates = fields
    else:
        fail(f"unsupported delay scalar {atom!r}")

    wanted = {"min": 0, "typ": 1, "max": 2}[corner]
    fallback_orders = {
        0: (0, 1, 2),
        1: (1, 2, 0),
        2: (2, 1, 0),
    }
    selected = ""
    for index in fallback_orders[wanted]:
        if candidates[index] != "":
            selected = candidates[index]
            break
    if selected == "":
        return Decimal(0)
    try:
        return Decimal(selected)
    except InvalidOperation:
        fail(f"invalid numeric SDF delay {selected!r}")


def parse_delay_value(node: SExpr, corner: str, factor: Decimal) -> Decimal:
    """Parse a parenthesized SDF delay value and convert it to nanoseconds."""

    if isinstance(node, str):
        atom = node
    elif len(node) == 0:
        return Decimal(0)
    elif len(node) == 1 and isinstance(node[0], str):
        atom = node[0]
    else:
        fail(f"unsupported delay value structure: {node!r}")
    return select_mtm(atom, corner) * factor


def parse_delay_pair(items: Sequence[SExpr], corner: str, factor: Decimal) -> DelayPair:
    """Read rise/fall fields; a single field applies to both transitions."""

    if not items:
        return DelayPair(Decimal(0), Decimal(0))
    rise = parse_delay_value(items[0], corner, factor)
    fall = parse_delay_value(items[1], corner, factor) if len(items) >= 2 else rise
    return DelayPair(rise, fall)


def atom_after(node: list[SExpr], index: int, context: str) -> str:
    """Read a required atom at a fixed list position."""

    if len(node) <= index or not isinstance(node[index], str):
        fail(f"expected atom {index} in {context}: {node!r}")
    return node[index]


def parse_iopath(node: list[SExpr], condition: str | None, corner: str, factor: Decimal) -> Iopath:
    """Parse one IOPATH list."""

    source = render_sexpr(node[1])
    destination = render_sexpr(node[2])
    delay = parse_delay_pair(node[3:], corner, factor)
    return Iopath(source=source, destination=destination, delay=delay, condition=condition)


def count_timing_checks(node: list[SExpr]) -> int:
    """Count direct timing-check statements in one TIMINGCHECK block."""

    return sum(1 for child in node[1:] if isinstance(child, list))


def parse_sdf(path: Path, corner: str) -> SdfModel:
    """Parse OpenACM's SDF into a compact annotation model."""

    root = parse_sexpr(read_text(path))
    if node_head(root) != "DELAYFILE":
        fail(f"{path} is not an SDF DELAYFILE")
    assert isinstance(root, list)

    design_node = first_child(root, "DESIGN")
    timescale_node = first_child(root, "TIMESCALE")
    design = atom_after(design_node, 1, "DESIGN") if design_node else ""
    timescale = atom_after(timescale_node, 1, "TIMESCALE") if timescale_node else "1ns"
    factor = timescale_factor_to_ns(timescale)

    cells: dict[str, CellAnnotation] = {}
    interconnects: list[Interconnect] = []
    timing_check_total = 0
    unsupported: dict[str, int] = {}

    supported_delay_heads = {"ABSOLUTE", "IOPATH", "COND", "INTERCONNECT"}

    for cell_node in child_nodes(root, "CELL"):
        type_node = first_child(cell_node, "CELLTYPE")
        instance_node = first_child(cell_node, "INSTANCE")
        if not type_node or not instance_node:
            fail("CELL is missing CELLTYPE or INSTANCE")
        cell_type = atom_after(type_node, 1, "CELLTYPE")
        instance_path = ""
        if len(instance_node) >= 2:
            instance_path = render_sexpr(instance_node[1]).strip()

        annotation = CellAnnotation(cell_type=cell_type, instance_path=instance_path)

        delay_node = first_child(cell_node, "DELAY")
        if delay_node:
            for mode_node in delay_node[1:]:
                if not isinstance(mode_node, list):
                    continue
                mode = node_head(mode_node)
                if mode != "ABSOLUTE":
                    unsupported[mode or "<unknown-delay-mode>"] = unsupported.get(mode or "<unknown-delay-mode>", 0) + 1
                    continue
                for entry in mode_node[1:]:
                    if not isinstance(entry, list):
                        continue
                    head = node_head(entry)
                    if head == "INTERCONNECT":
                        source = render_sexpr(entry[1])
                        destination = render_sexpr(entry[2])
                        interconnects.append(
                            Interconnect(source, destination, parse_delay_pair(entry[3:], corner, factor))
                        )
                    elif head == "IOPATH":
                        annotation.iopaths.append(parse_iopath(entry, None, corner, factor))
                    elif head == "COND":
                        if len(entry) < 3 or not isinstance(entry[-1], list) or node_head(entry[-1]) != "IOPATH":
                            unsupported["COND-non-IOPATH"] = unsupported.get("COND-non-IOPATH", 0) + 1
                            continue
                        condition = " ".join(render_sexpr(piece) for piece in entry[1:-1])
                        annotation.iopaths.append(parse_iopath(entry[-1], condition, corner, factor))
                    else:
                        unsupported[head or "<unknown-delay-entry>"] = unsupported.get(head or "<unknown-delay-entry>", 0) + 1

        timing_node = first_child(cell_node, "TIMINGCHECK")
        if timing_node:
            annotation.timing_check_count = count_timing_checks(timing_node)
            timing_check_total += annotation.timing_check_count

        # The top CELL has an empty INSTANCE and only carries INTERCONNECT data.
        if instance_path:
            if instance_path in cells:
                fail(f"duplicate SDF CELL instance {instance_path!r}")
            cells[instance_path] = annotation

    return SdfModel(
        design=design,
        timescale=timescale,
        cells=cells,
        interconnects=interconnects,
        timing_check_count=timing_check_total,
        unsupported_heads=unsupported,
    )


# ---------------------------------------------------------------------------
# Lightweight structural-Verilog parser
# ---------------------------------------------------------------------------


@dataclass
class Definition:
    kind: str
    name: str
    text: str


@dataclass
class PortConnection:
    pin: str
    expression: str
    expr_start: int
    expr_end: int


@dataclass
class Instance:
    module_type: str
    name: str
    type_start: int
    type_end: int
    statement_start: int
    statement_end: int
    ports: dict[str, PortConnection]


@dataclass
class ModuleInfo:
    name: str
    text: str
    instances: list[Instance]
    port_order: list[str]
    port_declarations: dict[str, tuple[str, str]]
    declaration_end: int


_DEF_START_RE = re.compile(r"(?m)^[ \t]*(module|primitive)[ \t]+(\\[^\s]+|[A-Za-z_$][A-Za-z0-9_$]*)")


def extract_definitions(text: str) -> list[Definition]:
    """Extract module and primitive blocks while preserving their source text."""

    definitions: list[Definition] = []
    position = 0
    while True:
        match = _DEF_START_RE.search(text, position)
        if not match:
            break
        kind = match.group(1)
        name = match.group(2)
        end_word = "endmodule" if kind == "module" else "endprimitive"
        end_match = re.search(rf"\b{end_word}\b", text[match.end() :])
        if not end_match:
            fail(f"unterminated {kind} {name}")
        end_word_start = match.end() + end_match.start()
        end_word_end = end_word_start + len(end_word)
        line_end = text.find("\n", end_word_end)
        end = end_word_end if line_end == -1 else line_end + 1
        definitions.append(Definition(kind=kind, name=name, text=text[match.start() : end]))
        position = end
    return definitions


def find_matching(text: str, open_index: int, opening: str = "(", closing: str = ")") -> int:
    """Find the matching closing delimiter while skipping strings and comments."""

    depth = 0
    index = open_index
    in_string = False
    escaped = False
    line_comment = False
    block_comment = False
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    fail(f"unmatched {opening!r} at character {open_index}")


_INSTANCE_RE = re.compile(
    r"(?m)^[ \t]*(?P<type>\\[^\s]+|[A-Za-z_$][A-Za-z0-9_$]*)"
    r"[ \t]+(?P<name>\\[^\s]+|[A-Za-z_$][A-Za-z0-9_$]*)[ \t]*\("
)

_VERILOG_KEYWORDS = {
    "module",
    "primitive",
    "input",
    "output",
    "inout",
    "wire",
    "reg",
    "logic",
    "assign",
    "always",
    "initial",
    "function",
    "task",
    "generate",
    "if",
    "for",
    "case",
}


def parse_named_ports(text: str, open_index: int, close_index: int) -> dict[str, PortConnection]:
    """Parse .PIN(expression) connections within one instance."""

    ports: dict[str, PortConnection] = {}
    position = open_index + 1
    pin_re = re.compile(r"\.\s*(\\[^\s(]+|[A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
    while position < close_index:
        match = pin_re.search(text, position, close_index)
        if not match:
            break
        pin = match.group(1)
        pin_open = text.find("(", match.start(), match.end())
        pin_close = find_matching(text, pin_open)
        if pin_close > close_index:
            fail("port connection extends past instance boundary")
        expression = text[pin_open + 1 : pin_close].strip()
        expr_raw_start = pin_open + 1
        expr_raw_end = pin_close
        while expr_raw_start < expr_raw_end and text[expr_raw_start].isspace():
            expr_raw_start += 1
        while expr_raw_end > expr_raw_start and text[expr_raw_end - 1].isspace():
            expr_raw_end -= 1
        ports[pin] = PortConnection(pin, expression, expr_raw_start, expr_raw_end)
        position = pin_close + 1
    return ports


def parse_port_header(module_text: str) -> list[str]:
    """Extract ordered port names from a non-ANSI module header."""

    match = re.search(r"\bmodule\s+(?:\\[^\s]+|[A-Za-z_$][A-Za-z0-9_$]*)\s*\(", module_text)
    if not match:
        return []
    open_index = module_text.find("(", match.start(), match.end())
    close_index = find_matching(module_text, open_index)
    content = module_text[open_index + 1 : close_index]
    ports = []
    for part in content.split(","):
        token = part.strip()
        if token:
            ports.append(token)
    return ports


def parse_port_declarations(module_text: str) -> tuple[dict[str, tuple[str, str]], int]:
    """Return name -> (direction, packed range) and the end of the declaration area."""

    declarations: dict[str, tuple[str, str]] = {}
    declaration_end = 0
    decl_re = re.compile(
        r"(?m)^[ \t]*(input|output|inout)[ \t]+"
        r"(?:(?:wire|reg|logic)[ \t]+)?"
        r"(?P<range>\[[^\]]+\][ \t]+)?"
        r"(?P<names>[^;]+);"
    )
    for match in decl_re.finditer(module_text):
        direction = match.group(1)
        packed_range = (match.group("range") or "").strip()
        for raw_name in match.group("names").split(","):
            name = raw_name.strip()
            if name:
                declarations[name] = (direction, packed_range)
        declaration_end = max(declaration_end, match.end())
    return declarations, declaration_end


def parse_module(definition: Definition) -> ModuleInfo:
    """Parse instances and ports from one structural module definition."""

    text = definition.text
    instances: list[Instance] = []
    for match in _INSTANCE_RE.finditer(text):
        module_type = match.group("type")
        name = match.group("name")
        if module_type in _VERILOG_KEYWORDS:
            continue
        open_index = text.find("(", match.start(), match.end())
        close_index = find_matching(text, open_index)
        semicolon = close_index + 1
        while semicolon < len(text) and text[semicolon].isspace():
            semicolon += 1
        if semicolon >= len(text) or text[semicolon] != ";":
            continue
        instances.append(
            Instance(
                module_type=module_type,
                name=name,
                type_start=match.start("type"),
                type_end=match.end("type"),
                statement_start=match.start(),
                statement_end=semicolon + 1,
                ports=parse_named_ports(text, open_index, close_index),
            )
        )
    declarations, declaration_end = parse_port_declarations(text)
    return ModuleInfo(
        name=definition.name,
        text=text,
        instances=instances,
        port_order=parse_port_header(text),
        port_declarations=declarations,
        declaration_end=declaration_end,
    )




def split_top_level_commas(expression: str) -> list[str]:
    """Split a concatenation body at commas that are not nested."""

    parts: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(expression):
        if char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(expression[start:index].strip())
            start = index + 1
    parts.append(expression[start:].strip())
    return [part for part in parts if part]


def scalar_bits_lsb_first(expression: str) -> list[str] | None:
    """Expand a simple concatenation into scalar expressions, LSB first."""

    expression = expression.strip()
    if not (expression.startswith("{") and expression.endswith("}")):
        return None
    items = split_top_level_commas(expression[1:-1])
    bits_msb_first: list[str] = []
    for item in items:
        part_select = re.fullmatch(r"(.+)\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\]", item)
        if part_select:
            base = part_select.group(1).strip()
            left = int(part_select.group(2))
            right = int(part_select.group(3))
            step = -1 if left > right else 1
            bits_msb_first.extend(f"{base}[{bit}]" for bit in range(left, right + step, step))
            continue
        sized_literal = re.fullmatch(r"(\d+)'[bBoOdDhH][0-9a-fA-FxXzZ_]+", item)
        if sized_literal and int(sized_literal.group(1)) != 1:
            return None
        # A bit-select, one-bit literal, or plain scalar net is one bit.
        bits_msb_first.append(item)
    return list(reversed(bits_msb_first))


def expression_bit(expression: str, bit: int) -> str:
    """Return a scalar expression for one bit of a simple vector connection."""

    expanded = scalar_bits_lsb_first(expression)
    if expanded is not None:
        if bit >= len(expanded):
            fail(f"bit {bit} is outside concatenation {expression!r}")
        return expanded[bit]
    if bit == 0 and re.fullmatch(r"[^\[]+", expression.strip()):
        return f"{expression.strip()}[0]"
    return f"{expression.strip()}[{bit}]"


def strip_specify_blocks(text: str) -> str:
    """Remove every specify...endspecify block from Verilog source."""

    return re.sub(r"(?s)\bspecify\b.*?\bendspecify\b", "", text)


def rename_module(text: str, old_name: str, new_name: str) -> str:
    """Rename only the declaration of a module."""

    pattern = re.compile(rf"(?m)^(?P<prefix>[ \t]*module[ \t]+){re.escape(old_name)}\b")
    changed, count = pattern.subn(rf"\g<prefix>{new_name}", text, count=1)
    if count != 1:
        fail(f"could not rename module {old_name} to {new_name}")
    return changed


# ---------------------------------------------------------------------------
# Annotation generator
# ---------------------------------------------------------------------------


def decimal_text(value: Decimal) -> str:
    """Format a Decimal without exponent notation or unnecessary trailing zeros."""

    normalized = value.quantize(Decimal("0.000001"))
    text = format(normalized, "f").rstrip("0").rstrip(".")
    return text if text else "0"


def max_delay(delays: Iterable[DelayPair]) -> DelayPair:
    """Return component-wise maximum rise/fall delays."""

    pairs = list(delays)
    if not pairs:
        return DelayPair(Decimal(0), Decimal(0))
    return DelayPair(max(item.rise_ns for item in pairs), max(item.fall_ns for item in pairs))


def generate_specify(iopaths: Sequence[Iopath], cond_mode: str) -> str:
    """Generate an Icarus-friendly specify block for one cell instance."""

    lines = ["  specify"]
    if cond_mode == "preserve":
        for path in iopaths:
            rise = decimal_text(path.delay.rise_ns)
            fall = decimal_text(path.delay.fall_ns)
            prefix = f"if ({path.condition}) " if path.condition else ""
            lines.append(f"    {prefix}({path.source} => {path.destination}) = ({rise}, {fall});")
    elif cond_mode == "max":
        grouped: dict[tuple[str, str], list[DelayPair]] = {}
        for path in iopaths:
            grouped.setdefault((path.source, path.destination), []).append(path.delay)
        for (source, destination), delays in sorted(grouped.items()):
            delay = max_delay(delays)
            rise = decimal_text(delay.rise_ns)
            fall = decimal_text(delay.fall_ns)
            lines.append(f"    ({source} => {destination}) = ({rise}, {fall});")
    else:
        fail(f"unknown condition mode {cond_mode!r}")
    lines.append("  endspecify")
    return "\n".join(lines)


def clone_library_module(original_text: str, old_name: str, new_name: str, iopaths: Sequence[Iopath], cond_mode: str) -> str:
    """Clone a functional cell module and inject its instance-specific paths."""

    specify_block = generate_specify(iopaths, cond_mode)
    if re.search(r"\bspecify\b.*?\bendspecify\b", original_text, re.DOTALL):
        cloned = re.sub(r"(?s)\bspecify\b.*?\bendspecify\b", specify_block, original_text, count=1)
    else:
        end_pos = original_text.rfind("endmodule")
        if end_pos < 0:
            fail(f"library module {old_name} has no endmodule")
        cloned = original_text[:end_pos] + specify_block + "\n\n" + original_text[end_pos:]
    return rename_module(cloned, old_name, new_name)


@dataclass
class AnnotationReport:
    sdf_file: str
    netlist_file: str
    top: str
    corner: str
    condition_mode: str
    sdf_timescale: str
    sdf_cells: int = 0
    matched_cells: int = 0
    iopath_total: int = 0
    conditional_iopath_total: int = 0
    interconnect_total: int = 0
    applied_interconnects: int = 0
    output_interconnects: int = 0
    timing_checks_ignored: int = 0
    design_module_clones: int = 0
    leaf_cell_clones: int = 0
    unmatched_cells: list[dict[str, str]] = field(default_factory=list)
    unmatched_interconnects: list[dict[str, str]] = field(default_factory=list)
    cell_type_mismatches: list[dict[str, str]] = field(default_factory=list)
    unsupported_sdf_constructs: dict[str, int] = field(default_factory=dict)


class Annotator:
    """Elaborate hierarchy and produce source-level SDF annotation."""

    def __init__(
        self,
        sdf: SdfModel,
        netlist_text: str,
        library_texts: Sequence[tuple[Path, str]],
        top: str,
        cond_mode: str,
        report: AnnotationReport,
    ) -> None:
        self.sdf = sdf
        self.top = top
        self.cond_mode = cond_mode
        self.report = report

        design_defs = [item for item in extract_definitions(netlist_text) if item.kind == "module"]
        self.design_modules = {item.name: parse_module(item) for item in design_defs}
        if top not in self.design_modules:
            fail(f"top module {top!r} not found in netlist")

        self.library_definitions: dict[str, Definition] = {}
        self.base_library_parts: list[str] = []
        for source_path, source_text in library_texts:
            definitions = extract_definitions(source_text)
            if not definitions:
                fail(f"no module or primitive definitions found in library {source_path}")
            stripped_source = strip_specify_blocks(source_text)
            self.base_library_parts.append(f"// Base library from {source_path}\n{stripped_source.rstrip()}\n")
            for definition in definitions:
                if definition.kind == "module":
                    self.library_definitions.setdefault(definition.name, definition)

        self.cell_clone_name: dict[str, str] = {}
        self.cell_clone_texts: list[str] = []
        self.design_clone_texts: list[str] = []
        self.visited_cell_paths: set[str] = set()
        self.visited_interconnect_indices: set[int] = set()
        self.design_clone_counter = 0
        self.cell_clone_counter = 0
        self.delay_wire_counter = 0

        self.interconnects_by_parent: dict[str, list[tuple[int, Interconnect, str, str]]] = {}
        self.output_interconnects: list[tuple[int, Interconnect]] = []
        for index, interconnect in enumerate(sdf.interconnects):
            if "/" not in interconnect.destination:
                self.output_interconnects.append((index, interconnect))
                continue
            instance_path, pin = interconnect.destination.rsplit("/", 1)
            if "/" in instance_path:
                parent_path, instance_name = instance_path.rsplit("/", 1)
            else:
                parent_path, instance_name = "", instance_path
            self.interconnects_by_parent.setdefault(parent_path, []).append(
                (index, interconnect, instance_name, pin)
            )

    def create_cell_clone(self, instance_path: str, annotation: CellAnnotation) -> str | None:
        """Create one leaf-cell module clone for an SDF CELL instance."""

        if instance_path in self.cell_clone_name:
            return self.cell_clone_name[instance_path]
        definition = self.library_definitions.get(annotation.cell_type)
        if definition is None:
            self.report.unmatched_cells.append(
                {
                    "instance": instance_path,
                    "cell_type": annotation.cell_type,
                    "reason": "cell type not found in supplied libraries",
                }
            )
            return None
        self.cell_clone_counter += 1
        clone_name = f"__SDF_CELL_{self.cell_clone_counter:05d}_{safe_identifier(annotation.cell_type, 24)}"
        clone_text = clone_library_module(
            definition.text,
            annotation.cell_type,
            clone_name,
            annotation.iopaths,
            self.cond_mode,
        )
        self.cell_clone_name[instance_path] = clone_name
        self.cell_clone_texts.append(
            f"// SDF leaf clone for {instance_path} ({annotation.cell_type})\n{clone_text.rstrip()}\n"
        )
        self.report.leaf_cell_clones += 1
        return clone_name

    def clone_occurrence(self, module_name: str, path: str, requested_name: str | None = None) -> str:
        """Recursively clone one design-module occurrence and annotate its children."""

        module = self.design_modules[module_name]
        self.design_clone_counter += 1
        clone_name = requested_name or f"__SDF_HIER_{self.design_clone_counter:05d}_{safe_identifier(path + '_' + module_name)}"
        replacements: list[tuple[int, int, str]] = []
        inserted_lines: list[str] = []
        instance_by_name = {instance.name: instance for instance in module.instances}

        # Every design-module occurrence gets its own module type. Instance names
        # themselves remain unchanged, preserving VCD hierarchy.
        for instance in module.instances:
            child_path = f"{path}/{instance.name}" if path else instance.name
            if instance.module_type in self.design_modules:
                child_clone = self.clone_occurrence(instance.module_type, child_path)
                replacements.append((instance.type_start, instance.type_end, child_clone))
                continue

            annotation = self.sdf.cells.get(child_path)
            if annotation is None:
                continue
            self.visited_cell_paths.add(child_path)
            if annotation.cell_type != instance.module_type:
                self.report.cell_type_mismatches.append(
                    {
                        "instance": child_path,
                        "sdf_cell_type": annotation.cell_type,
                        "netlist_cell_type": instance.module_type,
                    }
                )
            clone = self.create_cell_clone(child_path, annotation)
            if clone:
                replacements.append((instance.type_start, instance.type_end, clone))
                self.report.matched_cells += 1

        # Insert per-destination interconnect delay wires in this hierarchy level.
        # Bit-select destinations such as sram_inst/wd_in[3] are grouped so one
        # delayed vector replaces the original vector port connection.
        grouped_interconnects: dict[tuple[str, str], list[tuple[int, Interconnect, int | None]]] = {}
        for index, interconnect, instance_name, pin_text in self.interconnects_by_parent.get(path, []):
            pin_match = re.fullmatch(r"(.+?)(?:\[([0-9]+)\])?", pin_text)
            assert pin_match is not None
            base_pin = pin_match.group(1)
            bit = int(pin_match.group(2)) if pin_match.group(2) is not None else None
            grouped_interconnects.setdefault((instance_name, base_pin), []).append((index, interconnect, bit))

        for (instance_name, base_pin), entries in grouped_interconnects.items():
            instance = instance_by_name.get(instance_name)
            if instance is None:
                for _, interconnect, _ in entries:
                    self.report.unmatched_interconnects.append(
                        {
                            "source": interconnect.source,
                            "destination": interconnect.destination,
                            "reason": f"instance {instance_name!r} not found under {path or '<top>'}",
                        }
                    )
                continue
            connection = instance.ports.get(base_pin)
            if connection is None:
                for _, interconnect, _ in entries:
                    self.report.unmatched_interconnects.append(
                        {
                            "source": interconnect.source,
                            "destination": interconnect.destination,
                            "reason": f"pin {base_pin!r} not found on instance {instance_name!r}",
                        }
                    )
                continue

            bit_entries = [entry for entry in entries if entry[2] is not None]
            scalar_entries = [entry for entry in entries if entry[2] is None]
            if bit_entries and scalar_entries:
                for _, interconnect, _ in entries:
                    self.report.unmatched_interconnects.append(
                        {
                            "source": interconnect.source,
                            "destination": interconnect.destination,
                            "reason": "mixed scalar and bit-select delays for one destination pin",
                        }
                    )
                continue

            self.delay_wire_counter += 1
            wire_name = f"__sdf_ic_{self.delay_wire_counter:06d}"
            if bit_entries:
                max_bit = max(int(bit) for _, _, bit in bit_entries if bit is not None)
                expanded = scalar_bits_lsb_first(connection.expression)
                width = len(expanded) if expanded is not None else max_bit + 1
                inserted_lines.append(f"  wire [{width - 1}:0] {wire_name};")
                delay_by_bit = {int(bit): (index, interconnect) for index, interconnect, bit in bit_entries if bit is not None}
                for bit in range(width):
                    source_expression = expression_bit(connection.expression, bit)
                    delayed = delay_by_bit.get(bit)
                    if delayed is None:
                        inserted_lines.append(f"  assign {wire_name}[{bit}] = {source_expression};")
                        continue
                    index, interconnect = delayed
                    rise = decimal_text(interconnect.delay.rise_ns)
                    fall = decimal_text(interconnect.delay.fall_ns)
                    inserted_lines.append(
                        f"  assign #({rise}, {fall}) {wire_name}[{bit}] = {source_expression};"
                    )
                    self.visited_interconnect_indices.add(index)
                    self.report.applied_interconnects += 1
            else:
                index, interconnect, _ = scalar_entries[0]
                rise = decimal_text(interconnect.delay.rise_ns)
                fall = decimal_text(interconnect.delay.fall_ns)
                inserted_lines.append(f"  wire {wire_name};")
                inserted_lines.append(f"  assign #({rise}, {fall}) {wire_name} = {connection.expression};")
                self.visited_interconnect_indices.add(index)
                self.report.applied_interconnects += 1

            replacements.append((connection.expr_start, connection.expr_end, wire_name))

        cloned = apply_replacements(module.text, replacements)
        cloned = rename_module(cloned, module.name, clone_name)

        # Top-level output interconnects are implemented without a wrapper so the
        # visible VCD scope remains testbench/dut.
        if path == "":
            cloned = self.apply_top_output_delays(cloned, module)

        if inserted_lines:
            # Put generated wire declarations and delayed assignments before the
            # first instance.  Appending them just before endmodule makes an
            # earlier port connection look like an undeclared implicit wire to
            # Icarus, even though the declaration appears later in the module.
            parsed_clone = parse_module(
                Definition(kind="module", name=clone_name, text=cloned)
            )
            if parsed_clone.instances:
                insert_pos = min(
                    instance.statement_start for instance in parsed_clone.instances
                )
            else:
                insert_pos = cloned.rfind("endmodule")
            cloned = (
                cloned[:insert_pos]
                + "\n"
                + "\n".join(inserted_lines)
                + "\n"
                + cloned[insert_pos:]
            )

        self.design_clone_texts.append(
            f"// Elaborated design clone for hierarchy {path or '<top>'}\n{cloned.rstrip()}\n"
        )
        self.report.design_module_clones += 1
        return clone_name

    def apply_top_output_delays(self, cloned: str, original_module: ModuleInfo) -> str:
        """Move each delayed top output onto an internal net and delay its bits."""

        by_base: dict[str, dict[int | None, tuple[int, Interconnect]]] = {}
        for index, interconnect in self.output_interconnects:
            match = re.fullmatch(r"([A-Za-z_$][A-Za-z0-9_$]*)(?:\[([0-9]+)\])?", interconnect.destination)
            if not match:
                self.report.unmatched_interconnects.append(
                    {
                        "source": interconnect.source,
                        "destination": interconnect.destination,
                        "reason": "unsupported top-output syntax",
                    }
                )
                continue
            base = match.group(1)
            bit = int(match.group(2)) if match.group(2) is not None else None
            declaration = original_module.port_declarations.get(base)
            if not declaration or declaration[0] != "output":
                self.report.unmatched_interconnects.append(
                    {
                        "source": interconnect.source,
                        "destination": interconnect.destination,
                        "reason": "destination is not a declared top output",
                    }
                )
                continue
            by_base.setdefault(base, {})[bit] = (index, interconnect)

        if not by_base:
            return cloned

        declarations_to_add: list[str] = []
        assignments_to_add: list[str] = []
        logic_start = original_module.declaration_end
        # Module renaming does not change text length in a predictable way. Find
        # the declaration area's equivalent position in the renamed clone again.
        _, cloned_decl_end = parse_port_declarations(cloned)
        logic_start = cloned_decl_end
        end_pos = cloned.rfind("endmodule")
        prefix = cloned[:logic_start]
        logic = cloned[logic_start:end_pos]
        suffix = cloned[end_pos:]

        for base, bit_map in by_base.items():
            direction, packed_range = original_module.port_declarations[base]
            internal = f"__sdf_out_{base}"
            declarations_to_add.append(f"  wire {packed_range + ' ' if packed_range else ''}{internal};")
            logic = re.sub(
                rf"(?<![A-Za-z0-9_$]){re.escape(base)}(?![A-Za-z0-9_$])",
                internal,
                logic,
            )
            if packed_range:
                range_match = re.fullmatch(r"\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\]", packed_range)
                if not range_match:
                    fail(f"unsupported output range {packed_range!r} for {base}")
                left, right = int(range_match.group(1)), int(range_match.group(2))
                step = -1 if left > right else 1
                for bit in range(left, right + step, step):
                    entry = bit_map.get(bit)
                    if entry:
                        index, interconnect = entry
                        rise = decimal_text(interconnect.delay.rise_ns)
                        fall = decimal_text(interconnect.delay.fall_ns)
                        assignments_to_add.append(
                            f"  assign #({rise}, {fall}) {base}[{bit}] = {internal}[{bit}];"
                        )
                        self.visited_interconnect_indices.add(index)
                        self.report.applied_interconnects += 1
                        self.report.output_interconnects += 1
                    else:
                        assignments_to_add.append(f"  assign {base}[{bit}] = {internal}[{bit}];")
            else:
                entry = bit_map.get(None)
                if entry:
                    index, interconnect = entry
                    rise = decimal_text(interconnect.delay.rise_ns)
                    fall = decimal_text(interconnect.delay.fall_ns)
                    assignments_to_add.append(f"  assign #({rise}, {fall}) {base} = {internal};")
                    self.visited_interconnect_indices.add(index)
                    self.report.applied_interconnects += 1
                    self.report.output_interconnects += 1
                else:
                    assignments_to_add.append(f"  assign {base} = {internal};")

        insertion = "\n" + "\n".join(declarations_to_add) + "\n"
        tail = "\n" + "\n".join(assignments_to_add) + "\n"
        return prefix + insertion + logic + tail + suffix

    def generate(self) -> tuple[str, str]:
        """Generate annotated design source and annotated/base library source."""

        # The top clone deliberately keeps its original module name.
        self.clone_occurrence(self.top, "", requested_name=self.top)

        for instance_path, annotation in self.sdf.cells.items():
            if instance_path not in self.visited_cell_paths:
                self.report.unmatched_cells.append(
                    {
                        "instance": instance_path,
                        "cell_type": annotation.cell_type,
                        "reason": "instance path not found while elaborating design hierarchy",
                    }
                )

        for index, interconnect in enumerate(self.sdf.interconnects):
            if index not in self.visited_interconnect_indices:
                # Avoid duplicating an already detailed error.
                if not any(item["destination"] == interconnect.destination for item in self.report.unmatched_interconnects):
                    self.report.unmatched_interconnects.append(
                        {
                            "source": interconnect.source,
                            "destination": interconnect.destination,
                            "reason": "interconnect was not applied",
                        }
                    )

        netlist_header = (
            "`timescale 1ns/1ps\n"
            "// Generated by sdf_annotate_iverilog.py. Do not edit manually.\n"
            "// Instance names and visible hierarchy are preserved for VCD/OpenSTA mapping.\n\n"
        )
        # Children are appended before parents because clone_occurrence appends a
        # parent after recursively generating all children. Verilog permits either
        # order, but this order is convenient when reading the output.
        annotated_netlist = netlist_header + "\n".join(self.design_clone_texts)

        library_header = (
            "`timescale 1ns/1ps\n"
            "// Generated by sdf_annotate_iverilog.py. Do not edit manually.\n"
            "// Base-library specify blocks were removed; SDF-covered clones follow.\n\n"
        )
        annotated_library = (
            library_header
            + "\n".join(self.base_library_parts)
            + "\n// ------------------------------------------------------------------\n"
            + "// Instance-specific SDF cell clones\n"
            + "// ------------------------------------------------------------------\n\n"
            + "\n".join(self.cell_clone_texts)
        )
        return annotated_netlist, annotated_library


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert SDF + structural Verilog into Icarus-simulatable annotated Verilog."
    )
    parser.add_argument("--sdf", type=Path, required=True, help="input SDF file")
    parser.add_argument("--netlist", type=Path, required=True, help="input structural Verilog netlist")
    parser.add_argument(
        "--library",
        type=Path,
        action="append",
        required=True,
        help="functional Verilog library; repeat for Nangate, SRAM macro, filler stubs, etc.",
    )
    parser.add_argument("--top", required=True, help="top module name")
    parser.add_argument("--corner", choices=("min", "typ", "max"), default="max")
    parser.add_argument(
        "--condition-mode",
        choices=("max", "preserve"),
        default="max",
        help="max: collapse conditional paths conservatively; preserve: emit Verilog if-paths",
    )
    parser.add_argument("--output-netlist", type=Path, required=True)
    parser.add_argument("--output-library", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return failure if any CELL or INTERCONNECT cannot be applied",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)

    sdf = parse_sdf(args.sdf, args.corner)
    report = AnnotationReport(
        sdf_file=str(args.sdf),
        netlist_file=str(args.netlist),
        top=args.top,
        corner=args.corner,
        condition_mode=args.condition_mode,
        sdf_timescale=sdf.timescale,
        sdf_cells=len(sdf.cells),
        iopath_total=sum(len(cell.iopaths) for cell in sdf.cells.values()),
        conditional_iopath_total=sum(
            1 for cell in sdf.cells.values() for path in cell.iopaths if path.condition is not None
        ),
        interconnect_total=len(sdf.interconnects),
        timing_checks_ignored=sdf.timing_check_count,
        unsupported_sdf_constructs=sdf.unsupported_heads,
    )

    netlist_text = read_text(args.netlist)
    library_texts = [(path, read_text(path)) for path in args.library]
    annotator = Annotator(
        sdf=sdf,
        netlist_text=netlist_text,
        library_texts=library_texts,
        top=args.top,
        cond_mode=args.condition_mode,
        report=report,
    )
    annotated_netlist, annotated_library = annotator.generate()

    write_text(args.output_netlist, annotated_netlist)
    write_text(args.output_library, annotated_library)
    write_text(args.report, json.dumps(report.__dict__, indent=2, ensure_ascii=False) + "\n")

    print(f"SDF cells               : {report.sdf_cells}")
    print(f"Matched cells           : {report.matched_cells}")
    print(f"IOPATH entries          : {report.iopath_total}")
    print(f"Conditional IOPATHs     : {report.conditional_iopath_total}")
    print(f"INTERCONNECT entries    : {report.interconnect_total}")
    print(f"Applied interconnects   : {report.applied_interconnects}")
    print(f"Timing checks ignored   : {report.timing_checks_ignored}")
    print(f"Design module clones    : {report.design_module_clones}")
    print(f"Leaf cell clones        : {report.leaf_cell_clones}")
    print(f"Unmatched cells         : {len(report.unmatched_cells)}")
    print(f"Unmatched interconnects : {len(report.unmatched_interconnects)}")
    print(f"Report                  : {args.report}")

    has_errors = bool(
        report.unmatched_cells
        or report.unmatched_interconnects
        or report.cell_type_mismatches
        or report.unsupported_sdf_constructs
    )
    if args.strict and has_errors:
        print("Strict annotation failed; inspect the JSON report.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
