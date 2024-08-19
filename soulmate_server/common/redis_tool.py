import redis
from soulmate_server.conf.dataConf import redisConf
# -*- coding: utf-8 -*-
# 创建一个 Redis 连接池，设置最大连接数为10，默认就是10，我先不改
pool = redis.ConnectionPool(host=redisConf["host"], port=redisConf["port"],
                            password=redisConf["password"], db=redisConf["db"],
                            max_connections=redisConf["max_connections"])

# 创建一个全局的 Redis 连接对象并指定连接池
redis_client = redis.Redis(connection_pool=pool)



# 获取 Redis 中的值
def redis_get(key: str, prefix: str = ''):
    if redis_client.get(prefix + key) is None:
        return None
    return redis_client.get(prefix + key).decode('utf-8')


# 获取 Redis 中list类型的值
def redis_getList(key: str, prefix: str = ''):
    return [item.decode('utf-8') for item in redis_client.lrange(prefix + key, 0, -1)]

def redis_lpush(key: str, value: any, prefix: str = ''):
    return redis_client.lpush(prefix + key, value)
async def asyncRedis_getList(key: str, prefix: str = ''):
    return [item.decode('utf-8') for item in redis_client.lrange(prefix + key, 0, -1)]


# 设置 Redis 中的值
# expireTime是秒为单位
def redis_set(key: str, value: any, prefix: str = '', expireTime=None):
    return redis_client.set(prefix + key, value, ex=expireTime)
if __name__ == '__main__':
    redis_set('123', '123',expireTime=10)
async def asyncRedis_set(key: str, value: any, prefix: str = '', expireTime=None):
    return redis_client.set(prefix + key, value, ex=expireTime)
# 设置 Redis 中list类型的值
# 历史聊天记录，数组存储
def redis_setList(key: str, value: any, prefix: str = '', expireTime=None):
    redis_client.rpush(prefix + key, *value)
    if expireTime != None:
        redis_client.expire(prefix + key, expireTime)
    # 优化存储，检查列表长度，如果超过10个元素，则修剪它
    # list_length = redis_client.llen(prefix+key)
    # if list_length > 10:
    #     redis_client.ltrim(prefix+key, list_length-10, list_length-1)


def redis_delete(key: str, prefix: str = ''):
    # 删除键值
    return redis_client.delete(prefix + key);
async def asyncRedis_delete(key: str, prefix: str = ''):
    # 删除键值
    return redis_client.delete(prefix + key);


async def redis_exist(key: str, prefix: str = ''):
    # 判断键值存在与否
    return redis_client.exists(prefix + key);


async def redis_refreshTime(key: str, prefix: str = '', expireTime=None):
    # 刷新过期时间
    if expireTime != None:
        return redis_client.expire(prefix + key, expireTime);


async def close_redis_connection():
    # 关闭 Redis 连接
    pool.disconnect()


# 新增值指定存在时间
def setExKey(key, seconds, value):
    redis_client.setex(key, seconds, value)


# 查询这个是否存在这个键存在返回1不存在返回0
def existsKey(key):
    return redis_client.exists(key)


