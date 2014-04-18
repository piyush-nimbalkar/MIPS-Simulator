from config import *
import executable


class Stage: pass



class FetchStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'IF'

    def run(self, instruction):
        STAGE['IF'] = True

    def next(self):
        if STAGE['ID'] == False:
            STAGE['IF'] = False
            return DecodeStage(self.instruction)
        return self



class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.name = 'ID'

    def run(self, instruction):
        STAGE['ID'] = True

    def next(self):
        func_unit = self.instruction.func_unit
        if func_unit == 'NONE':
            STAGE['ID'] = False
            return None
        if STAGE[func_unit] == False:
            STAGE['ID'] = False
            return self.__execution_stage()
        return self

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
        self.cycles = 2
        self.name = 'EX'

    def run(self, instruction):
        STAGE['INTEGER'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['INTEGER'] = False
            return executable.Executable.write_back
        return self



class FPAddStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 4
        self.name = 'EX'

    def run(self, instruction):
        STAGE['FP_ADD'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_ADD'] = False
            return executable.Executable.write_back
        return self



class FPMulStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 6
        self.name = 'EX'

    def run(self, instruction):
        STAGE['FP_MUL'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_MUL'] = False
            return executable.Executable.write_back
        return self



class FPDivStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 20
        self.name = 'EX'

    def run(self, instruction):
        STAGE['FP_DIV'] = True
        self.cycles -= 1

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_DIV'] = False
            return executable.Executable.write_back
        return self



class WriteBackStage(Stage):
    def __init__(self):
        self.name = 'WB'

    def run(self, instruction):
        STAGE['WB'] = True

    def next(self):
        STAGE['WB'] = False
        return None
