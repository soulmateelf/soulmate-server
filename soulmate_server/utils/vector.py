import random
import uuid

import openai
from pymilvus import Collection, connections, utility, FieldSchema, DataType, CollectionSchema

from soulmate_server.conf.dataConf import milvusConf
from soulmate_server.utils.chat import get_embedding

# Create a connection
# alias 是个连接别名，默认是default, 可以自定义，后面操作中会用到
# 如果自定义了名称，后面的操作
# 需要指定连接名称
# 连接 Milvus 服务器
connections.connect(host=milvusConf['host'], port='19530', user=milvusConf['username'], password=milvusConf['password'],
                    db_name=milvusConf['db_name'])


class ConnectionManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            connections.connect(
                host=milvusConf['host'],
                db_name=milvusConf['db_name'],
                port=milvusConf['port'],
                user=milvusConf['username'],
                password=milvusConf['password'],
            )
        return cls._instance

    def __del__(self):
        connections.disconnect()


def generate_numeric_uuid():
    # 生成UUID
    uuid_str = str(uuid.uuid4())

    # 去掉UUID中的非数字部分
    numeric_uuid = ''.join(c for c in uuid_str if c.isdigit())

    return numeric_uuid



def insertData(save_messages, tokens, collection_name):
    try:
        res_embedding = get_embedding(save_messages, model='text-embedding-ada-002')
        save_messages =save_messages

        # 判断是否存在
        if utility.has_collection(collection_name) is False:
            createCollection(collection_name)
        # 数据集合
        collection = Collection(name=collection_name)
        entities = [

            [item['embedding'] for item in res_embedding['data']],  # field vector
            save_messages,  # field originData
            tokens,  # field token
        ]

        collection.insert(entities)
    except Exception as e:
        print(e)
        return False



# 创建表
def createCollection(collection_name):
    vectorId = FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True
    )
    vector = FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=1536,
    )

    message = FieldSchema(
        name="message",
        dtype=DataType.VARCHAR,
        # The default value will be used if this field is left empty during data inserts or upserts.
        # The data type of `default_value` must be the same as that specified in `dtype`.
        max_length=9999
    )
    token = FieldSchema(
        name="token",
        dtype=DataType.INT64
    )
    schema = CollectionSchema(
        fields=[vectorId, vector, message, token],
        description=collection_name,
        enable_dynamic_field=True
    )

    collection = Collection(
        name=collection_name,
        schema=schema
    )
    collection.create_index(field_name="vector",
                            index_params={"metric_type": "COSINE", "index_type": "IVF_FLAT", "nlist": 256})
    collection.load()


# 查询数据
# milvus数据库有两种查询，一个search, 一个query
# search是用向量查询，query是用条件查询


def searchData(vectorData, collection_name):
    # 判断是否存在
    if utility.has_collection(collection_name) is False:
        return None
    # 数据集合
    collection = Collection(name=collection_name)
    # 查询条件
    search_params = {
        "metric_type": "COSINE",  # 指定距离度量查询类型 L2欧氏距离，IP内积，COSINE余弦相识度距离
        "offset": 0,  # 查询结果的偏移量，指定了搜索结果的偏移量。如果设置为 0，则从结果的第一个开始返回；如果设置为 1，则从结果的第二个开始返回，以此类推
        "ignore_growing": False,  # 指示是否忽略在向量搜索期间集合的动态增长。如果设置为 True，则忽略动态增长；如果设置为 False，则考虑动态增长。
        # 指定查询参数，如 nprobe 参数。nprobe 参数用于指定在搜索期间要访问的索引节点数。nprobe 值越大，搜索的精度越高，但搜索速度越慢。默认值为 32。
        "params": {"nprobe": 10}
    }
    # 查询向量
    results = collection.search(
        data=[vectorData],
        anns_field="vector",  # 搜索的向量字段
        param=search_params,
        limit=5,  # 指定要返回的搜索结果的数量。默认值为 100。
        # expr=None,  # 指定查询表达式，以过滤搜索结果。默认值为 None。
        # expr="sum(token) <= 500",  # 使用表达式进行过滤
        output_fields=['id', 'message', 'token'],  # 指定要返回的字段。默认值为 None，表示返回所有字段。
        consistency_level="Strong"  # 指定查询的一致性级别。默认值为 None，表示使用集合的默认值。
    )
    # 搜索结果是一个list，最匹配的排在最前面
    return results


if __name__ == '__main__':
    try:
        try:
            1 / 0
        except Exception as e:
            print(1)
            # raise  # 重新引发异常
    except Exception as e:
        print(2)
    # messageList = ['周杰伦']
    # res = get_embedding(messageList, model='text-embedding-ada-002')
    #
    # searchResult = searchData(res['data'][0]['embedding'],'message')
    # print(searchResult)
    # # hit = searchResult[0][0]
    # # print(hit.entity.get('originData'))
