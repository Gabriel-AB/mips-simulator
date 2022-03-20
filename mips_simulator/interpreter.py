from typing import Dict, Literal, Sequence
from functools import partial
from .constants import REGS


FUNCTIONS = { 0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav", 8: "jr", 16: "mfhi", 18: "mflo", 24: "mult", 25: "multu", 26: "div", 27: "divu", 32: "add", 33: "addu", 34: "sub", 35: "subu", 36: "and", 37: "or", 38: "xor", 39: "nor", 42: "slt"}
OPCODES = {
    0: FUNCTIONS,
    1: "bltz", 2: "j", 3: "jal", 4: "beq", 5: "bne", 6: "blez", 7: "bgtz", 8: "addi", 9: "addiu", 10: "slti", 12: "andi", 13: "ori", 14: "xori", 15: "lui", 32: "lb", 35: "lw", 36: "lbu", 40: "sb", 43: "sw"
}


def hex2bin(text: str) -> str:
    value = int(text, base=16)
    return f'{value:032b}'


def split_bits(text: str, indexes: Sequence[int]) -> tuple[str]:
    b_iter = iter(indexes)
    e_iter = iter(indexes)
    next(e_iter)
    return tuple(
        text[begin:end] 
        for begin, end in
        zip(b_iter, e_iter)
    )


split_r = partial(split_bits, indexes=(0, 6, 11, 16, 21, 26, 32))
split_i = partial(split_bits, indexes=(0, 6, 11, 16, 32))
split_j = partial(split_bits, indexes=(0, 6, 32))


def check_type(binary_text: str) -> Literal['R', 'I', 'J']:
    opcode = int(binary_text[:6], base=2)
    if opcode == 0:
        return 'R'
    elif opcode in [2,3]:
        return 'J'
    return 'I'


def translate_r_command(text: str) -> str:
    parts = split_r(text)
    parts = tuple(map(partial(int, base=2), parts))

    op, rs, rt, rd, sh, fn = parts
    rs, rt, rd = REGS[rs], REGS[rt], REGS[rd]
    
    if fn == 12:
        return 'syscall'
    
    name = FUNCTIONS[fn]
    
    if name in 'mfhimflojr': # one argument cases
        return f'{name} {rs}'

    if name in 'multudivu': # two argument cases
        return f'{name} {rs}, {rt}'

    return f'{name} {rd}, {rs}, {rt}'


def translate_i_command(text: str) -> str:
    parts = split_i(text)
    parts = tuple(map(partial(int, base=2), parts))

    op, rs, rt, operand_or_offset = parts
    name, rs, rt = OPCODES[op], REGS[rs], REGS[rt]

    if name in 'lwswlbusb': # offset cases
        return f'{name} {rs}, {operand_or_offset}({rt})'

    if name in 'luibltz': # one argument cases
        return f'{name} {rs}, {operand_or_offset}'

    return f'{name} {rs}, {rt}, {operand_or_offset}'


def translate_j_command(text: str) -> str:
    parts = split_j(text)
    op, jump = parts
    op = OPCODES[int(parts[0], base=2)]
    jump
    return f'{op} {jump}'


def translate(input: Dict):
    commands = map(hex2bin, input['text'])

    result = []
    for command in commands:
        command_type = check_type(command)

        if command_type == 'R':
            translated = translate_r_command(command)
        elif command_type == 'I':
            translated = translate_i_command(command)
        elif command_type == 'J':
            translated = translate_j_command(command)
        
        result.append(translated)
    return '\n'.join(result)