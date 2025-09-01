import redis

r = redis.Redis()

def clear_redis_cache():
    for key in r.scan_iter('parking:lots*'):
        r.delete(key)
    