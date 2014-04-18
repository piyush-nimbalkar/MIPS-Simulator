from config import *


class Instruction:
    """ Structure to store the instruction
    """

    count = 0

    def __init__(self, instr_name, operands):
        self.name = instr_name.upper()
        self.type = self.__instruction_type(self.name)
        self.func_unit = self.__functional_unit(self.name)
        self.__store_registers(self.name, operands)
        self.address = Instruction.count * WORD_SIZE
        Instruction.count += 1


    def __instruction_type(self, name):
        if name in ['LW', 'SW', 'L.D', 'S.D']:
            return 'DATA'
        elif name in ['J', 'BEQ', 'BNE']:
            return 'BRANCH'
        elif name == 'HLT':
            return 'SPECIAL'
        else:
            return 'ALU'


    def __functional_unit(self, name):
        if name in ['ADD.D', 'SUB.D']:
            return 'FP_ADD'
        elif name == 'MUL.D':
            return 'FP_MUL'
        elif name == 'DIV.D':
            return 'FP_DIV'
        elif name in ['J', 'BNE', 'BEQ', 'HLT']:
            return 'NONE'
        else:
            return 'INTEGER'


    def __store_registers(self, name, operands):
        operands = [x.upper() for x in operands]
        self.dest_reg = ''
        self.src_reg = []
        self.immediate = ''
        self.offset = ''
        for op in operands:
            if name not in  ['SW', 'S.D', 'J', 'BNE', 'BEQ']:
                self.dest_reg = operands[0].strip(',')

            if name in ['LW', 'L.D']:
                self.offset = operands[1].split('(')[0]
                self.src_reg = [operands[1].split('(')[1].split(')')[0]]
            elif name in ['SW', 'S.D']:
                self.offset = operands[1].split('(')[0]
                self.src_reg = [operands[0].strip(','), operands[1].split('(')[1].split(')')[0]]
            elif name in ['DADDI', 'DSUBI', 'ANDI', 'ORI']:
                self.src_reg = [operands[1].strip(',')]
                self.immediate = operands[2]
            elif name in ['BNE', 'BEQ']:
                self.src_reg = [operands[0].strip(','), operands[1].strip(',')]
                self.immediate = operands[2]
            elif name in ['J']:
                self.immediate = operands[0]
            else:
                self.src_reg = [operands[1].strip(','), operands[2].strip(',')]


    def set_immediate(self, value):
        self.immediate = value
