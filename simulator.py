from collections import deque
from instruction import *
from executable import *
from icache import *
from dcache import *
from config import *
import sys


labels = {}


def parse_instructions(filename):
    file = open(filename, 'r')

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
    DCache()



def simulate_run():
    instruction_queue = deque([])
    clock_cycle = 1
    result = []
    REGISTER['PC'] = 1
    instruction_queue.appendleft(Executable(INSTRUCTIONS[0], clock_cycle))

    while len(instruction_queue) > 0:
        queue_size = len(instruction_queue)
        for stage in ['WB', 'EX', 'ID', 'IF']:
            transfer_queue = deque([])
            while len(instruction_queue) > 0:
                instruction = instruction_queue.pop()
                if instruction.current_stage.name == stage:
                    if instruction.continue_execution():
                        transfer_queue.appendleft(instruction)
                    else:
                        result.append(instruction.result)
                        if REGISTER['FLUSH']:
                            result.append(instruction_queue.pop().result)
                            STAGE['IF'] = FREE
                            STAGE['IBUS'] = FREE
                            REGISTER['FLUSH'] = False
                    queue_size -= 1
                else:
                    transfer_queue.appendleft(instruction)

            instruction_queue = transfer_queue

        clock_cycle += 1

        if STAGE['IF'] == FREE and REGISTER['PC'] < len(INSTRUCTIONS):
            instruction_queue.appendleft(Executable(INSTRUCTIONS[REGISTER['PC']], clock_cycle))
            REGISTER['PC'] += 1

    display_result(result)



def display_result(result):
    result = sorted(result, key=lambda x: x.IF_cycle)
    result[len(result) - 1].ID_cycle = 0
    print('-' * 94)
    print('\tInstruction\t\tFT\tID\tEX\tWB\tRAW\tWAR\tWAW\tStruct')
    print('-' * 94)
    for i in range(len(result)):
        found_label = False
        for label, address in labels.items():
            if result[i].instruction.address == address:
                found_label = True
                print(label + ':\t'),
        if not found_label:
            print('\t'),
        print(result[i])
    print('-' * 94)

    print("\nTotal number of access requests for instruction cache: " + str(ICache.request_count))
    print("Number of instruction cache hits: " + str(ICache.hit_count))
    print("\nTotal number of access requests for data cache: " + str(DCache.request_count))
    print("Number of data cache hits: " + str(DCache.hit_count))
    print



if  __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage: python simulator.py inst.txt data.txt reg.txt config.txt result.txt')
        exit()
    parse_instructions(sys.argv[1])
    parse_data(sys.argv[2])
    parse_registers(sys.argv[3])
    parse_config(sys.argv[4])
    initialize_cache()
    reset_register_status()
    simulate_run()
