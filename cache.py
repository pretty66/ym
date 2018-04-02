import redis
import helper


class cacheBase(object):
    def __init__(self):
        host = helper.common.getConfig('redis', 'host')
        port = helper.common.getConfig('redis', 'port')
        db = helper.common.getConfig('redis', 'db')
        password = helper.common.getConfig('redis', 'password')
        self.handle = redis.Redis(host=host, port=port, db=db,password=password, decode_responses=True)
    def get_client(self):
        return self.handle


cache = cacheBase().get_client()

