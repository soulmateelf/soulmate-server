# 数据库配置文件

# 环境设置，还可以加local之类的配置
environment = 'production'
# redis配置列表
redisConfList = {
    "develop": {
        "host": "",
        "port": 55824,
        "username": "",
        "password": "",
        "db": 0,
        "max_connections": 10
    },
    "production": {
        "host": "",
        "port": 55824,
        "username": "",
        "password": "",
        "db": 0,
        "max_connections": 10
    }
}
# mysql配置列表
mysqlConfList = {
    "develop": {
        "host": "",
        "port": 42896,
        "username": "",
        "password": "",
        "db": "soulmate_server",
        "pool_size": 20,
        "max_overflow": 50,
    },
    "production": {
        "host": "",
        "port": 56487,
        "username": "",
        "password": "",
        "db": "soulmate_server",
        "pool_size": 5,
        "max_overflow": 10
    }
}
# 向量数据库配置列表
milvusConfList = {
    "develop": {
        "host": "",
        "db_name": "default",
        "username": "",
        "password": "",
        "port": 19530
    },
    "production": {
        "host": "",
        "db_name": "default",
        "username": "",
        "password": "",
        "port": 19530
    }
}
# 向量数据库配置列表
mqttList = {
    "develop": {
        "host": "",
        "db_name": 'default',
        "username": "",
        "password": "",
        "port": 19530
    },
    "production": {
        "host": "",
        "username": "",
        "password": "",
        "port": 1883
    }
}
# 生效的redis配置
redisConf = redisConfList[environment]
# 生效的mysql配置
mysqlConf = mysqlConfList[environment]
# 生效的向量数据库配置
milvusConf = milvusConfList[environment]

mqttConf = mqttList[environment]
