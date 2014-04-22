from config import *
from cache_block import *


class ICache:

    size = CACHE_SIZE
    block_size = CACHE_BLOCK_SIZE
    cache_block = []

    def __init__(self):
        for i in range(ICache.size):
            ICache.cache_block.append(CacheBlock(i, ICache.block_size))

    @classmethod
    def access(self, address):
        tag = address >> 6
        blk_no = (address >> 4) % 4
        if ICache.cache_block[blk_no].valid == True and ICache.cache_block[blk_no].tag == tag:
            return True, address
        else:
            ICache.cache_block[blk_no].tag = tag
            ICache.cache_block[blk_no].valid = True
            return False, address
