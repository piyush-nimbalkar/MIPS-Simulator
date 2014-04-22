from config import *
from cache_block import *
from cache_set import *


class DCache:

    sets = []
    lru_for_cache_block = [0, 0]

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
                DCache.lru_for_cache_block[blk_no] = 1 if i == 0 else 0
                return HIT, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2]

        set_no = DCache.lru_for_cache_block[blk_no]
        DCache.sets[set_no].cache_block[blk_no].tag = tag
        DCache.sets[set_no].cache_block[blk_no].valid = True
        DCache.sets[set_no].cache_block[blk_no].words = []
        DCache.lru_for_cache_block[blk_no] = 1 if set_no == 0 else 0
        base_address = MEMORY_BASE_ADDRESS + ((address >> 4) << 4)
        for i in range(CACHE_BLOCK_SIZE):
            DCache.sets[set_no].cache_block[blk_no].words.append(DATA[base_address + (i * WORD_SIZE)])
        return MISS, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2]
