from result import *
import stage



class Executable():
    def __init__(self, instruction, cycle):
        self.current_stage = stage.FetchStage(instruction)
        self._instruction = instruction
        self.current_stage.run(self._instruction)
        self.result = Result(instruction, cycle)


    def continue_execution(self):
        previous_stage = self.current_stage
        self.current_stage = previous_stage.next()

        if previous_stage != self.current_stage:
            if previous_stage.hazard.struct:
                self.result.struct_hazard = True
            if previous_stage.hazard.raw:
                self.result.raw_hazard = True
            if previous_stage.hazard.waw:
                self.result.waw_hazard = True

        if self.current_stage == None:
            return False

        self.__update_cycles(previous_stage, self.current_stage)
        self.current_stage.run(self._instruction)
        return True


    def __update_cycles(self, previous_stage, current_stage):
        if previous_stage.name == 'IF' and current_stage.name == 'IF':
            self.result.IF_cycle += 1
        elif previous_stage.name == 'IF' and current_stage.name == 'ID':
            self.result.ID_cycle = self.result.IF_cycle + 1
        elif previous_stage.name == 'ID' and current_stage.name == 'ID':
            self.result.ID_cycle += 1
        elif previous_stage.name == 'ID' and current_stage.name == 'EX':
            self.result.EX_cycle = self.result.ID_cycle + 1
        elif previous_stage.name == 'EX' and current_stage.name == 'EX':
            self.result.EX_cycle += 1
        elif previous_stage.name == 'EX' and current_stage.name == 'WB':
            self.result.WB_cycle = self.result.EX_cycle + 1
