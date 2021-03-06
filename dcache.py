from config import *
from cache_block import *
from cache_set import *


class DCache:

    sets = []
    lru_for_cache_block = [0, 0]
    request_count = 0
    hit_count = 0

    def __init__(self):
        for i in range(CACHE_SETS):
            DCache.sets.append(Set(i, CACHE_SIZE / CACHE_SETS))


    @classmethod
    def read(self, address):
        DCache.request_count += 1
        address -= MEMORY_BASE_ADDRESS
        blk_no = (address >> 4) % 2
        read_cycles = 0

        for i in range(CACHE_SETS):
            if DCache._is_address_present_in_set(address, i):
                DCache.hit_count += 1
                DCache._set_lru(blk_no, i)
                return HIT, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2], ACCESS_TIME['DCACHE']

        set_no = DCache.lru_for_cache_block[blk_no]

        if DCache.sets[set_no].cache_block[blk_no].dirty:
            read_cycles += DCache._write_back(set_no, blk_no)

        DCache._setup_block(address, set_no)
        read_cycles += (ACCESS_TIME['DCACHE'] + ACCESS_TIME['MEMORY']) * 2
        return MISS, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2], read_cycles


    @classmethod
    def write(self, address, value, writable = True):
        DCache.request_count += 1
        address -= MEMORY_BASE_ADDRESS
        blk_no = (address >> 4) % 2
        write_cycles = 0

        for i in range(CACHE_SETS):
            if DCache._is_address_present_in_set(address, i):
                DCache.hit_count += 1
                DCache._set_lru(blk_no, i)
                DCache._set_value(address, i, value, writable)
                return HIT, ACCESS_TIME['DCACHE']

        set_no = DCache.lru_for_cache_block[blk_no]

        if DCache.sets[set_no].cache_block[blk_no].dirty:
            write_cycles += DCache._write_back(set_no, blk_no)

        DCache._setup_block(address, set_no)
        DCache._set_value(address, set_no, value, writable)
        return MISS, write_cycles + (ACCESS_TIME['DCACHE'] + ACCESS_TIME['MEMORY']) * 2


    @classmethod
    def is_hit(self, address):
        address -= MEMORY_BASE_ADDRESS
        for i in range(CACHE_SETS):
            if DCache._is_address_present_in_set(address, i):
                return True
        return False


    @classmethod
    def _is_address_present_in_set(self, address, set_no):
        tag = address >> 5
        blk_no = (address >> 4) % 2
        return DCache.sets[set_no].is_block_valid(blk_no) and DCache.sets[set_no].tag_for_block(blk_no) == tag


    @classmethod
    def _write_back(self, set_no, blk_no):
        tag = DCache.sets[set_no].cache_block[blk_no].tag
        base_address = MEMORY_BASE_ADDRESS + ((tag << 5) | (blk_no << 4))
        for i in range(CACHE_BLOCK_SIZE):
            DATA[base_address + (i * WORD_SIZE)] = DCache.sets[set_no].cache_block[blk_no].words[i]
        return (ACCESS_TIME['DCACHE'] + ACCESS_TIME['MEMORY']) * 2


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
    def _set_value(self, address, set_no, value, writable):
        blk_no = (address >> 4) % 2
        DCache.sets[set_no].cache_block[blk_no].dirty = True
        if writable:
            DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2] = value
