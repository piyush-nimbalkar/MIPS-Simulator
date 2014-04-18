from config import *
import executable


class Stage:
    def run(self, instruction):
        assert 0, "run not implemented"

    def next(self, input):
        assert 0, "next not implemented"


class FetchStage(Stage):
    def run(self, instruction):
        STAGE['IF'] = 1
        print(instruction.name + ' in IF')

    def next(self):
        return executable.Executable.decode

class DecodeStage(Stage):
    def run(self, instruction):
        STAGE['IF'] = 0
        STAGE['ID'] = 1
        print(instruction.name + ' in ID')

    def next(self):
        return executable.Executable.execute

class ExecuteStage(Stage):
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
        return executable.Executable.done
