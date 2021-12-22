import json

from Net.RedisHelper import RedisManager, insert_single


def insert_network_map_to_redis():
    redis = RedisManager()
    with open("./NetworkMap.json") as json_file:
        network_map = json.load(json_file)
        try:
            insert_single(redis.lists, "NetworkMap", network_map, timeout=None)
        except Exception as c:
            print("Error in inserting Network Map to redis", c)
            pass
