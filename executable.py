import stage

class Executable():
    def __init__(self, instruction):
        self.current_stage = Executable.fetch
        self._instruction = instruction
        self.current_stage.run(self._instruction)

    def continue_execution(self):
        self.current_stage.run(self._instruction)


Executable.fetch = stage.FetchStage()
Executable.decode = stage.DecodeStage()
Executable.execute = stage.ExecuteStage()
Executable.write_back = stage.WriteBackStage()
