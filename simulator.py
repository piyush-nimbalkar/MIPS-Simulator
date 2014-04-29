from collections import deque
from instruction import *
from executable import *
from icache import *
from dcache import *
from config import *
import operator
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



def prioritize_for_write_back(new_queue, ex_queue):
    priority_map = {}

    for i in range(len(ex_queue)):
        ex = ex_queue.pop()

        if ex._instruction.functional_unit() == 'FP_DIV':
            if FP_DIV['PIPELINED']:
                priority_map[ex] = FP_DIV['CYCLES']
            else:
                priority_map[ex] = FP_DIV['CYCLES'] + 100

        elif ex._instruction.functional_unit() == 'FP_MUL':
            if FP_MUL['PIPELINED']:
                priority_map[ex] = FP_MUL['CYCLES']
            else:
                priority_map[ex] = FP_MUL['CYCLES'] + 100

        elif ex._instruction.functional_unit() == 'FP_ADD':
            if FP_ADD['PIPELINED']:
                priority_map[ex] = FP_ADD['CYCLES']
            else:
                priority_map[ex] = FP_ADD['CYCLES'] + 100

        else:
            priority_map[ex] = 0

    sorted_x = sorted(priority_map.iteritems(), key=operator.itemgetter(1), reverse=True)
    for element in sorted_x:
        new_queue.appendleft(element[0])

    return new_queue



def reorder_instructions(old_queue):
    new_queue = deque([])

    for i in range(len(old_queue)):
        instruction = old_queue.pop()
        if instruction.current_stage.name == 'WB':
            new_queue.appendleft(instruction)
        else:
            old_queue.appendleft(instruction)

    ex_queue = deque([])
    for i in range(len(old_queue)):
        instruction = old_queue.pop()
        if instruction.current_stage.name == 'EX':
            ex_queue.appendleft(instruction)
        else:
            old_queue.appendleft(instruction)
    new_queue = prioritize_for_write_back(new_queue, ex_queue)

    for i in range(len(old_queue)):
        instruction = old_queue.pop()
        if instruction.current_stage.name == 'ID':
            new_queue.appendleft(instruction)
        else:
            old_queue.appendleft(instruction)

    for i in range(len(old_queue)):
        instruction = old_queue.pop()
        if instruction.current_stage.name == 'IF':
            new_queue.appendleft(instruction)
        else:
            old_queue.appendleft(instruction)

    return new_queue



def simulate_run():
    instruction_queue = deque([])
    clock_cycle = 1
    result = []
    REGISTER['PC'] = 1
    instruction_queue.appendleft(Executable(INSTRUCTIONS[0], clock_cycle))

    while len(instruction_queue) > 0:
        instruction_queue = reorder_instructions(instruction_queue)
        transfer_queue = deque([])
        while len(instruction_queue) > 0:
            instruction = instruction_queue.pop()
            if instruction.continue_execution():
                transfer_queue.appendleft(instruction)
            else:
                result.append(instruction.result)
                if REGISTER['FLUSH']:
                    result.append(instruction_queue.pop().result)
                    STAGE['IF'] = FREE
                    STAGE['IBUS'] = FREE
                    REGISTER['FLUSH'] = False

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
