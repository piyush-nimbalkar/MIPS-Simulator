from config import *
import executable


class Stage: pass


class FetchStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['IF'] = 1
        print(self.instruction.name + ' in IF')

    def next(self):
        if STAGE['ID'] == 0:
            STAGE['IF'] = 0
            return DecodeStage(self.instruction)
        return self


class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['ID'] = 1
        print(instruction.name + ' in ID')

    def next(self):
        if STAGE['EX'] == 0:
            STAGE['ID'] = 0
            return ExecuteStage(self.instruction)
        return self


class ExecuteStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction
        self.cycles = 3

    def run(self, instruction):
        STAGE['EX'] = 1
        self.cycles -= 1
        print(instruction.name + ' in EX')

    def next(self):
        if self.cycles == 0 and STAGE['WB'] == 0:
            STAGE['EX'] = 0
            return executable.Executable.write_back
        return self


class WriteBackStage(Stage):
    def run(self, instruction):
        STAGE['WB'] = 1
        print(instruction.name + ' in WB!  \m/')

    def next(self):
        STAGE['WB'] = 0
        return None
