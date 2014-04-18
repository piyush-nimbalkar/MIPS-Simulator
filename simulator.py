from collections import deque
from instruction import *
from executable import *
from config import *


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


def simulate_run():
    instruction_queue = deque([])
    clock_cycle = 1
    instruction_count = 1

    instruction_queue.appendleft(Executable(INSTRUCTIONS[0]))

    while len(instruction_queue) > 0:
        print('------- End of Clock Cycle %s -------\n' % str(clock_cycle))
        for i in range(0, len(instruction_queue)):
            instruction = instruction_queue.pop()
            instruction.continue_execution()

            if instruction.current_stage != Executable.write_back:
                instruction_queue.appendleft(instruction)

        if STAGE['IF'] == 0 and instruction_count < len(INSTRUCTIONS):
            instruction_queue.appendleft(Executable(INSTRUCTIONS[instruction_count]))
            instruction_count += 1

        clock_cycle += 1


if  __name__ == '__main__':
    parse('inst.txt')
    parse_registers('reg.txt')
    parse_data('data.txt')
    simulate_run()
