from config import *
from instruction import *


class Parser:

    @classmethod
    def parse_instructions(self, filename):
        file = open(filename, 'r')

        for line in file:
            line = line.strip().upper()
            if ':' in line:
                instruction = line.split(':')
                LABEL[instruction[0].strip().upper()] = Instruction.count * WORD_SIZE
                instruction = instruction[1].strip().split(' ')
            else:
                instruction = line.split(' ')

            instruction_name = instruction[0]
            operands = ''.join(instruction[1 : len(instruction)]).split(',')
            INSTRUCTIONS.append(Instruction(instruction_name, operands))

        for instr in INSTRUCTIONS:
            if instr.immediate in LABEL.keys():
                instr.set_immediate(LABEL[instr.immediate])


    @classmethod
    def parse_data(self, filename):
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


    @classmethod
    def parse_registers(self, filename):
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


    @classmethod
    def parse_config(self, filename):
        file = open(filename, 'r')

        for line in file:
            line = line.lower().strip()
            split_line = line.split(':')
            if 'adder' in split_line[0]:
                Parser.write_pipelining_status(FP_ADD, split_line[1])
            elif 'multiplier' in split_line[0]:
                Parser.write_pipelining_status(FP_MUL, split_line[1])
            elif 'divider' in split_line[0]:
                Parser.write_pipelining_status(FP_DIV, split_line[1])
            elif 'memory' in split_line[0]:
                ACCESS_TIME['MEMORY'] = int(split_line[1].strip())
            elif 'i-cache' in split_line[0]:
                ACCESS_TIME['ICACHE'] = int(split_line[1].strip())
            elif 'd-cache' in split_line[0]:
                ACCESS_TIME['DCACHE'] = int(split_line[1].strip())


    @classmethod
    def write_pipelining_status(self, fu_hash, param_string):
        params = [x.strip() for x in param_string.split(',')]
        fu_hash['CYCLES'] = int(params[0])
        if params[1] == 'yes':
            fu_hash['PIPELINED'] = True
        else:
            fu_hash['PIPELINED'] = False


    @classmethod
    def reset_register_status(self):
        for i in range(32):
            REGISTER_STATUS['R' + str(i)] = FREE
            REGISTER_STATUS['F' + str(i)] = FREE
