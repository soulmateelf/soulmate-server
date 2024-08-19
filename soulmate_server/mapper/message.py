# 消息表 mapper
# -*- coding: utf-8 -*-
import datetime
import json
import random
import uuid
from time import sleep

from sqlalchemy import desc, and_

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.mapper.user import queryLoginLog
from soulmate_server.models.other import Message, MessageObject
from soulmate_server.models.user import IntimacyEvent, AchievementDetails, DailyTaskDetails, RechargeEvent
from soulmate_server.utils.NotificationUtil import send
from soulmate_server.utils.mqtt import mqttCo


# 查询全部消息列表 根据用户id 分页

def queryMessageByUserId(userId: str, pageNum: int, pageSize: int, sql: mysqlSession = None, messageType: int = 0):
    offset = (pageNum - 1) * pageSize
    messages = sql.query(Message).filter(
        and_(Message.userId == userId, Message.messageType == messageType, Message.status == 0)).order_by(
        desc(Message.createTime)).limit(pageSize).offset(offset).all()

    return messages


def queryMessageReadUpdate(userId: str, updateList, sql: mysqlSession = mysqlSession,
                       ):

    # 遍历每条记录并逐一更新
    updateCount = 0
    for message in updateList:
        if message.readStatus == 0:
            message.readStatus = 1
            updateCount = updateCount + 1
    if updateCount > 0:
        mq = mqttCo
        me = MessageObject(clear=True, content="日常消息与系统消息发送已读")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
    return True


# 查询消息总未读数
def queryMessageByUserIdAndReadStatusCount(userId: str, readStatus: int, sql: mysqlSession = None):
    count = sql.query(Message).filter(
        and_(Message.userId == userId, Message.status == 0,
             Message.readStatus == readStatus)).count()

    return count


# 批量修改消息已读未读状态
def updateMessageStatusBatch(messageIds, userId, sql: mysqlSession = None):
    message = sql.query(Message).filter(Message.messageId.in_(messageIds), Message.userId == userId).update(
        {Message.readStatus: 1}, synchronize_session=False)

    return message


# 查询未读消息列表 根据用户id 分页
def queryMessageByUserIdAndReadStatus(userId: str, readStatus: int, pageNum: int, pageSize: int,
                                      sql: mysqlSession = None, messageType: int = 0):
    offset = (pageNum - 1) * pageSize
    messages = sql.query(Message).filter(
        and_(Message.userId == userId, Message.messageType == messageType, Message.status == 0,
             Message.readStatus == readStatus)).order_by(
        desc(Message.createTime)).limit(pageSize).offset(offset).all()

    return messages


# 新增消息
def addMessage(message: Message, sql: mysqlSession = None):
    sql.add(message)

    return True


# 删除消息
def deleteMessage(messageId, userId, sql: mysqlSession = None):
    message = sql.query(Message).filter(Message.messageId == messageId, Message.userId == userId).update(
        {Message.status: 1})

    return message


# 修改消息已读未读状态
def updateMessageStatus(messageId, userId, sql: mysqlSession = None):
    message = sql.query(Message).filter(Message.messageId == messageId, Message.userId == userId).update(
        {Message.readStatus: 1})

    return message


# 批量修改消息已读未读状态
def updateMessageStatusBatch(messageIds, userId, sql: mysqlSession = None):
    message = sql.query(Message).filter(Message.messageId.in_(messageIds), Message.userId == userId).update(
        {Message.readStatus: 1}, synchronize_session=False)

    return message


