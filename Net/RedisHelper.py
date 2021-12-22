import json
import os

import redis


def get_single(connection: redis.StrictRedis, key):
    try:
        value = connection.get(key)
        return {key: value}
    except Exception as c:
        print("Error in getting single info : ", c)
        return None


def get_bulk(connection: redis.StrictRedis):
    try:
        keys = connection.keys()
        values = connection.mget(keys)
        data = dict(zip(keys, [json.loads(value) for value in values]))
        return data
    except Exception as c:
        print("Error in getting bulk info : ", c)
        return None


def insert_single(connection: redis.StrictRedis, key, value, timeout=60):
    try:
        connection.set(key, json.dumps(value), ex=timeout)
        return True
    except Exception as c:
        print("Error in inserting single info : ", c)
        return False


def remove_single(connection: redis.StrictRedis, key):
    try:
        connection.delete(key)
        return True
    except Exception as c:
        print("Error in removing single info : ", c)
        return False


def insert_bulk(connection: redis.StrictRedis, data, timeout=60):
    try:
        pipe = connection.pipeline()
        for key, value in data.items():
            pipe.set(key, json.dumps(value), ex=timeout)
        pipe.execute()
        return True
    except Exception as c:
        print("Error in inserting bulk info : ", c)
        return False


def insert_single_list(connection: redis.StrictRedis, key, value):
    try:
        connection.lpush(key, json.dumps(value))
        return True
    except Exception as c:
        print("Error in inserting single info : ", c)
        return False


def insert_single_set(connection: redis.StrictRedis, key, value):
    try:
        connection.sadd(key, value)
        return True
    except Exception as c:
        print("Error in inserting single info : ", c)
        return False


class RedisManager:
    def __init__(self):
        self.pipe = None
        try:
            redis_host = os.getenv("REDIS_HOST", default="192.168.55.251")
            redis_port = os.getenv("REDIS_PORT", default=6379)
            redis_mikrotik_db = os.getenv("REDIS_MIKROTIK_DB", default=0)
            redis_cisco_db = os.getenv("REDIS_CISCO_DB", default=1)
            redis_miner_db = os.getenv("REDIS_MINER_DB", default=2)
            redis_miner_detail_db = os.getenv("REDIS_MINER_DETAIL_DB", default=3)
            redis_port_failure_db = os.getenv("REDIS_PORT_FAILURE_DB", default=4)
            redis_switch_failure_db = os.getenv("REDIS_SWITCH_FAILURE_DB", default=5)
            redis_miner_failure_db = os.getenv("REDIS_MINER_FAILURE_DB", default=6)
            redis_restart_db = os.getenv("REDIS_RESTART_DB", default=7)
            redis_pool_db = os.getenv("REDIS_POOL_DB", default=8)
            redis_clock_db = os.getenv("REDIS_CLOCK_DB", default=9)
            redis_lists_db = os.getenv("REDIS_LISTS_DB", default=10)
            self.mikrotik = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                              decode_responses=True, db=redis_mikrotik_db)
            self.cisco = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                           decode_responses=True, db=redis_cisco_db)
            self.miner = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                           decode_responses=True, db=redis_miner_db)
            self.miner_detail = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                                  decode_responses=True, db=redis_miner_detail_db)
            self.port_failure = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                                  decode_responses=True, db=redis_port_failure_db)
            self.switch_failure = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                                    decode_responses=True, db=redis_switch_failure_db)
            self.miner_failure = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                                   decode_responses=True, db=redis_miner_failure_db)
            self.restart = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                             decode_responses=True, db=redis_restart_db)
            self.pool = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                          decode_responses=True, db=redis_pool_db)
            self.clock = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                           decode_responses=True, db=redis_clock_db)
            self.lists = redis.StrictRedis(host=redis_host, port=redis_port, charset="utf-8",
                                           decode_responses=True, db=redis_lists_db)
        except Exception as c:
            print("Error in redis connection", c)
            pass
