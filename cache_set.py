from config import *
from cache_block import *


class Set:

    cache_block = []

    def __init__(self, id, size):
        self.id = 0
        self.size = size
        for i in range(size):
            Set.cache_block.append(CacheBlock(i, CACHE_BLOCK_SIZE))
