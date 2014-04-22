DATA = {}

REGISTER = {}

REGISTER_STATUS = {}

WORD_SIZE = 4

MEMORY_SIZE = 128

CACHE_SIZE = 4

CACHE_BLOCK_SIZE = 4

MEMORY_BASE_ADDRESS = 256

INSTRUCTIONS = []

BUSY = True

FREE = False

HIT = True

MISS = False

STAGE = {
    'IF': FREE,
    'ID': FREE,
    'IU': FREE,
    'MEM': FREE,
    'FP_ADD': FREE,
    'FP_MUL': FREE,
    'FP_DIV': FREE,
    'WB': FREE
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
