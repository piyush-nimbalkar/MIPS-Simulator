DATA = {}

REGISTER = {}

WORD_SIZE = 4

MEMORY_BASE_ADDRESS = 256

INSTRUCTIONS = []

BUSY = True

FREE = False

STAGE = {
    'IF': FREE,
    'ID': FREE,
    'INTEGER': FREE,
    'FP_ADD': FREE,
    'FP_MUL': FREE,
    'FP_DIV': FREE,
    'WB': FREE
}

INTEGER = {
    'CYCLES': 2,
    'PIPELINED': True
}

FP_ADD = {
    'CYCLES': 4,
    'PIPELINED': False
}

FP_MUL = {
    'CYCLES': 6,
    'PIPELINED': False
}

FP_DIV = {
    'CYCLES': 20,
    'PIPELINED': False
}
