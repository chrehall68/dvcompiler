from typing import List, Union
from .translator import encode, imm_to_binary
from .grammar import Label, Instruction, Data, Token, DataSegment, TextSegment


PROGRAM_START_ADDR = 0x1000
DATA_START_ADDR = 0x01008000


def assemble(segments: List[Union[DataSegment, TextSegment]]) -> str:
    labels = {}  # label : instruction_idx
    cur_labels = []

    filtered_statements = [Instruction("jmp", [Token("label", "main")])]
    filtered_datas: List[Data] = []
    data_to_offset = {}
    data_offset = 0

    # first pass is locate all labels and calculate addresses of
    # data
    for segment in segments:
        if type(segment) is TextSegment:
            for statement in segment.items:
                if type(statement) is Label:
                    cur_labels.append(statement.name)
                else:
                    for label in cur_labels:
                        # this is what the label points to
                        labels[label] = len(filtered_statements)
                    cur_labels = []
                    filtered_statements.append(statement)  # only take instructions
        else:
            # data segment
            for data in segment.items:
                if data.name in data_to_offset:
                    raise Exception(f"{data.name} already declared!")
                data_to_offset[data.name] = data_offset
                filtered_datas.append(data)
                data_offset += len(data.values)

    # second pass is replace labels w/ absolute addresses
    # and replace any la with the correct logical address
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
                    addr = hex(PROGRAM_START_ADDR + labels[statement.args[j].contents])
                    statement.args[j] = Token(
                        "literal",
                        addr,
                    )
                elif statement.name == "la":
                    addr = hex(
                        DATA_START_ADDR + data_to_offset[statement.args[j].contents]
                    )
                    statement.args[j] = Token("literal", addr)
                else:
                    raise Exception(
                        f"Didn't expect a label for instruction {statement.name}"
                    )

    # technically assemblers can do everything in 2 passes
    # but we'll do the translation in a third pass
    results = ["// ------ Program Part ------", "@00001000"]
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

    if len(filtered_datas) > 0:
        results.append("")  # newline for breathing space
        results.append("// ------ Data Part ------")
        results.append("@01008000")  # data start
        for data in filtered_datas:
            for i, val in enumerate(data.values):
                # modelsim expects everything in hex already
                # so we remove the leading "0x" and pad to 8 digits just in case
                binary = imm_to_binary(val.contents, 32)
                results.append(hex(int(binary, 2))[2:].rjust(8, "0"))
                if i == 0:
                    results[-1] += (
                        f"    // {data.name}: {', '.join(map(lambda a: a.contents, data.values))}".rstrip()
                        + ";"
                    )

    return "\n".join(results)
