from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship

from soulmate_server.common.mysql_tool import Base


# 角色表
class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roleId = Column(String(100), primary_key=True, index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False, comment='角色名称')
    age = Column(Integer, comment='年龄')
    gender = Column(String(100), comment='性别,male男性,female女性,或者其他')
    avatar = Column(String(255), comment='头像地址')
    hobby = Column(String(1000), comment='爱好')
    description = Column(String(5000), comment='角色介绍')
    setting = Column(Text, comment='角色设定,服务于gpt接口')
    origin = Column(Integer, comment='来源,0系统创建,1客户定制')
    userId = Column(String(100), comment='如果是客户定制的,需要有客户id')
    # 角色音色
    voice = Column(String(255), comment='角色音色')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    # 角色生成朋友圈使用的描绘
    gptDescription = Column(String(5000), comment='角色生成朋友圈使用的描绘')
    # 角色引导语
    guide = Column(Text, comment='角色引导语')
    updateTime = Column(BigInteger)


# 角色关系表
class RoleRelationship(Base):
    __tablename__ = "roleRelationship"
    id = Column(Integer, primary_key=True, autoincrement=True)
    relationId = Column(String(255), primary_key=True, index=True, nullable=False)
    roleIdMain = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    roleIdSub = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    relationship = Column(String(100), comment='关系,roleIdMain是roleIdSub的什么,比如wife,friend,son等等')
    level = Column(Integer, nullable=False, server_default='1', comment='关系等级1-10,数字越大越亲密')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 角色的记忆事件库，也是朋友圈
class RoleMemory(Base):
    __tablename__ = "roleMemory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    memoryId = Column(String(100), primary_key=True, index=True, nullable=False)
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    content = Column(String(5000), comment='事件内容')
    image = Column(String(255), comment='事件图片地址')
    startTime = Column(BigInteger, comment='事件的开始时间')
    endTime = Column(BigInteger, comment='事件的结束时间,产品说结束时间就是发布时间,但是最好是区分开')
    publishTime = Column(BigInteger, nullable=False, comment='发布时间,这个是预先生成的，到时间再显示')
    public = Column(Integer, nullable=False, server_default='0', comment='0公开的朋友圈,1对用户私人开放的朋友圈')
    userId = Column(String(100), comment='关联user表userId,对用户私人开放的朋友圈需要userId')
    gptLogId = Column(String(100), comment='记忆库是对接gpt生成的,对应的原始记录id')
    # 解释
    explanation = Column(String(1000), comment='解释')
    # 经验
    experience = Column(String(1000), comment='经验')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)

    # 使用 relationship 定义关系，指定 primaryjoin 参数
    activities = relationship('RoleMemoryActivity', back_populates='role_memory',
                              primaryjoin='RoleMemory.memoryId == RoleMemoryActivity.memoryId')


# 角色的记忆事件库(朋友圈)的点赞评论事件
class RoleMemoryActivity(Base):
    __tablename__ = "roleMemoryActivity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    activityId = Column(String(100), primary_key=True, index=True, nullable=False)
    memoryId = Column(String(100), ForeignKey('roleMemory.memoryId'), index=True, nullable=False,
                      comment='关联RoleMemory表memoryId')
    userId = Column(String(100), comment='关联user表userId')
    type = Column(Integer, nullable=False, server_default='0', comment='0点赞,1评论')
    content = Column(String(1000), comment='评论内容')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)
    avatar = Column(String(255), comment='头像地址')
    userName = Column(String(255), comment='用户名')
    role_memory = relationship('RoleMemory', back_populates='activities')



# 角色的记忆事件库(朋友圈)的未读消息
class RoleMemoryNotify(Base):
    __tablename__ = "roleMemoryNotify"
    id = Column(Integer, primary_key=True, autoincrement=True)
    notifyId = Column(String(100), primary_key=True, index=True, nullable=False)
    memoryId = Column(String(100), index=True, nullable=False, comment='关联RoleMemory表memoryId')
    userId = Column(String(100), comment='关联user表userId')
    roleId = Column(String(100), comment='关联role表roleId')
    readStatus = Column(Integer, server_default='0',
                        comment='该条朋友圈对该用户的状态,默认是未读状态,其他类型的默认已读,0未读,1已读')
    # 显隐时间 与朋友圈发布时间相同
    publishTime = Column(BigInteger, nullable=False, comment='发布时间,这个是预先生成的，到时间再显示')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 角色主动打招呼
class RoleGreet(Base):
    __tablename__ = "roleGreet"
    id = Column(Integer, primary_key=True, autoincrement=True)
    greetId = Column(String(100), primary_key=True, index=True, nullable=False)
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    content = Column(String(1000), comment='打招呼的内容')
    publishTime = Column(BigInteger, nullable=False, comment='发布时间,这个是预先生成的，到时间再显示')
    gptLogId = Column(String(100), comment='主动打招呼是对接gpt生成的,对应的原始记录id')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 生成朋友圈(角色事件表)
class RoleMemoryCreateLog(Base):
    __tablename__ = "role_memory_create_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    createLogId = Column(String(100), primary_key=True, index=True, nullable=False)
    result = Column(String(1000), comment='生成结果')
    gptResult = Column(Text(), comment='gpt生成结果')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')

    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)
