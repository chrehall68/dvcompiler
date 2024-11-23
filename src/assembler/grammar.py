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
            any_of(*INSTRUCTIONS),
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


def parse(tokens: List[Token]) -> List[Union[Label, Instruction]]:
    def parse_label(idx: int) -> Tuple[Optional[Label], int]:
        if (
            tokens[idx].cls != "label"
            or idx + 1 >= len(tokens)
            or tokens[idx + 1].cls != "colon"
        ):
            return None, idx
        return Label(tokens[idx].contents), idx + 2

    def parse_instruction(idx: int) -> Tuple[Optional[Instruction], int]:
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

    def any_of(fns, idx: int):
        latest = idx
        for f in fns:
            result, newIdx = f(idx)
            if result:
                return result, newIdx
            latest = max(newIdx, latest)
        return None, latest

    statements = []
    idx = 0
    while idx < len(tokens):
        v, idx = any_of([parse_instruction, parse_label], idx)
        if v is None:
            raise Exception(f"Improper statement near {tokens[idx:]}")
        statements.append(v)
    return statements


def process(contents: str):
    return parse(preprocess(lex(contents)))
