from config import *
from cache_block import *
from cache_set import *


class DCache:

    sets = []

    def __init__(self):
        for i in range(CACHE_SETS):
            DCache.sets.append(Set(i, CACHE_SIZE / CACHE_SETS))


    @classmethod
    def access(self, address):
        address -= MEMORY_BASE_ADDRESS
        tag = address >> 5
        blk_no = (address >> 4) % 2

        for i in range(CACHE_SETS):
            if DCache.sets[i].cache_block[blk_no].valid == True and DCache.sets[i].cache_block[blk_no].tag == tag:
                return HIT, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2]

        DCache.sets[0].cache_block[blk_no].tag = tag
        DCache.sets[0].cache_block[blk_no].valid = True
        DCache.sets[0].cache_block[blk_no].words = []
        base_address = MEMORY_BASE_ADDRESS + ((address >> 4) << 4)
        for i in range(CACHE_BLOCK_SIZE):
            DCache.sets[0].cache_block[blk_no].words.append(DATA[base_address + (i * WORD_SIZE)])
        return MISS, DCache.sets[0].cache_block[blk_no].words[(address & 12) >> 2]
