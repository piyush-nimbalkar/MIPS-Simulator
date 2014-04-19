from config import *
import executable


class Stage: pass



class FetchStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'IF'
        self.struct_hazard = False

    def run(self, instruction):
        STAGE['IF'] = BUSY

    def next(self):
        if STAGE['ID'] == FREE:
            STAGE['IF'] = FREE
            return DecodeStage(self.instruction), self.struct_hazard
        return self, self.struct_hazard



class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'ID'
        self.struct_hazard = False

    def run(self, instruction):
        STAGE['ID'] = BUSY

    def next(self):
        func_unit = self.instruction.func_unit
        if func_unit == 'NONE':
            STAGE['ID'] = FREE
            return None, self.struct_hazard
        if STAGE[func_unit] == FREE:
            STAGE['ID'] = FREE
            return self.__execution_stage(), self.struct_hazard
        self.struct_hazard = True
        return self, self.struct_hazard

    def __execution_stage(self):
        func_unit = self.instruction.func_unit
        if func_unit == 'FP_ADD':
            return FPAddStage(self.instruction)
        elif func_unit == 'FP_MUL':
            return FPMulStage(self.instruction)
        elif func_unit == 'FP_DIV':
            return FPDivStage(self.instruction)
        else:
            return ExecuteStage(self.instruction)



class ExecuteStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'EX'
        self.struct_hazard = False

    def run(self, instruction):
        if STAGE['IU'] != BUSY:
            self.__execute()
        STAGE['IU'] = BUSY

    def next(self):
        if STAGE['MEM'] == FREE:
            STAGE['IU'] = FREE
            return MemoryStage(self.instruction), self.struct_hazard
        self.struct_hazard = True
        return self, self.struct_hazard

    def __execute(self):
        instr = self.instruction
        if instr.name == 'LW':
            REGISTER[instr.dest_reg] = DATA[REGISTER[instr.src_reg[0]] + int(instr.offset)]
        elif instr.name == 'DADD':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] + REGISTER[instr.src_reg[1]]
        elif instr.name == 'DADDI':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] + int(instr.immediate)
        elif instr.name == 'DSUB':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] - REGISTER[instr.src_reg[1]]
        elif instr.name == 'DSUBI':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] - int(instr.immediate)
        elif instr.name == 'AND':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] & REGISTER[instr.src_reg[1]]
        elif instr.name == 'ANDI':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] & int(instr.immediate)
        elif instr.name == 'OR':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] | REGISTER[instr.src_reg[1]]
        elif instr.name == 'ORI':
            REGISTER[instr.dest_reg] = REGISTER[instr.src_reg[0]] | int(instr.immediate)



class MemoryStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)

    def run(self, instruction):
        STAGE['MEM'] = BUSY

    def next(self):
        if STAGE['WB'] == FREE:
            STAGE['MEM'] = FREE
            return executable.Executable.write_back, self.struct_hazard
        self.struct_hazard = True
        return self, self.struct_hazard



class FPAddStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_ADD['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_ADD['CYCLES']:
            STAGE['FP_ADD'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.struct_hazard = True
        if FP_ADD['PIPELINED']:
            STAGE['FP_ADD'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_ADD'] = FREE
            return executable.Executable.write_back, self.struct_hazard
        return self, self.struct_hazard



class FPMulStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_MUL['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_MUL['CYCLES']:
            STAGE['FP_MUL'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.struct_hazard = True
        if FP_MUL['PIPELINED']:
            STAGE['FP_MUL'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_MUL'] = FREE
            return executable.Executable.write_back, self.struct_hazard
        return self, self.struct_hazard



class FPDivStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_DIV['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_DIV['CYCLES']:
            STAGE['FP_DIV'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.struct_hazard = True
        if FP_DIV['PIPELINED']:
            STAGE['FP_DIV'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_DIV'] = FREE
            return executable.Executable.write_back, self.struct_hazard
        return self, self.struct_hazard



class WriteBackStage(Stage):
    def __init__(self):
        self.name = 'WB'
        self.struct_hazard = False

    def run(self, instruction):
        STAGE['WB'] = BUSY

    def next(self):
        STAGE['WB'] = FREE
        return None, self.struct_hazard
