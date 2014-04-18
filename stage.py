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
        return DecodeStage(self.instruction)


class DecodeStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['IF'] = 0
        STAGE['ID'] = 1
        print(instruction.name + ' in ID')

    def next(self):
        return ExecuteStage(self.instruction)


class ExecuteStage(Stage):
    def __init__(self, instruction):
        self.instruction = instruction

    def run(self, instruction):
        STAGE['ID'] = 0
        STAGE['EX'] = 1
        print(instruction.name + ' in EX')

    def next(self):
        return executable.Executable.write_back


class WriteBackStage(Stage):
    def run(self, instruction):
        STAGE['EX'] = 0
        STAGE['WB'] = 1
        print(instruction.name + ' in WB!  \m/')

    def next(self):
        return None
