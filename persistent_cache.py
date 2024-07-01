import time
import os
import pickle

class PersistentCache:
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as file:
                try:
                    return pickle.load(file)
                except (pickle.PickleError, EOFError):
                    pass
        return {}

    def save_cache(self):
        with open(self.cache_file, 'wb') as file:
            pickle.dump(self.cache, file)

    def get(self, key, default=None):
        if key in self.cache:
            value, expiry = self.cache[key]
            if expiry < time.time():
                self.delete(key)
                return default
            return value
        return default

    def set(self, key, value, expiry_seconds=300):
        expiry = None
        if expiry_seconds is not None:
            expiry = time.time() + expiry_seconds
        self.cache[key] = (value, expiry)
        self.save_cache()

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            self.save_cache()

    def clear(self):
        self.cache.clear()
        self.save_cache()