class Instruction:
    """ Structure to store the instruction
    """

    def __init__(self, instr_name, operands):
        self.name = instr_name
        self.type = self.__instruction_type(instr_name)
        self.operands = operands


    def __instruction_type(self, name):
        if name in ['LW', 'SW', 'L.D', 'S.D']:
            return 'DATA'
        elif name in ['J', 'BEQ', 'BNE']:
            return 'BRANCH'
        elif name == 'HLT':
            return 'SPECIAL'
        else:
            return 'ALU'


def parse(filename):
    file = open(filename, 'r')
    instructions = []
    for line in file:
        instruction = filter(None, line.strip().split(' '))
        if (':' in instruction[0]):
            instructions.append(Instruction(instruction[1], instruction[2:len(instruction)]))
        else:
            instructions.append(Instruction(instruction[0], instruction[1:len(instruction)]))


    for obj in instructions:
        print(obj.name),
        print(obj.operands),
        print(obj.type)


def main():
    parse("inst.txt")


if  __name__ == '__main__':
    main()
