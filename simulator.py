from collections import deque
from executable import *
from parser import *
from icache import *
from dcache import *
from config import *
import operator
import sys



def initialize_cache():
    ICache()
    DCache()



def prioritize_for_write_back(new_queue, ex_queue):
    priority_map = {}
    count = MAX

    for i in range(len(ex_queue)):
        ex = ex_queue.pop()

        if ex._instruction.functional_unit() == 'FP_DIV':
            if FP_DIV['PIPELINED']:
                priority_map[ex] = count + FP_DIV['CYCLES']
            else:
                priority_map[ex] = count + FP_DIV['CYCLES'] + MAX

        elif ex._instruction.functional_unit() == 'FP_MUL':
            if FP_MUL['PIPELINED']:
                priority_map[ex] = count + FP_MUL['CYCLES']
            else:
                priority_map[ex] = count + FP_MUL['CYCLES'] + MAX

        elif ex._instruction.functional_unit() == 'FP_ADD':
            if FP_ADD['PIPELINED']:
                priority_map[ex] = count + FP_ADD['CYCLES']
            else:
                priority_map[ex] = count + FP_ADD['CYCLES'] + MAX

        else:
            priority_map[ex] = count

        count -= 1

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
        for label, address in LABEL.items():
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

    path = ""

    try:
        Parser.parse_instructions(path + sys.argv[1])
        Parser.parse_data(path + sys.argv[2])
        Parser.parse_registers(path + sys.argv[3])
        Parser.parse_config(path + sys.argv[4])
    except Exception as e:
        print('Parse Exception: ' + str(e))
        exit()

    initialize_cache()
    simulate_run()
