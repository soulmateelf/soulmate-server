from sqlalchemy import Column, Integer, String, BigInteger, Text
from soulmate_server.common.mysql_tool import Base


# 用户聊天数据表
# 这个的动态的表名,每个用户一个,表名是chat{userId}
class BaseChat:

    __abstract__ = True  # 声明为抽象类，不会在数据库中生成表
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatId = Column(String(255), primary_key=True, index=True, nullable=False)
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    content = Column(Text, comment='聊天内容')
    role = Column(String(100), comment='对话角色,这个角色是api层面的,这里只有两种user和assistant')
    origin = Column(Integer, nullable=False, server_default='0',
                    comment='对话来源,0是默认值正常对话,1是角色主动打招呼发送的')
    inputType = Column(Integer, nullable=False, server_default='0', comment='用户聊天输入的类型,0是文本,1是语音')
    roleGreetId = Column(String(100), comment='角色主动打招呼发送的消息,保留打招呼的id')
    gptLogId = Column(String(100), comment='聊天对接gpt,对应的原始记录id')
    readStatus = Column(Integer, server_default='0',
                        comment='默认是已读状态,角色主动打招呼是未读,其他类型的默认已读,0未读,1已读')
    # 语音地址
    voiceUrl = Column(String(255), comment='语音地址')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    conclusionState = Column(Integer, nullable=False, server_default='0', comment='0未总结,1已总结')
    tokenSize = Column(Integer, nullable=False, server_default='0', comment='本次聊天消耗的token')
    # 语音时长
    voiceSize = Column(Integer(), server_default="0", comment="语音时长", nullable=False)
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 聊天记录总结表
# 这个的动态的表名,每个用户一个,表名是chatSummary{userId}
class ChatSummary(Base):
    __tablename__ = "chatSummary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    summaryId = Column(Integer, primary_key=True, index=True, nullable=False)
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    content = Column(String(1000), comment='总结的内容')
    score = Column(Integer, comment='本条内容的打分1-10')
    gptLogId = Column(String(100), comment='聊天总结是对接gpt生成的,对应的原始记录id')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


class redisMessage:
    def __init__(self, message, message_type,token):
        self.message = message
        self.message_type = message_type
        self.token = token
