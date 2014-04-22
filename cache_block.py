class CacheBlock:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.tag = 0
        self.valid = False
        self.words = []

    def store(self, words):
        self.words = words
