from config import *
import executable


class Stage: pass



class FetchStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['IF'] = True
        print(self.instruction.name + ' in IF')

    def next(self):
        if STAGE['ID'] == False:
            STAGE['IF'] = False
            return DecodeStage(self.instruction)
        return self



class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['ID'] = True
        print(instruction.name + ' in ID')

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

    def run(self, instruction):
        STAGE['INTEGER'] = True
        self.cycles -= 1
        print(instruction.name + ' in EX')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['INTEGER'] = False
            return executable.Executable.write_back
        return self



class FPAddStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 4

    def run(self, instruction):
        STAGE['FP_ADD'] = True
        self.cycles -= 1
        print(instruction.name + ' in FP_ADD')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_ADD'] = False
            return executable.Executable.write_back
        return self



class FPMulStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 6

    def run(self, instruction):
        STAGE['FP_MUL'] = True
        self.cycles -= 1
        print(instruction.name + ' in FP_MUL')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_MUL'] = False
            return executable.Executable.write_back
        return self



class FPDivStage(ExecuteStage):
    def __init__(self, instruction):
        ExecuteStage.__init__(self, instruction)
        self.cycles = 20

    def run(self, instruction):
        STAGE['FP_DIV'] = True
        self.cycles -= 1
        print(instruction.name + ' in FP_DIV')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['FP_DIV'] = False
            return executable.Executable.write_back
        return self



class WriteBackStage(Stage):
    def run(self, instruction):
        STAGE['WB'] = True
        print(instruction.name + ' in WB!  \m/')

    def next(self):
        STAGE['WB'] = False
        return None
