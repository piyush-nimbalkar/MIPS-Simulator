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
        self.cycles = 3

    def run(self, instruction):
        STAGE['EX'] = True
        self.cycles -= 1
        print(instruction.name + ' in EX')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == False:
            STAGE['EX'] = False
            return executable.Executable.write_back
        return self


class WriteBackStage(Stage):
    def run(self, instruction):
        STAGE['WB'] = True
        print(instruction.name + ' in WB!  \m/')

    def next(self):
        STAGE['WB'] = False
        return None
