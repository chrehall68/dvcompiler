from typing import Optional

# ==============================
# Constants
# ==============================
REG_WIDTH = 5
OPCODE_WIDTH = 6
SHAMT_WIDTH = 5
FUNCT_WIDTH = 6
JMP_ADDR_WIDTH = 26
IMM_WIDTH = 16
OPCODES = {
    "addi": bin(int(0x08))[2:].rjust(OPCODE_WIDTH, "0"),
    "muli": bin(int(0x1D))[2:].rjust(OPCODE_WIDTH, "0"),
    "andi": bin(int(0x0C))[2:].rjust(OPCODE_WIDTH, "0"),
    "ori": bin(int(0x0D))[2:].rjust(OPCODE_WIDTH, "0"),
    "lui": bin(int(0x0F))[2:].rjust(OPCODE_WIDTH, "0"),
    "slti": bin(int(0x0A))[2:].rjust(OPCODE_WIDTH, "0"),
    "beq": bin(int(0x04))[2:].rjust(OPCODE_WIDTH, "0"),
    "bne": bin(int(0x05))[2:].rjust(OPCODE_WIDTH, "0"),
    "lw": bin(int(0x23))[2:].rjust(OPCODE_WIDTH, "0"),
    "sw": bin(int(0x2B))[2:].rjust(OPCODE_WIDTH, "0"),
    "jmp": bin(int(0x02))[2:].rjust(OPCODE_WIDTH, "0"),
    "jal": bin(int(0x03))[2:].rjust(OPCODE_WIDTH, "0"),
    "push": bin(int(0x1B))[2:].rjust(OPCODE_WIDTH, "0"),
    "pop": bin(int(0x1C))[2:].rjust(OPCODE_WIDTH, "0"),
}
FUNCTS = {
    "add": bin(int(0x20))[2:].rjust(FUNCT_WIDTH, "0"),
    "sub": bin(int(0x22))[2:].rjust(FUNCT_WIDTH, "0"),
    "mul": bin(int(0x2C))[2:].rjust(FUNCT_WIDTH, "0"),
    "and": bin(int(0x24))[2:].rjust(FUNCT_WIDTH, "0"),
    "or": bin(int(0x25))[2:].rjust(FUNCT_WIDTH, "0"),
    "nor": bin(int(0x27))[2:].rjust(FUNCT_WIDTH, "0"),
    "slt": bin(int(0x2A))[2:].rjust(FUNCT_WIDTH, "0"),
    "sll": bin(int(0x01))[2:].rjust(FUNCT_WIDTH, "0"),
    "srl": bin(int(0x02))[2:].rjust(FUNCT_WIDTH, "0"),
    "jr": bin(int(0x08))[2:].rjust(FUNCT_WIDTH, "0"),
}
INSTRUCTIONS = set(OPCODES.keys()) | set(FUNCTS.keys())
GENERIC_R_TYPES = [key for key in FUNCTS if key not in ["jr", "sll", "srl"]]
GENERIC_I_TYPES = ["addi", "muli", "andi", "ori", "slti", "beq", "bne", "lw", "sw"]


def reg_to_binary(reg_num: str):
    assert reg_num.startswith("r"), f"Expected register, got {reg_num}"
    return bin(int(reg_num.removeprefix("r")))[2:].rjust(5, "0")


def imm_to_binary(imm: str, size: int = IMM_WIDTH):
    if imm.startswith("0x"):
        imm = int(imm[2:], 16)  # hex
    elif imm.startswith("0b"):
        imm = int(imm[2:], 2)  # binary
    else:  # decimal
        imm = int(imm)
    if imm < 0:
        tmp = list(map(lambda x: x, bin(imm)[3:].rjust(size, "0")))
        first_one_index = size - 1
        while first_one_index > -1 and tmp[first_one_index] != "1":
            first_one_index -= 1
        # now, everything before this must get swapped
        for i in range(first_one_index - 1, -1, -1):
            if tmp[i] == "1":
                tmp[i] = "0"
            else:
                tmp[i] = "1"
        return "".join(tmp)

    return bin(imm)[2:].rjust(size, "0")


