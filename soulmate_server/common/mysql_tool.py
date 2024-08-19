
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from soulmate_server.conf.dataConf import mysqlConf


# 数据库连接地址
# 注意，sqlalchemy只是一个orm的表映射工具，方便你业务操作的一个工具而已，真正连接数据库的还是pymysql这样的插件，所以还是需要安装的
DATABASE_URL = f'mysql+pymysql://{mysqlConf["username"]}:{mysqlConf["password"]}@{mysqlConf["host"]}:{mysqlConf["port"]}/{mysqlConf["db"]}'
# 创建数据库引擎和会话
# create_engine可以设置连接池的大小,默认pool_size=5,默认最大max_overflow=10，我先不改
# session就是事务，报错可以调用session.rollback()回滚
engine = create_engine(DATABASE_URL, pool_size=mysqlConf["pool_size"], max_overflow=mysqlConf["max_overflow"]
                       , pool_recycle=10800, pool_pre_ping=True,pool_timeout=30)
Session = sessionmaker(bind=engine, expire_on_commit=False)
mysqlSession = Session()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

async def get_db1():
    db = Session()
    try:
        yield db
    finally:
        db.close()

# 定义一个函数，循环sqlalchemy的对象属性，把他们变成键值对，同时过滤掉私有属性和sqlalchemy自带的属性
# 参考链接：https://stackoverflow.com/questions/54026174/proper-autogenerate-of-str-implementation-also-for-sqlalchemy-classes
def keyvalgen(obj):
    """ Generate attr name/val pairs, filtering out SQLA attrs."""
    excl = ('_sa_adapter', '_sa_instance_state')
    for k, v in vars(obj).items():
        if not k.startswith('_') and not any(hasattr(v, a) for a in excl):
            yield k, v


# 定义一个自己的基础类，基础类中有一个把sqlalchemy对象转化为json字符串的函数
class MyBase:
    def translateString(self):
        params = ', '.join(f'"{k}":"{v}"' for k, v in keyvalgen(self))
        return "{" + params + "}"


# Base 类是基础模型类,继承了我们上面写的自定义基础类
# 定义的表又继承了Base基础类，所以都会继承转字符串的方法
Base = declarative_base(cls=MyBase)

