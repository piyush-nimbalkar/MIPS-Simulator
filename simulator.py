from collections import deque


DATA = {}
REGISTER = {}
WORD_SIZE = 4
MEMORY_BASE_ADDRESS = 256
INSTRUCTIONS = []


class Instruction:
    """ Structure to store the instruction
    """

    count = 0

    def __init__(self, instr_name, operands):
        self.name = instr_name
        self.type = self.__instruction_type(instr_name)
        self.func_unit = self.__functional_unit(instr_name)
        self.__store_registers(instr_name, operands)
        self.address = Instruction.count * WORD_SIZE
        Instruction.count += 1


    def __instruction_type(self, name):
        if name in ['LW', 'SW', 'L.D', 'S.D']:
            return 'DATA'
        elif name in ['J', 'BEQ', 'BNE']:
            return 'BRANCH'
        elif name == 'HLT':
            return 'SPECIAL'
        else:
            return 'ALU'


    def __functional_unit(self, name):
        if name in ['ADD.D', 'SUB.D']:
            return 'FP_ADD'
        elif name == 'MUL.D':
            return 'FP_MUL'
        elif name == 'DIV.D':
            return 'FP_DIV'
        elif name in ['J', 'BNE', 'BEQ', 'HLT']:
            return 'NONE'
        else:
            return 'INTEGER'


    def __store_registers(self, name, operands):
        self.dest_reg = ''
        self.src_reg = []
        self.immediate = ''
        self.offset = ''
        for op in operands:
            if name not in  ['SW', 'S.D', 'J', 'BNE', 'BEQ']:
                self.dest_reg = operands[0].strip(',')

            if name in ['LW', 'L.D']:
                self.offset = operands[1].split('(')[0]
                self.src_reg = [operands[1].split('(')[1].split(')')[0]]
            elif name in ['SW', 'S.D']:
                self.offset = operands[1].split('(')[0]
                self.src_reg = [operands[0].strip(','), operands[1].split('(')[1].split(')')[0]]
            elif name in ['DADDI', 'DSUBI', 'ANDI', 'ORI']:
                self.src_reg = [operands[1].strip(',')]
                self.immediate = operands[2]
            elif name in ['BNE', 'BEQ']:
                self.src_reg = [operands[0].strip(','), operands[1].strip(',')]
                self.immediate = operands[2]
            elif name in ['J']:
                self.immediate = operands[0]
            else:
                self.src_reg = [operands[1].strip(','), operands[2].strip(',')]


    def set_immediate(self, value):
        self.immediate = value



def parse(filename):
    file = open(filename, 'r')
    labels = {}

    for line in file:
        instruction = filter(None, line.strip().split(' '))
        if ':' in instruction[0]:
            labels[instruction[0].strip(':')] = Instruction.count * WORD_SIZE
            INSTRUCTIONS.append(Instruction(instruction[1], instruction[2:len(instruction)]))
        else:
            INSTRUCTIONS.append(Instruction(instruction[0], instruction[1:len(instruction)]))

    for instr in INSTRUCTIONS:
        if instr.immediate in labels.keys():
            instr.set_immediate(labels[instr.immediate])


def parse_registers(filename):
    file = open(filename, 'r')
    reg_count = 0

    for line in file:
        value = 0
        count = (WORD_SIZE * 8) - 1
        for i in line.strip():
            value += pow(2, count) * int(i)
            count -= 1
        REGISTER['R' + str(reg_count)] = value
        reg_count += 1


def parse_data(filename):
    file = open(filename, 'r')
    word_count = 0

    for line in file:
        value = 0
        count = (WORD_SIZE * 8) - 1
        for i in line.strip():
            value += pow(2, count) * int(i)
            count -= 1
        DATA[MEMORY_BASE_ADDRESS + word_count] = value
        word_count += 1



class Status():
    """ To store the status of the instruction
    """

    def __init__(self, instr):
        self._instr = instr
        self._stage = 'IF'


    def update(self):
        if self._stage == 'IF' and STAGE['ID'] == 0:
            self._stage = 'ID'
            STAGE['IF'] = 0
            STAGE['ID'] = 1
        elif self._stage == 'ID' and STAGE['EX'] == 0:
            self._stage = 'EX'
            STAGE['ID'] = 0
            STAGE['EX'] = 1
        elif self._stage == 'EX' and STAGE['WB'] == 0:
            self._stage = 'WB'
            STAGE['EX'] = 0
            STAGE['WB'] = 1
        elif self._stage == 'WB':
            self._stage = 'DONE'
            STAGE['WB'] = 0


STAGE = {
    'IF': 0,
    'ID': 0,
    'EX': 0,
    'WB': 0
}

def simulate_run():
    clock_cycle = 1
    instr_count = 0
    pending_queue = deque([])

    while True:
        print('\nClock: ' + str(clock_cycle))
        for i in range(0, len(pending_queue)):
            status = pending_queue.pop()
            status.update()
            if status._stage != 'DONE':
                print(status._instr.name + ' in ' +  status._stage + ' stage')
                pending_queue.appendleft(status)
            else:
                print(status._instr.name + ' done with WB stage')

        if STAGE['IF'] == 0:
            instr = INSTRUCTIONS[instr_count]
            print(instr.name + ' in IF stage')
            pending_queue.appendleft(Status(instr))
            STAGE['IF'] = 1
            instr_count += 1

        if instr.name == 'HLT':
            break;

        clock_cycle += 1



def main():
    parse('inst.txt')
    parse_registers('reg.txt')
    parse_data('data.txt')
    simulate_run()


if  __name__ == '__main__':
    main()
