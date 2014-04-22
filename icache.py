from config import *
from cache_block import *


class ICache:

    cache_block = []

    def __init__(self):
        for i in range(CACHE_SIZE):
            ICache.cache_block.append(CacheBlock(i, CACHE_BLOCK_SIZE))

    @classmethod
    def access(self, address):
        tag = address >> 6
        blk_no = (address >> 4) % 4
        if ICache.cache_block[blk_no].valid == True and ICache.cache_block[blk_no].tag == tag:
            return HIT
        else:
            ICache.cache_block[blk_no].tag = tag
            ICache.cache_block[blk_no].valid = True
            return MISS
