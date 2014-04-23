from config import *


class Instruction:
    """ Structure to store the instruction
    """

    count = 0

    def __init__(self, instr_name, operands):
        self._full_name = instr_name  + ' ' + ', '.join(operands)
        self.name = instr_name
        self._store_registers(operands)
        self.address = Instruction.count * WORD_SIZE
        Instruction.count += 1


    def __str__(self):
        return self._full_name


    def type(self, name):
        if name in ['LW', 'SW', 'L.D', 'S.D']:
            return 'DATA'
        elif name in ['J', 'BEQ', 'BNE']:
            return 'BRANCH'
        elif name == 'HLT':
            return 'SPECIAL'
        else:
            return 'ALU'


    def functional_unit(self):
        if self.name in ['ADD.D', 'SUB.D']:
            return 'FP_ADD'
        elif self.name == 'MUL.D':
            return 'FP_MUL'
        elif self.name == 'DIV.D':
            return 'FP_DIV'
        elif self.name in ['J', 'BNE', 'BEQ', 'HLT']:
            return 'NONE'
        else:
            return 'IU'


    def _store_registers(self, operands_):
        operands = self._extract_operands(filter(None, operands_))
        self.dest_reg = ''
        self.src_reg = []
        self.immediate = ''
        self.offset = ''
        if self.name == 'HLT':
            return
        if self.name not in  ['SW', 'S.D', 'J', 'BNE', 'BEQ']:
            self.dest_reg = operands[0]
        if self.name in ['LW', 'L.D']:
            self.offset = operands[1]
            self.src_reg = [operands[2]]
        elif self.name in ['SW', 'S.D']:
            self.offset = operands[1]
            self.src_reg = [operands[2]]
        elif self.name in ['DADDI', 'DSUBI', 'ANDI', 'ORI']:
            self.src_reg = operands[:1]
            self.immediate = operands[2]
        elif self.name in ['BNE', 'BEQ']:
            self.src_reg = [operands[0]]
            self.immediate = operands[2]
        elif self.name in ['J']:
            self.immediate = operands[0]
        else:
            self.src_reg = operands[1:]


    def _extract_operands(self, operands_):
        if len(operands_) > 1 and '(' in operands_[1]:
            operands = [operands_[0]]
            operands.append(operands_[1].split('(')[0])
            operands.append(operands_[1].split('(')[1].split(')')[0])
        else:
            operands = operands_
        return operands


    def set_immediate(self, value):
        self.immediate = value
