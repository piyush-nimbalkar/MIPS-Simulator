import stage

class Executable():
    def __init__(self, instruction):
        self.current_stage = stage.FetchStage(instruction)
        self._instruction = instruction
        self.current_stage.run(self._instruction)

    def continue_execution(self):
        self.current_stage = self.current_stage.next()
        self.current_stage.run(self._instruction)


Executable.write_back = stage.WriteBackStage()
