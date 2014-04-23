from config import *
from hazard import *
from icache import *
from dcache import *
import executable


class Stage: pass



class FetchStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'IF'
        self.cycles = ICache.read(self.instruction.address)
        self.hazard = Hazard()

    def run(self, instruction):
        STAGE['IF'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles <= 0 and STAGE['ID'] == FREE:
            STAGE['IF'] = FREE
            return DecodeStage(self.instruction), self.hazard
        return self, self.hazard



class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'ID'
        self.hazard = Hazard()

    def run(self, instruction):
        STAGE['ID'] = BUSY

    def next(self):
        func_unit = self.instruction.functional_unit()
        self._detect_hazard(func_unit)
        if func_unit == 'NONE' and not self._is_hazard():
            STAGE['ID'] = FREE
            return None, self.hazard
        if func_unit != 'NONE' and STAGE[func_unit] == FREE and not self._is_hazard():
            STAGE['ID'] = FREE
            return self._execution_stage(func_unit), self.hazard
        return self, self.hazard

    def _execution_stage(self, func_unit):
        if func_unit == 'FP_ADD':
            return FPAddStage(self.instruction)
        elif func_unit == 'FP_MUL':
            return FPMulStage(self.instruction)
        elif func_unit == 'FP_DIV':
            return FPDivStage(self.instruction)
        else:
            return ExecuteStage(self.instruction)

    def _detect_hazard(self, func_unit):
        if self.instruction.dest_reg != '' and REGISTER_STATUS[self.instruction.dest_reg] == BUSY:
            self.hazard.waw = True
        for reg in self.instruction.src_reg:
            if REGISTER_STATUS[reg] == BUSY:
                self.hazard.raw = True
        if func_unit != 'NONE' and STAGE[func_unit] == BUSY:
            self.hazard.struct = True

    def _is_hazard(self):
        if self.instruction.dest_reg != '' and REGISTER_STATUS[self.instruction.dest_reg] == BUSY:
            return True
        for reg in self.instruction.src_reg:
            if REGISTER_STATUS[reg] == BUSY:
                return True
        return False



class ExecuteStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'EX'
        self.hazard = Hazard()

    def run(self, instruction):
        if STAGE['IU'] != BUSY:
            self._block_register()
            self._execute()
        STAGE['IU'] = BUSY

    def next(self):
        if STAGE['MEM'] == FREE:
            STAGE['IU'] = FREE
            return MemoryStage(self.instruction), self.hazard
        self.hazard.struct = True
        return self, self.hazard

    def _execute(self):
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

    def _block_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = BUSY



class MemoryStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = self._calc_memory_cycles()

    def run(self, instruction):
        STAGE['MEM'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.hazard.struct = True
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['MEM'] = FREE
            return WriteBackStage(self.instruction), self.hazard
        return self, self.hazard

    def _calc_memory_cycles(self):
        if self.instruction.name == 'LW':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[0]]
            REGISTER[self.instruction.dest_reg], cycles = DCache.read(address)
            return cycles
        elif self.instruction.name == 'L.D':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[0]]
            word, first_word_access_time = DCache.read(address)
            word, second_word_access_time = DCache.read(address + 4)
            if second_word_access_time == ACCESS_TIME['DCACHE']:
                return first_word_access_time + 1
            else:
                return first_word_access_time + second_word_access_time
        return 1



class FPAddStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_ADD['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_ADD['CYCLES']:
            self._block_register()
            STAGE['FP_ADD'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.hazard.struct = True
        if FP_ADD['PIPELINED']:
            STAGE['FP_ADD'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_ADD'] = FREE
            return WriteBackStage(self.instruction), self.hazard
        return self, self.hazard

    def _block_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = BUSY



class FPMulStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_MUL['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_MUL['CYCLES']:
            self._block_register()
            STAGE['FP_MUL'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.hazard.struct = True
        if FP_MUL['PIPELINED']:
            STAGE['FP_MUL'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_MUL'] = FREE
            return WriteBackStage(self.instruction), self.hazard
        return self, self.hazard

    def _block_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = BUSY



class FPDivStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = FP_DIV['CYCLES']

    def run(self, instruction):
        if self.cycles == FP_DIV['CYCLES']:
            self._block_register()
            STAGE['FP_DIV'] = BUSY
        self.cycles -= 1

    def next(self):
        if self.cycles < 0:
            self.hazard.struct = True
        if FP_DIV['PIPELINED']:
            STAGE['FP_DIV'] = FREE
        if self.cycles <= 0 and STAGE['WB'] == FREE:
            STAGE['FP_DIV'] = FREE
            return WriteBackStage(self.instruction), self.hazard
        return self, self.hazard

    def _block_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = BUSY



class WriteBackStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'WB'
        self.hazard = Hazard()

    def run(self, instruction):
        STAGE['WB'] = BUSY

    def next(self):
        STAGE['WB'] = FREE
        self._unblock_register()
        return None, self.hazard

    def _unblock_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = FREE
