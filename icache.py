from config import *
from cache_block import *


class ICache:

    cache_block = []
    request_count = 0
    hit_count = 0

    def __init__(self):
        for i in range(CACHE_SIZE):
            ICache.cache_block.append(CacheBlock(i, CACHE_BLOCK_SIZE))


    @classmethod
    def read(self, address):
        ICache.request_count += 1
        tag = address >> 6
        blk_no = (address >> 4) % 4
        if ICache.cache_block[blk_no].valid == True and ICache.cache_block[blk_no].tag == tag:
            ICache.hit_count += 1
            return HIT, ACCESS_TIME['ICACHE']
        else:
            ICache.cache_block[blk_no].tag = tag
            ICache.cache_block[blk_no].valid = True
            return MISS, (ACCESS_TIME['ICACHE'] + ACCESS_TIME['MEMORY']) * 2
