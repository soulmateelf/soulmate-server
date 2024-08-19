from sqlalchemy import Column, Integer, String, BigInteger, Text
from soulmate_server.common.mysql_tool import Base


# 消息表
# 日常消息：亲密度（涨、降）、赠送*能量(聊天达到**句,看广告)、分享成功获得能量加倍卡
# 系统消息：充值（成功、失败）、订阅（成功、失败）、定制（成功、失败）、版本更新（修复、添加）
# 充值和订阅--点击跳转历史订单页
# 定制成功--点击跳转角色列表页
# 其他消息类型不跳转
class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    messageId = Column(String(100), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), comment='关联user表userId')
    title = Column(String(255), comment='标题')
    roleId = Column(String(100), comment='关联role表roleId')
    content = Column(Text, comment='内容')  # 使用Text类型来存储大文本内容
    messageType = Column(Integer, server_default='0', nullable=False, comment='消息类别大类,0日常消息, 1系统消息')
    subType = Column(Integer, nullable=False,
                     comment='消息类别小类,0亲密度相关,1能量相关,2加倍卡,3充值,4订阅,5定制,6版本更新')
    readStatus = Column(Integer, server_default='0', comment='消息的未读已读状态,0未读,1已读')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 定义一个消息对象
class MessageObject:
    def __init__(self, clear: bool, content: str, messageType: int = 0):
        self.clear = clear
        self.content = content
        # 0是日常消息与系统消息刷新，1是聊天未读数刷新,2是gpt聊天消息模块，3是亲密度发生变化 结合clear刷新
        self.messageType = messageType

    def to_dict(self):
        return {"clear": self.clear, "content": self.content, "messageType": self.messageType}


# gpt api对接的原始记录表
# 聊天，定时任务朋友圈，总结等等
class GPTLog(Base):
    __tablename__ = "gptLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gptLogId = Column(String(100), primary_key=True, index=True, nullable=False)
    content = Column(Text, comment='内容')
    apiStatus = Column(Integer, server_default='0', comment='gpt对接状态,0成功,1失败')
    model = Column(String(100), comment='使用的gpt模型版本')
    promptTokens = Column(Integer, server_default='0', comment='gpt发送信息消耗的token')
    completionTokens = Column(Integer, server_default='0', comment='gpt返回信息消耗的token')
    totalTokens = Column(Integer, server_default='0', comment='本次api,gpt总消耗的token')
    type = Column(Integer, server_default='0', comment='类型,0聊天,1角色记忆(朋友圈),2总结任务')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 背景图片资源库
class BackgroundImage(Base):
    __tablename__ = "backgroundImage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    imageId = Column(String(255), primary_key=True, index=True, nullable=False)
    imageUrl = Column(String(255), comment='图片地址')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 反馈表
class FeedBack(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    feedBackId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    content = Column(String(255), index=True, nullable=False, comment='反馈内容')
    notify = Column(Integer, server_default='0', comment='是否允许将反馈结果发送邮件通知客户,0不允许,1允许')
    imageList = Column(String(500), comment='反馈图片地址列表,逗号隔开的多个,最多三张')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    sendEmail = Column(String(500), comment='需要发送的邮箱 如果没勾选则为null')
    updateTime = Column(BigInteger)


# 分享记录表
class ShareLog(Base):
    __tablename__ = "shareLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shareId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    result = Column(Integer, nullable=False, comment='分享结果成功还是失败,0成功, 1失败')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 推送记录表
# 推送系统消息和主动打招呼的消息
# 系统消息：充值（成功、失败）、订阅（成功、失败）、定制（成功、失败）
# 充值和订阅--点击跳转历史订单页
# 定制成功--点击跳转角色列表页
# 主动打招呼--点击跳转角色聊天页
# 其他推送类型点击启动app就行了
class pushLog(Base):
    __tablename__ = "pushLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pushId = Column(String(500), primary_key=True, index=True, nullable=False)
    userId = Column(String(500), index=True, nullable=False, comment='关联user表userId')
    responseCode = Column(Integer, comment='推送返回码')
    responseContent = Column(String(500), comment='推送返回结果,里面有第三方的消息id和其他信息')
    messageType = Column(Integer, nullable=False, comment='消息类别,0充值,1订阅,2定制,3角色打招呼')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 角色定制表
class Customization(Base):
    __tablename__ = "customization"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customId = Column(String(255), primary_key=True, index=True, nullable=False)
    orderId = Column(String(500), index=True, nullable=False, comment='订单id')
    userId = Column(String(500), index=True, nullable=False, comment='关联user表userId')
    name = Column(String(100), index=True, nullable=False, comment='角色名称')
    age = Column(Integer, comment='年龄')
    gender = Column(String(100), comment='性别,male男性,female女性,或者其他')
    avatar = Column(String(255), comment='头像地址')
    hobby = Column(String(255), comment='爱好')
    description = Column(String(255), comment='角色介绍')
    message = Column(String(255), comment='用户的其他要求')
    result = Column(String(100), server_default='0', comment='定制状态,0进行中,1成功,2失败')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 总结日志表
class SummaryLog(Base):
    __tablename__ = "summaryLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    summaryId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(500), index=True, nullable=False, comment='关联user表userId')
    roleId = Column(String(500), index=True, nullable=False, comment='关联role表roleId')
    content = Column(String(5000), comment='总结结果')
    gptLogId = Column(String(255))
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 升级表
class AppVersion(Base):
    __tablename__ = "appVersion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appVersionId = Column(String(255), primary_key=True,
                          index=True, nullable=False)
    platform = Column(String(255), comment='android还是ios平台')
    version = Column(String(255), comment='显示版本名称')
    buildId = Column(Integer, comment='版本升级关键参数')
    content = Column(String(500), comment='更新内容，英文分号隔开')
    isForce = Column(Integer, comment='0不是强制更新，1强制更新版本')
    downLoadUrl = Column(String(255), comment='下载链接')
    remark = Column(String(255), comment='备注')
    status = Column(Integer, comment='0正常状态，1删除状态')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)
