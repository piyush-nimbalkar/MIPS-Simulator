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
        if STAGE['EX'] == False:
            STAGE['ID'] = False
            return ExecuteStage(self.instruction)
        return self



class ExecuteStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.cycles = self.__calculate_cycles()

    def run(self, instruction):
        STAGE['EX'] = True
        self.cycles -= 1
        print(instruction.name + ' in EX')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['EX'] = False
            return executable.Executable.write_back
        return self

    def __calculate_cycles(self):
        func_unit = self.instruction.func_unit
        if func_unit == 'FP_ADD':
            return 4
        elif func_unit == 'FP_MUL':
            return 6
        elif func_unit == 'FP_DIV':
            return 20
        elif func_unit == 'INTEGER':
            return 2
        else:
            return 1



class WriteBackStage(Stage):
    def run(self, instruction):
        STAGE['WB'] = True
        print(instruction.name + ' in WB!  \m/')

    def next(self):
        STAGE['WB'] = False
        return None