def to_hex(*args):
    return hex(int("".join(args), 2))[2:].rjust(8, "0").upper()


def encode_r_type(
    opcode: Optional[str] = None,
    rs: Optional[str] = None,
    rt: Optional[str] = None,
    rd: Optional[str] = None,
    shamt: Optional[str] = None,
    funct: Optional[str] = None,
):
    """
    Returns the 8-digit hex encoding
    """
    opcode = opcode or "0" * OPCODE_WIDTH
    rs = rs or "0" * REG_WIDTH
    rt = rt or "0" * REG_WIDTH
    rd = rd or "0" * REG_WIDTH
    shamt = shamt or "0" * SHAMT_WIDTH
    funct = funct or "0" * FUNCT_WIDTH
    return to_hex(opcode, rs, rt, rd, shamt, funct)


def encode_i_type(
    opcode: Optional[str] = None,
    rs: Optional[str] = None,
    rt: Optional[str] = None,
    imm: Optional[str] = None,
):
    """
    Returns the 8-digit hex encoding
    """
    opcode = opcode or "0" * OPCODE_WIDTH
    rs = rs or "0" * REG_WIDTH
    rt = rt or "0" * REG_WIDTH
    imm = imm or "0" * IMM_WIDTH
    return to_hex(opcode, rs, rt, imm)


def encode_j_type(
    opcode: Optional[str] = None,
    addr: Optional[str] = None,
):
    opcode = opcode or "0" * OPCODE_WIDTH
    addr = addr or "0" * JMP_ADDR_WIDTH
    return to_hex(opcode, addr)


# ==============================
# R Types
# ==============================
for inst in GENERIC_R_TYPES:
    exec(
        f"""
def encode_{inst}(rd, rs, rt):
    return encode_r_type(rd=reg_to_binary(rd), rs=reg_to_binary(rs), rt=reg_to_binary(rt), funct=FUNCTS["{inst}"])
""".strip()
    )


def encode_srl(rd, rs, shamt):
    return encode_r_type(
        rd=reg_to_binary(rd),
        rs=reg_to_binary(rs),
        shamt=imm_to_binary(shamt, SHAMT_WIDTH),
        funct=FUNCTS["srl"],
    )


def encode_sll(rd, rs, shamt):
    return encode_r_type(
        rd=reg_to_binary(rd),
        rs=reg_to_binary(rs),
        shamt=imm_to_binary(shamt, SHAMT_WIDTH),
        funct=FUNCTS["sll"],
    )


def encode_jr(rs):
    return encode_r_type(rs=reg_to_binary(rs), funct=FUNCTS["jr"])


# ==============================
# I Types
# ==============================
for inst in GENERIC_I_TYPES:
    exec(
        f"""
def encode_{inst}(rt, rs, imm):
    return encode_i_type(rt=reg_to_binary(rt), rs=reg_to_binary(rs), imm=imm_to_binary(imm), opcode=OPCODES["{inst}"])
        """.strip()
    )


def encode_lui(rt, imm):
    return encode_i_type(
        rt=reg_to_binary(rt),
        rs=reg_to_binary(rt),
        imm=imm_to_binary(imm),
        opcode=OPCODES["lui"],
    )


# ==============================
# J Types
# ==============================
def encode_jmp(addr):
    return encode_j_type(
        opcode=OPCODES["jmp"], addr=imm_to_binary(addr, JMP_ADDR_WIDTH)
    )


def encode_jal(addr):
    return encode_j_type(
        opcode=OPCODES["jal"], addr=imm_to_binary(addr, JMP_ADDR_WIDTH)
    )


def encode_push():
    return encode_j_type(opcode=OPCODES["push"])


def encode_pop():
    return encode_j_type(opcode=OPCODES["pop"])


def encode(inst: str, *args: str) -> str:
    local_dict = {}
    exec(f"f = encode_{inst}", globals(), local_dict)
    return local_dict["f"](*args)
