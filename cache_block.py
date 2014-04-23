class CacheBlock:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.tag = 0
        self.valid = False
        self.dirty = False
        self.words = [0, 0, 0, 0]

    def store(self, words):
        self.words = words
