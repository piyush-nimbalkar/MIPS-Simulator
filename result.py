class Result:
    def __init__(self, instruction, cycle = 0):
        self.instruction = instruction
        self.IF_cycle = cycle
        self.ID_cycle = 0
        self.EX_cycle = 0
        self.WB_cycle = 0
        self.struct_hazard = False
        self.raw_hazard = False
        self.waw_hazard = False


    def display(self):
        print(self.instruction.name + '\t'),
        print(str(self.IF_cycle) + '\t'),
        print(str(self.ID_cycle) + '\t'),

        if self.EX_cycle != 0:
            print(str(self.EX_cycle) + '\t'),
        else:
            print('-\t'),

        if self.WB_cycle != 0:
            print(str(self.WB_cycle) + '\t'),
        else:
            print('-\t'),

        if self.struct_hazard:
            print('Y\t'),
        else:
            print('N\t'),

        if self.raw_hazard:
            print('Y\t'),
        else:
            print('N\t'),

        if self.waw_hazard:
            print('Y')
        else:
            print('N')
