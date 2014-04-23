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
    def read(self, address):
        address -= MEMORY_BASE_ADDRESS
        blk_no = (address >> 4) % 2

        for i in range(CACHE_SETS):
            if DCache._is_address_present_in_set(address, i):
                DCache._set_lru(blk_no, i)
                return HIT, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2]

        set_no = DCache.lru_for_cache_block[blk_no]

        if DCache.sets[set_no].cache_block[blk_no].dirty:
            DCache._write_back(set_no, blk_no)

        DCache._setup_block(address, set_no)
        return MISS, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2]


    @classmethod
    def write(self, address, value):
        address -= MEMORY_BASE_ADDRESS
        blk_no = (address >> 4) % 2

        for i in range(CACHE_SETS):
            if DCache._is_address_present_in_set(address, i):
                DCache._set_lru(blk_no, i)
                DCache._set_value(address, i, value)
                return HIT, value

        set_no = DCache.lru_for_cache_block[blk_no]

        if DCache.sets[set_no].cache_block[blk_no].dirty:
            DCache._write_back(set_no, blk_no)

        DCache._setup_block(address, set_no)
        DCache._set_value(address, set_no, value)
        return MISS, value


    @classmethod
    def _is_address_present_in_set(self, address, set_no):
        tag = address >> 5
        blk_no = (address >> 4) % 2
        return DCache.sets[set_no].cache_block[blk_no].valid == True and DCache.sets[set_no].cache_block[blk_no].tag == tag


    @classmethod
    def _write_back(self, set_no, blk_no):
        tag = DCache.sets[set_no].cache_block[blk_no].tag
        base_address = MEMORY_BASE_ADDRESS + ((tag << 5) | (blk_no << 4))
        for i in range(CACHE_BLOCK_SIZE):
            DATA[base_address + (i * WORD_SIZE)] = DCache.sets[set_no].cache_block[blk_no].words[i]


    @classmethod
    def _setup_block(self, address, set_no):
        blk_no = (address >> 4) % 2
        DCache.sets[set_no].cache_block[blk_no].tag = address >> 5
        DCache.sets[set_no].cache_block[blk_no].valid = True
        DCache._set_lru(blk_no, set_no)
        DCache._read_from_memory(address, set_no)


    @classmethod
    def _set_lru(self, blk_no, set_no):
        DCache.lru_for_cache_block[blk_no] = 1 if set_no == 0 else 0


    @classmethod
    def _read_from_memory(self, address, set_no):
        blk_no = (address >> 4) % 2
        base_address = MEMORY_BASE_ADDRESS + ((address >> 4) << 4)
        for i in range(CACHE_BLOCK_SIZE):
            DCache.sets[set_no].cache_block[blk_no].words[i] = DATA[base_address + (i * WORD_SIZE)]


    @classmethod
    def _set_value(self, address, set_no, value):
        blk_no = (address >> 4) % 2
        DCache.sets[set_no].cache_block[blk_no].dirty = True
        DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2] = value
