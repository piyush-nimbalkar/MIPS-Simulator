from collections import deque
from instruction import *
from executable import *
from icache import *
from config import *


def parse(filename):
    file = open(filename, 'r')
    labels = {}

    for line in file:
        line = line.strip().upper()
        if ':' in line:
            instruction = line.split(':')
            labels[instruction[0].strip().upper()] = Instruction.count * WORD_SIZE
            instruction = instruction[1].strip().split(' ')
        else:
            instruction = line.split(' ')

        instruction_name = instruction[0]
        operands = ''.join(instruction[1 : len(instruction)]).split(',')
        INSTRUCTIONS.append(Instruction(instruction_name, operands))

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
        DATA[MEMORY_BASE_ADDRESS + (word_count * WORD_SIZE)] = value
        word_count += 1


def parse_config(filename):
    file = open(filename, 'r')

    for line in file:
        line = line.lower().strip()
        split_line = line.split(':')
        if 'adder' in split_line[0]:
            write_pipelining_status(FP_ADD, split_line[1])
        elif 'multiplier' in split_line[0]:
            write_pipelining_status(FP_MUL, split_line[1])
        elif 'divider' in split_line[0]:
            write_pipelining_status(FP_DIV, split_line[1])
        elif 'memory' in split_line[0]:
            ACCESS_TIME['MEMORY'] = int(split_line[1].strip())
        elif 'i-cache' in split_line[0]:
            ACCESS_TIME['ICACHE'] = int(split_line[1].strip())
        elif 'd-cache' in split_line[0]:
            ACCESS_TIME['DCACHE'] = int(split_line[1].strip())


def write_pipelining_status(fu_hash, param_string):
    params = [x.strip() for x in param_string.split(',')]
    fu_hash['CYCLES'] = int(params[0])
    if params[1] == 'yes':
        fu_hash['PIPELINED'] = True
    else:
        fu_hash['PIPELINED'] = False


def reset_register_status():
    for i in range(32):
        REGISTER_STATUS['R' + str(i)] = FREE
        REGISTER_STATUS['F' + str(i)] = FREE


def initialize_cache():
    ICache()

def simulate_run():
    instruction_queue = deque([])
    clock_cycle = 1
    instruction_count = 1
    result = []
    instruction_queue.appendleft(Executable(INSTRUCTIONS[0], clock_cycle))

    while len(instruction_queue) > 0:
        queue_size = len(instruction_queue)
        for stage in ['WB', 'EX', 'ID', 'IF']:
            for i in range(0, len(instruction_queue)):
                instruction = instruction_queue.pop()
                if instruction.current_stage.name == stage:
                    if instruction.continue_execution():
                        instruction_queue.appendleft(instruction)
                    else:
                        result.append(instruction.result)
                    queue_size -= 1
                else:
                    instruction_queue.appendleft(instruction)
            if queue_size == 0:
                break

        clock_cycle += 1

        if STAGE['IF'] == FREE and instruction_count < len(INSTRUCTIONS):
            instruction_queue.appendleft(Executable(INSTRUCTIONS[instruction_count], clock_cycle))
            instruction_count += 1


    print('-' * 86)
    print('INSTRUCTION\t\tIF\tID\tEX\tWB\tRAW\tWAR\tWAW\tSTRUCT')
    print('-' * 86)
    for row in sorted(result, key=lambda x: x.IF_cycle):
        print(row)
        print('-' * 86)



if  __name__ == '__main__':
    parse('inst.txt')
    parse_registers('reg.txt')
    parse_data('data.txt')
    parse_config('config.txt')
    initialize_cache()
    reset_register_status()
    simulate_run()
