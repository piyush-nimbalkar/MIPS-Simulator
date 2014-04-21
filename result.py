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


    def __str__(self):
        string = self.instruction.name + '\t'
        string += str(self.IF_cycle) + '\t'
        string += str(self.ID_cycle) + '\t'

        if self.EX_cycle != 0:
            string += str(self.EX_cycle) + '\t'
        else:
            string += '-\t'

        if self.WB_cycle != 0:
            string += str(self.WB_cycle) + '\t'
        else:
            string += '-\t'

        if self.raw_hazard:
            string += ' Y\t'
        else:
            string += ' -\t'

        string += ' -\t'

        if self.waw_hazard:
            string += ' Y\t'
        else:
            string += ' -\t'

        if self.struct_hazard:
            string += ' Y'
        else:
            string += ' -'

        return string
