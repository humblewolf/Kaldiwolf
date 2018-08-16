import redis

class PySimpleQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db= redis.Redis(**redis_kwargs)
        #self.key = '%s:%s' %(namespace, name)

    def qsize(self, key):
        """Return the approximate size of the queue."""
        return self.__db.llen(key)

    def empty(self, key):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize(key) == 0

    def put(self, key, item):
        """Put item into the queue."""
        self.__db.rpush(key, item)

    def get(self, key, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(key, timeout=timeout)
        else:
            item = self.__db.lpop(key)

        if item:
            item = item[1]
        return item

    def get_nowait(self, key):
        """Equivalent to get(False)."""
        return self.get(key, False)