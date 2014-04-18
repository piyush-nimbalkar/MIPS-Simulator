class Result:
    def __init__(self, instruction, cycle = 0):
        self.instruction = instruction
        self.IF_cycle = cycle
        self.ID_cycle = 0
        self.EX_cycle = 0
        self.WB_cycle = 0


    def display(self):
        print(self.instruction.name + '\t'),
        print(str(self.IF_cycle) + '\t'),
        print(str(self.ID_cycle) + '\t'),

        if self.EX_cycle != 0:
            print(str(self.EX_cycle) + '\t'),
        else:
            print('-\t'),

        if self.WB_cycle != 0:
            print(str(self.WB_cycle))
        else:
            print('-')