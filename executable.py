import stage

class Executable():
    def __init__(self, instruction):
        self.current_stage = stage.FetchStage(instruction)
        self._instruction = instruction
        self.current_stage.run(self._instruction)

    def continue_execution(self):
        self.current_stage = self.current_stage.next()
        if self.current_stage == None:
            return False
        self.current_stage.run(self._instruction)
        return True


Executable.write_back = stage.WriteBackStage()
