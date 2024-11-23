"""
Main must be the last label in the file
"""

from typing import List, Union
from .translator import encode
from .grammar import Label, Instruction, Token


START_ADDR = 0x1000


def assemble(statements: List[Union[Instruction, Label]]) -> str:
    labels = {}  # label : instruction_idx
    cur_labels = []

    filtered_statements = [Instruction("jmp", [Token("label", "main")])]

    # first pass is locate all labels
    for statement in statements:
        if type(statement) is Label:
            cur_labels.append(statement.name)
        else:
            for label in cur_labels:
                # this is what the label points to
                labels[label] = len(filtered_statements)
            cur_labels = []
            filtered_statements.append(statement)  # only take instructions

    # second pass is replace labels w/ absolute addresses
    for i, statement in enumerate(filtered_statements):
        for j in range(len(statement.args)):
            if statement.args[j].cls == "label":
                # replace
                if statement.name in {"beq", "bne"}:
                    # relative
                    # (PC+1)+x = label
                    # x = label - (PC+1)
                    diff = labels[statement.args[j].contents] - (i + 1)
                    statement.args[j] = Token("literal", str(diff))
                elif statement.name in {"jmp", "jal"}:
                    # absolute
                    statement.args[j] = Token(
                        "literal",
                        str(START_ADDR + labels[statement.args[j].contents]),
                    )
                else:
                    raise Exception(
                        f"Didn't expect a label for instruction {statement.name}"
                    )

    # technically assemblers can do everything in 2 passes
    # but we'll do the translation in a third pass
    results = ["@00001000"]
    sorted_labels = sorted([(idx, label) for label, idx in labels.items()])
    label_idx = 0
    for i, statement in enumerate(filtered_statements):
        args = list(map(lambda t: t.contents, statement.args))
        tmp = [encode(statement.name, *args), "    //"]
        while label_idx < len(sorted_labels) and sorted_labels[label_idx][0] <= i:
            tmp.append(f" {sorted_labels[label_idx][1]}:")
            label_idx += 1
        tmp.append(f" {statement.name}")
        if len(args) > 0:
            tmp.append(" " + ", ".join(args))
        tmp.append(";")
        results.append("".join(tmp))
    return "\n".join(results)
