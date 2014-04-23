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
    def read(self, address, size = 1):
        address -= MEMORY_BASE_ADDRESS
        tag = address >> 5
        blk_no = (address >> 4) % 2

        for i in range(CACHE_SETS):
            if DCache.sets[i].cache_block[blk_no].valid == True and DCache.sets[i].cache_block[blk_no].tag == tag:
                DCache.lru_for_cache_block[blk_no] = 1 if i == 0 else 0
                return HIT, address + MEMORY_BASE_ADDRESS, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2]

        set_no = DCache.lru_for_cache_block[blk_no]
        if DCache.sets[set_no].cache_block[blk_no].dirty:
            old_tag = DCache.sets[set_no].cache_block[blk_no].tag
            old_address = (old_tag << 5) | (blk_no << 4)
            base_address = MEMORY_BASE_ADDRESS + old_address
            for i in range(CACHE_BLOCK_SIZE):
                DATA[base_address + (i * WORD_SIZE)] = DCache.sets[set_no].cache_block[blk_no].words[i]



        DCache.sets[set_no].cache_block[blk_no].tag = tag
        DCache.sets[set_no].cache_block[blk_no].valid = True
        DCache.lru_for_cache_block[blk_no] = 1 if set_no == 0 else 0

        base_address = MEMORY_BASE_ADDRESS + ((address >> 4) << 4)
        for i in range(CACHE_BLOCK_SIZE):
            DCache.sets[set_no].cache_block[blk_no].words[i] = DATA[base_address + (i * WORD_SIZE)]

        return MISS, address + MEMORY_BASE_ADDRESS, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2]


    @classmethod
    def write(self, address, value, size = 1):
        address -= MEMORY_BASE_ADDRESS
        new_tag = address >> 5
        blk_no = (address >> 4) % 2

        for i in range(CACHE_SETS):
            if DCache.sets[i].cache_block[blk_no].valid == True and DCache.sets[i].cache_block[blk_no].tag == new_tag:
                DCache.lru_for_cache_block[blk_no] = 1 if i == 0 else 0
                DCache.sets[i].cache_block[blk_no].dirty = True
                DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2] = value
                return HIT, address + MEMORY_BASE_ADDRESS, DCache.sets[i].cache_block[blk_no].words[(address & 12) >> 2]


        set_no = DCache.lru_for_cache_block[blk_no]
        if DCache.sets[set_no].cache_block[blk_no].dirty:
            old_tag = DCache.sets[set_no].cache_block[blk_no].tag
            old_address = (old_tag << 5) | (blk_no << 4)
            base_address = MEMORY_BASE_ADDRESS + old_address
            for i in range(CACHE_BLOCK_SIZE):
                DATA[base_address + (i * WORD_SIZE)] = DCache.sets[set_no].cache_block[blk_no].words[i]

        DCache.sets[set_no].cache_block[blk_no].tag = new_tag
        DCache.sets[set_no].cache_block[blk_no].valid = True
        DCache.lru_for_cache_block[blk_no] = 1 if set_no == 0 else 0

        base_address = MEMORY_BASE_ADDRESS + ((address >> 4) << 4)
        for i in range(CACHE_BLOCK_SIZE):
            if ((address & 12) >> 2) == i:
                DCache.sets[set_no].cache_block[blk_no].words[i] = value
            else:
                DCache.sets[set_no].cache_block[blk_no].words[i] = DATA[base_address + (i * WORD_SIZE)]

        return MISS, address + MEMORY_BASE_ADDRESS, DCache.sets[set_no].cache_block[blk_no].words[(address & 12) >> 2]


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

    for i in sorted(DATA.keys()):
        print(i),
        print(DATA[i])
    print

if __name__ == '__main__':
    parse_data('data.txt')
    DCache()
    # print(DCache.fetch(256))
    # print(DCache.fetch(264))
    # print(DCache.fetch(272))
    # print(DCache.fetch(276))
    # print(DCache.fetch(288))
    # print(DCache.fetch(292))
    # print(DCache.fetch(304))
    # print(DCache.fetch(256))
    # print(DCache.fetch(266))
    # print(DCache.fetch(322))
    # print(DCache.fetch(288))
    # print(DCache.fetch(322))
    # print(DCache.fetch(322))
    # print(DCache.fetch(288))
    # print(DCache.fetch(256))
    print(DCache.fetch(256))
    print(DCache.store(256, 1))
    print(DCache.fetch(256))
    print(DCache.fetch(268))

    print(DCache.fetch(288))
    print(DCache.fetch(320))
    print(DCache.fetch(256))
    print(DCache.store(268, 32))
    print(DCache.fetch(320))
    print(DCache.store(288, 45))
    print(DCache.fetch(268))
    print(DCache.fetch(288))
    print(DCache.fetch(268))
    print(DCache.fetch(324))
    print(DCache.fetch(288))
    # print(DCache.store(256, 1))
    # print(DCache.fetch(256))
    # print(DCache.fetch(268))

    # print(DCache.fetch(264))
    # print(DCache.fetch(272))
    # print(DCache.fetch(276))
    # print(DCache.fetch(288))
    # print(DCache.fetch(292))
    # print(DCache.fetch(304))
    # print(DCache.fetch(256))
    # print(DCache.fetch(266))
    # print(DCache.fetch(322))
    # print(DCache.fetch(288))
    # print(DCache.fetch(322))
    # print(DCache.fetch(322))
    # print(DCache.fetch(288))
    # print(DCache.fetch(256))
