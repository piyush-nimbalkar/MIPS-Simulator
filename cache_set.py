from config import *
from cache_block import *


class Set:

    def __init__(self, id, size):
        self.id = 0
        self.size = size
        self.cache_block = []
        for i in range(size):
            self.cache_block.append(CacheBlock(i, CACHE_BLOCK_SIZE))
