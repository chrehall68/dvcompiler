import re
from .translator import INSTRUCTIONS
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

REGISTERS = [f"r{i}" for i in range(0, 32)]


@dataclass
class Token:
    cls: str
    contents: str


@dataclass
class Label:
    name: str


@dataclass
class Instruction:
    name: str
    args: List[Token]


@dataclass
class TextSegment:
    items: List[Union[Label, Instruction]]


@dataclass
class Data:
    name: str
    values: List[Token]


@dataclass
class DataSegment:
    items: List[Data]


def any_of(*items: str):
    items = sorted(list(items), key=len, reverse=True)
    items = "|".join(map(lambda a: f"({a})", items))
    return re.compile(f"({items})")


def lex(contents: str) -> List[Token]:
    possibilities = [
        (
            "whitespace",
            re.compile(r"[\t\r\n ]*"),
        ),
        (
            "register",
            any_of(*REGISTERS),
        ),
        (
            "instruction",
            any_of(*INSTRUCTIONS, "la"),  # la is recognized by assembler
        ),
        (
            "label",
            re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*"),
        ),
        (
            "literal",
            re.compile(r"((0x[0-9A-F]+)|(0b[01]+)|(-?[0-9]+))"),
        ),
        (
            "colon",
            re.compile(r":"),
        ),
        (
            "comma",
            re.compile(r","),
        ),
        (
            "semicolon",
            re.compile(r";"),
        ),
        (
            "comment",
            re.compile(r"//.*"),
        ),
        (
            "multiline_comment",
            re.compile(r"\/\*(.*?\n?)*?\*\/"),
        ),
        ("data", re.compile(r"\.data")),
        ("text", re.compile(r"\.text")),
    ]

    position = 0
    tokens = []

    while position < len(contents):
        longest_chunk = 0
        possib_name = ""
        for possib, expr in possibilities:
            match = expr.match(contents, position)
            if match and len(match.group()) > longest_chunk:
                longest_chunk = len(match.group())
                possib_name = possib
        if longest_chunk == 0:
            raise Exception(f"Unexpected token starting at {contents[position:]}")
        tokens.append(Token(possib_name, contents[position : position + longest_chunk]))
        position = position + longest_chunk
    return tokens


def preprocess(tokens: List[Token]):
    exclude = {"whitespace", "comment", "multiline_comment"}
    return list(filter(lambda tok: tok.cls not in exclude, tokens))


def parse(tokens: List[Token]) -> List[Union[DataSegment, TextSegment]]:
    def parse_label(idx: int) -> Tuple[Optional[Label], int]:
        # label:
        if (
            tokens[idx].cls != "label"
            or idx + 1 >= len(tokens)
            or tokens[idx + 1].cls != "colon"
        ):
            return None, idx
        return Label(tokens[idx].contents), idx + 2

    def parse_instruction(idx: int) -> Tuple[Optional[Instruction], int]:
        # keyword [(literal|register|label) {, (literal|register|label)}];
        if tokens[idx].cls != "instruction":
            return None, idx
        name = tokens[idx].contents
        args = []
        # take any arguments
        pos = idx + 1
        posibs = {"literal", "register", "label"}
        if pos < len(tokens) and tokens[pos].cls in posibs:
            args.append(tokens[pos])
            pos += 1

            while pos < len(tokens) and tokens[pos].cls != "semicolon":
                if tokens[pos].cls != "comma":
                    return None, pos
                pos += 1
                if tokens[pos].cls not in {"literal", "register", "label"}:
                    return None, pos
                args.append(tokens[pos])
                pos += 1
        if pos >= len(tokens) or tokens[pos].cls != "semicolon":
            return None, pos
        return Instruction(name=name, args=args), pos + 1

    def parse_data(idx: int) -> Tuple[Optional[Data], int]:
        # label: d1 {, d2};
        if (
            tokens[idx].cls != "label"
            or idx + 1 >= len(tokens)
            or tokens[idx + 1].cls != "colon"
        ):
            return None, idx
        name = tokens[idx].contents
        idx += 2
        if tokens[idx].cls != "literal":
            return None, idx
        items = []
        items.append(tokens[idx])
        idx += 1
        while idx < len(tokens) and tokens[idx].cls != "semicolon":
            # take comma
            if tokens[idx].cls != "comma":
                return None, idx
            idx += 1
            # take data
            if tokens[idx].cls != "literal":
                return None, idx
            items.append(tokens[idx])
            idx += 1
        if idx >= len(tokens):
            return None, idx
        # otherwise, cur token is semicolon
        return Data(name, items), idx + 1

    def any_of(fns, idx: int):
        latest = idx
        for f in fns:
            result, newIdx = f(idx)
            if result:
                return result, newIdx
            latest = max(newIdx, latest)
        return None, latest

    def take_items(fns, idx: int):
        items = []
        while idx < len(tokens):
            v, idx = any_of(fns, idx)
            if v is None:
                break
            items.append(v)
        return items, idx

    def parse_data_segment(idx: int):
        if idx >= len(tokens) or tokens[idx].cls != "data":
            return None, idx
        v, idx = take_items([parse_data], idx + 1)
        return DataSegment(v), idx

    def parse_text_segment(idx: int):
        if idx >= len(tokens) or tokens[idx].cls != "text":
            return None, idx
        v, idx = take_items([parse_instruction, parse_label], idx + 1)
        return TextSegment(v), idx

    results, idx = take_items([parse_text_segment, parse_data_segment], 0)
    if idx < len(tokens):
        raise Exception(f"Error parsing, near {tokens[idx:]}")
    return results


def process(contents: str):
    return parse(preprocess(lex(contents)))
