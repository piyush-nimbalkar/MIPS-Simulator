from config import *
from hazard import *
from icache import *
from dcache import *
import executable


class Stage:
    def __init__(self, instruction):
        self.instruction = instruction
        self.hazard = Hazard()



class FetchStage(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.name = 'IF'
        self.cache_hit, self.cycles = ICache.read(self.instruction.address)


    def run(self, instruction):
        STAGE['IF'] = BUSY

        if not self.cache_hit and STAGE['DBUS'] == FREE and self.cycles > 0:
            STAGE['IBUS'] = BUSY

        if not self.cache_hit and MemoryStage.first_bus_access:
            STAGE['IBUS'] = BUSY
            STAGE['DBUS'] = FREE
            MemoryStage.first_bus_access = False

        if self.cache_hit or STAGE['IBUS'] == BUSY:
            self.cycles -= 1


    def next(self):
        if self.cycles == 0:
            STAGE['IBUS'] = FREE

        if self.cycles <= 0 and REGISTER['FLUSH']:
            STAGE['IF'] = FREE
            STAGE['IBUS'] = FREE
            REGISTER['FLUSH'] = False
            return None

        if self.cycles <= 0 and STAGE['ID'] == FREE:
            STAGE['IF'] = FREE
            return DecodeStage(self.instruction)

        return self



class DecodeStage(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.name = 'ID'


    def run(self, instruction):
        STAGE['ID'] = BUSY


    def next(self):
        func_unit = self.instruction.functional_unit()
        self._detect_hazard(func_unit)

        if func_unit == 'NONE' and not self._is_hazard(func_unit):
            self._execute_branch_instruction()
            STAGE['ID'] = FREE
            return None

        if not self._is_hazard(func_unit):
            STAGE['ID'] = FREE
            return self._execution_stage(func_unit)

        return self


    def _execution_stage(self, func_unit):
        if func_unit == 'FP_ADD':
            return FPAddStage(self.instruction)

        elif func_unit == 'FP_MUL':
            return FPMulStage(self.instruction)

        elif func_unit == 'FP_DIV':
            return FPDivStage(self.instruction)

        else:
            return ExecuteStage(self.instruction)


    def _execute_branch_instruction(self):
        if self.instruction.name == 'J':
            REGISTER['PC'] = self.instruction.immediate / 4
            REGISTER['FLUSH'] = True

        elif self.instruction.name == 'BEQ':
            if REGISTER[self.instruction.src_reg[0]] == REGISTER[self.instruction.src_reg[1]]:
                REGISTER['PC'] = self.instruction.immediate / 4
                REGISTER['FLUSH'] = True

        elif self.instruction.name == 'BNE':
            if REGISTER[self.instruction.src_reg[0]] != REGISTER[self.instruction.src_reg[1]]:
                REGISTER['PC'] = self.instruction.immediate / 4
                REGISTER['FLUSH'] = True


    def _detect_hazard(self, func_unit):
        if not self._is_hazard(func_unit):
            return

        self.hazard.waw = False
        if self.instruction.dest_reg != '' and REGISTER_STATUS[self.instruction.dest_reg] == BUSY:
            self.hazard.waw = True

        self.hazard.raw = False
        for reg in self.instruction.src_reg:
            if REGISTER_STATUS[reg] == BUSY:
                self.hazard.raw = True

        self.hazard.struct = False
        if func_unit != 'NONE' and STAGE[func_unit] == BUSY:
            self.hazard.struct = True


    def _is_hazard(self, func_unit):
        if self.instruction.dest_reg != '' and REGISTER_STATUS[self.instruction.dest_reg] == BUSY:
            return True

        for reg in self.instruction.src_reg:
            if REGISTER_STATUS[reg] == BUSY:
                return True

        if func_unit != 'NONE' and STAGE[func_unit] == BUSY:
            return True

        return False



class ExecuteStage(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.name = 'EX'


    def run(self, instruction):
        if STAGE['IU'] != BUSY:
            self._block_register()
            self._execute()

        STAGE['IU'] = BUSY


    def next(self):
        # if STAGE['MEM'] == FREE and not self._bus_hazard():
        if STAGE['MEM'] == FREE:
            STAGE['IU'] = FREE
            return MemoryStage(self.instruction)

        self.hazard.struct = True
        return self


    def _bus_hazard(self):
        address = 0
        if self.instruction.name in ['LW', 'L.D']:
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[0]]
        elif self.instruction.name in ['SW', 'S.D']:
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[1]]

        if self.instruction.name in ['LW', 'L.D', 'SW', 'S.D']:
            if not DCache.is_hit(address) and STAGE['IBUS'] == BUSY:
                return True
        return False


    def _execute(self):
        instr = self.instruction

        if instr.name == 'DADD':
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

    first_bus_access = False

    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.stalled_for_ibus = False
        self.first_word_hit = True
        self.second_word_hit = True
        self.first_word_cycles, self.second_word_cycles = self._calc_memory_cycles()


    def run(self, instruction):
        if not self.stalled_for_ibus:
            if not self.first_word_hit:
                MemoryStage.first_bus_access = True
                self.stalled_for_ibus = True
            if not self.second_word_hit and self.first_word_cycles == 0:
                MemoryStage.first_bus_access = True
                self.stalled_for_ibus = True
        else:
            MemoryStage.first_bus_access = False

        if MemoryStage.first_bus_access and STAGE['IBUS'] == BUSY:
            if not self.first_word_hit:
                self.first_word_cycles -= 1
            elif not self.second_word_hit:
                self.second_word_cycles -= 1

        if self.first_word_cycles == 0:
            if not self.second_word_hit and STAGE['IBUS'] == FREE:
                STAGE['DBUS'] = BUSY

            if self.second_word_hit or STAGE['DBUS'] == BUSY:
                self.second_word_cycles -= 1

        STAGE['MEM'] = BUSY

        if not self.first_word_hit and STAGE['IBUS'] == FREE and self.first_word_cycles > 0:
            STAGE['DBUS'] = BUSY

        if (self.first_word_hit or STAGE['DBUS'] == BUSY) and self.first_word_cycles > 0:
            self.first_word_cycles -= 1


    def next(self):
        if not self.first_word_hit and self.first_word_cycles == 0 and self.second_word_hit:
            STAGE['DBUS'] = FREE

        if not self.second_word_hit and self.second_word_cycles == 0:
            STAGE['DBUS'] = FREE

        if self.second_word_cycles < 0:
            self.hazard.struct = True

        if (self.first_word_cycles + self.second_word_cycles) <= 0 and STAGE['WB'] == FREE:
            STAGE['MEM'] = FREE
            return WriteBackStage(self.instruction)

        return self


    def _calc_memory_cycles(self):
        if self.instruction.name == 'LW':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[0]]
            self.first_word_hit, REGISTER[self.instruction.dest_reg], cycles = DCache.read(address)
            return cycles, 0

        elif self.instruction.name == 'L.D':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[0]]
            self.first_word_hit, word, first_word_read_time = DCache.read(address)
            self.second_word_hit, word, second_word_read_time = DCache.read(address + 4)
            return first_word_read_time, second_word_read_time

        elif self.instruction.name == 'SW':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[1]]
            self.first_word_hit, cycles = DCache.write(address, REGISTER[self.instruction.src_reg[0]])
            return cycles, 0

        elif self.instruction.name == 'S.D':
            address = int(self.instruction.offset) + REGISTER[self.instruction.src_reg[1]]
            self.first_word_hit, first_word_write_time = DCache.write(address, 0, False)
            self.second_word_hit, second_word_write_time = DCache.write(address + 4, 0, False)
            return first_word_write_time, second_word_write_time

        return 1, 0



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
            return WriteBackStage(self.instruction)

        return self



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
            return WriteBackStage(self.instruction)

        return self



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
            return WriteBackStage(self.instruction)

        return self



class WriteBackStage(Stage):
    def __init__(self, instruction):
        Stage.__init__(self, instruction)
        self.name = 'WB'


    def run(self, instruction):
        STAGE['WB'] = BUSY


    def next(self):
        STAGE['WB'] = FREE
        self._unblock_register()
        return None


    def _unblock_register(self):
        if self.instruction.dest_reg != '':
            REGISTER_STATUS[self.instruction.dest_reg] = FREE