# 根据新增类型新增消息
def addMessageByType(userId, messageType, roleId=None, num=None, sql: mysqlSession = None):
    mq = mqttCo
    login = queryLoginLog(userId=userId, sql=sql)
    messageId = uuid.uuid4().hex
    if messageType is IntimacyEvent.AMOUNT100MESSAGE.value:
        sql.add(Message(
            messageId=messageId,
            userId=userId,
            roleId=roleId,
            messageType=0,
            subType=1,
            title="Closeness greater than 100 gives physical strength",
            content="added " + str(num) + " Point energy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Intimacy greater than 100 gives energy")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=1, pushId=login.pushId, content="added" + str(num) + "Point energy",
        #      title="Intimacy greater than 100 gives energy")

    if messageType is AchievementDetails.FIRST.value:
        sql.add(Message(
            messageId=messageId,
            messageType=0,
            subType=0,
            userId=userId,
            roleId=roleId,
            title="Achieve your first chat with a character",
            content="added 5 Point intimacy",
            createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Achieve your first chat with a character")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="added 5 Point intimacy",
        #      title="Achieve your first chat with a character")
    if messageType is AchievementDetails.COUNT10.value:
        sql.add(Message(
            messageId=messageId,
            userId=userId,
            roleId=roleId,
            messageType=0,
            subType=0,
            title="Achieve 10 chats with your character",
            content="added 10 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Achieve 10 chats with your character")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="added" + '10' + "Point intimacy",
        #      title="Achieve 10 chats with your character")
    if messageType is AchievementDetails.COUNT100.value:
        sql.add(Message(
            messageId=messageId,
            userId=userId,
            roleId=roleId,
            messageType=0,
            subType=0,
            title="Achieve 100 chats with characters",
            content="added 10 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Achieve 100 chats with characters")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="added" + '10' + "Point intimacy",
        #      title="Achieve 100 chats with characters")
    if messageType is DailyTaskDetails.TODAY.value:
        sql.add(Message(
            messageId=messageId,
            userId=userId,
            messageType=0,
            subType=0,
            roleId=roleId,
            title="Chat with characters daily",
            content="added 1 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Chat with characters daily")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="added" + '1' + "Point intimacy",
        #      title="Chat with characters daily")
    if messageType is DailyTaskDetails.TODAYCOUNT10.value:
        sql.add(Message(
            messageId=messageId,
            userId=userId,
            roleId=roleId,
            messageType=0,
            subType=0,
            title="Chat with the character ten sentences a day",
            content="added 2 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Chat with the character ten sentences a day")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="added" + '2' + "Point intimacy",
        #      title="Chat with the character ten sentences a day")
    if messageType is DailyTaskDetails.TODAYNOTTALK50.value:
        sql.add(Message(
            messageId=messageId,
            messageType=0,
            subType=0,
            userId=userId,
            roleId=roleId,
            title="Not chatting with the character yesterday deducted intimacy",
            content="diminished 1 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Not chatting with the character yesterday deducted intimacy")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="diminished" + '1' + "Point intimacy",
        #      title="Not chatting with the character yesterday deducted intimacy")
    if messageType is DailyTaskDetails.NOTTALK50DOWN.value:
        sql.add(Message(
            messageId=uuid.uuid4().hex,
            messageType=0,
            subType=0,
            userId=userId,
            roleId=roleId,
            title="Two days without chatting with the character subtract intimacy",
            content="diminished 1 Point intimacy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Two days without chatting with the character subtract intimacy")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        # send(subType=0, pushId=login.pushId, content="diminished" + '1' + "Point intimacy",
        #      title="Two days without chatting with the character subtract intimacy")
    if messageType is RechargeEvent.RECHARGE.value:
        sql.add(Message(
            messageId=messageId,
            messageType=1,
            subType=3,
            userId=userId,

            title="Power pack purchased successfully",
            content="added " + str(num) + " Point energy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Power pack purchased successfully")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        send(subType=3, pushId=login.pushId, content="added" + str(num) + "Point energy",
             title="Power pack purchased successfully")
    if messageType is RechargeEvent.SUBSCRIPTION.value:
        sql.add(Message(
            messageId=messageId,
            messageType=1,
            subType=4,
            userId=userId,

            title="Subscribe successfully",
            content="added " + str(num) + " Point energy"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Subscribe successfully")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        send(subType=4, pushId=login.pushId, content="added" + str(num) + "Point energy",
             title="Subscribe successfully")
    if messageType is RechargeEvent.role.value:
        sql.add(Message(
            messageId=messageId,
            messageType=1,
            subType=5,
            userId=userId,

            title="Role purchase success",
            content="It's being rushed"
            , createTime=int(datetime.datetime.now().timestamp() * 1000)
        ))
        me = MessageObject(clear=True, content="Role purchase success")
        me_dict = me.to_dict()
        js = json.dumps(me_dict)
        mq.publish(topic=userId, message=str(js))
        send(subType=5, pushId=login.pushId, content="It's being rushed", title="Role purchase success")
    return messageId


if __name__ == '__main__':
    for i in range(12):
        print(uuid.uuid4().hex)
