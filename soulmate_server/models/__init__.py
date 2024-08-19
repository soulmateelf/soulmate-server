from sqlalchemy import inspect
from soulmate_server.common.mysql_tool import Base, engine
from soulmate_server.models.dynamic import BaseChat

# 这个文件夹下的文件都是表结构，这个初始化文件在这里导入了这些模型文件，然后创建表
# 虽然下面的导入并看起来没有使用，但是是必要的
from . import user
from . import role
from . import energy
from . import other

# 创建mysql表结构
Base.metadata.create_all(engine)


# 判断表存在与否
def table_exists(tableName):
    inspector = inspect(engine)
    return tableName in inspector.get_table_names()


# 创建动态类
def createDynamicClass(tableName):
    # 检查类是否已存在
    if tableName in globals():
        # 如果类已存在，更新它的定义并返回
        existing_class = globals()[tableName]
        existing_class.__table__.name = tableName  # 更新表名
        return existing_class

    # 如果类不存在，动态创建类
    dynamicClass = type(tableName, (Base, BaseChat), {
        '__tablename__': tableName
    })

    # 将类添加到全局命名空间
    globals()[tableName] = dynamicClass

    return dynamicClass


# 创建动态表
def createDynamicTable(userId: str = '', tablePrefix: str = 'chat'):
    # 目前只有聊天记录表和聊天记录总结表两个是动态表
    if tablePrefix not in ('chat', 'chatSummary'):
        return None
    # 表名
    tableName = f'{tablePrefix}{userId}'
    # 动态创建类

    dynamicClass = createDynamicClass(tableName)
    if not table_exists(tableName):
        # 不存在就创建表
        dynamicClass.__table__.create(bind=engine)
    return dynamicClass
async def asyncCreateDynamicTable(userId: str = '', tablePrefix: str = 'chat'):
    # 目前只有聊天记录表和聊天记录总结表两个是动态表
    if tablePrefix not in ('chat', 'chatSummary'):
        return None
    # 表名
    tableName = f'{tablePrefix}{userId}'
    # 动态创建类

    dynamicClass = createDynamicClass(tableName)
    if not table_exists(tableName):
        # 不存在就创建表
        dynamicClass.__table__.create(bind=engine)
    return dynamicClass
