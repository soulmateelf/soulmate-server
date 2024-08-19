# -*- coding: utf-8 -*-
import datetime
import json
import threading
import uuid

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.conf.chatConf import get_random_roleId, get_random_dream_message
from soulmate_server.mapper.chat import addChatMessage
from soulmate_server.mapper.role import addRoleMemoryNotify
from soulmate_server.models import createDynamicTable
from soulmate_server.models.other import MessageObject
from soulmate_server.models.role import RoleMemory, RoleMemoryNotify
from soulmate_server.models.user import LoginLog, User, UserRoleAchievement, UserRole, IntimacyLog
from sqlalchemy import and_, desc, text

from soulmate_server.utils.mqtt import mqttCo


# 根据邮箱和密码查询用户详情
def queryUserInfo(email: str, password: str, sql: mysqlSession = None):
    user = sql.query(User).filter(
        and_(User.email == email, User.password == password, User.status == 0)).first()

    return user


# 查询所有的角色用户关联关系
def queryUserRole(sql:mysqlSession = None):
    userRole = sql.query(UserRole).filter(UserRole.status == 0).all()

    return userRole


# 查询不用特别条件的同步数据的userRole
def queryUserRoleByFilter(roleIds, userId, sql: mysqlSession = None):
    roleId_list = (
        sql.query(UserRole.roleId)
        .filter(UserRole.status == 0, UserRole.userId == userId, ~UserRole.roleId.in_(roleIds))
        .distinct()
        .all()
    )

    return [role_id for role_id, in roleId_list]


def queryUserInfoByEmail(email: str, sql: mysqlSession = None):
    user = sql.query(User).filter(
        and_(User.email == email, User.status == 0)).first()

    return user


def queryUserInfoByAppId(appLoginId: str, sql: mysqlSession = None):
    user = sql.query(User).filter(
        and_(User.appLoginId == appLoginId, User.status == 0)).first()

    return user


# 根据id查询用户详情
def queryUserInfoById(userId: str, sql: mysqlSession = None):
    user = sql.query(User).filter(
        and_(User.userId == userId, User.status == 0)).first()

    return user


async def asyncQueryUserInfoById(userId: str, sql: mysqlSession = None):
    user = sql.query(User).filter(
        and_(User.userId == userId, User.status == 0)).first()

    return user


def queryUserInfoList(page, size, sql: mysqlSession = None):
    offset = (page - 1) * size
    messages = sql.query(User).filter(
        and_(User.status == 0)).order_by(
        desc(User.createTime)).limit(size).offset(offset).all()


def updateUserNameById(userId: str, newNickName, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update({User.nickName: newNickName})

    return True


# 查询最新的一条登录日志
def queryLoginLog(userId: str, sql: mysqlSession = None):
    loginLog = sql.query(LoginLog).filter(LoginLog.userId == userId).order_by(
        desc(LoginLog.createTime)).first()

    return loginLog


# 新增一条登录日志
def addLoginLog(loginLogRecord, sql: mysqlSession = None):
    sql.add(loginLogRecord)

    return True


# 注册接口
def registerUser(user, sql: mysqlSession = None):
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    sql.add(user)
    roleIds = get_random_roleId()
    if roleIds is not None and len(roleIds) > 0:
        for roleId in roleIds:
            userRole = UserRole(
                userRoleId=uuid.uuid4().hex,
                userId=user.userId,
                roleId=roleId,
                createTime=int(datetime.datetime.now().timestamp() * 1000)
            )
            sql.add(userRole)
            # 创建动态表,返回动态类
            UserChatClass = createDynamicTable(user.userId, tablePrefix='chat')
            chatRecord = UserChatClass(chatId=uuid.uuid4().hex, roleId=roleId, content=get_random_dream_message(),
                                       role='assistant',
                                       createTime=timestamp,
                                       updateTime=timestamp, inputType=0, readStatus=0)
            sendMess = {"chatId": chatRecord.chatId,
                        "roleId": chatRecord.roleId,
                        "content": chatRecord.content,
                        "role": chatRecord.role,
                        "createTime": chatRecord.createTime,
                        "readStatus": chatRecord.readStatus,
                        "inputType": chatRecord.inputType,
                        "voiceUrl": chatRecord.voiceUrl,
                        "voiceSize": chatRecord.voiceSize,
                        "tokenSize": chatRecord.tokenSize}
            if sendMess.get("content") is not None:
                sendMess.update({"content": sendMess.get("content").replace('"', "'")})
            # 发送消息
            mq = mqttCo
            me = MessageObject(clear=False, content=json.dumps(sendMess), messageType=2)
            me_dict = me.to_dict()
            js = json.dumps(me_dict)
            mq.publish(topic=user.userId, message=str(js))

            addChatMessage(sql, chatRecord)

    # t = threading.Thread(target=syncRoleMemoryNewUser, args=[user.userId])
    # t.start()
    return True


def syncRoleMemoryNewUser(userId: str, sql=mysqlSession):
    memory = sql.query(RoleMemory).all()
    for it in memory:
        addRoleMemoryNotify(RoleMemoryNotify(
            notifyId=uuid.uuid4().hex,
            userId=userId,
            roleId=it.roleId,
            createTime=int(datetime.datetime.now().timestamp() * 1000),
            status=0,
            memoryId=it.memoryId,
            publishTime=it.publishTime
        ), sql=sql)
    sql.commit()
    sql.expire_all()


if __name__ == '__main__':
    sql = mysqlSession
    memory = sql.query(RoleMemory).all()
    users = sql.query(User).filter(User.status == 0).all()
    for user in users:
        for it in memory:
            addRoleMemoryNotify(RoleMemoryNotify(
                notifyId=uuid.uuid4().hex,
                userId=user.userId,
                roleId=it.roleId,
                createTime=int(datetime.datetime.now().timestamp() * 1000),
                status=0,
                memoryId=it.memoryId,
                publishTime=it.publishTime
            ), sql=sql)
    sql.commit()
    sql.expire_all()


# 修改密码接口
def updatePassword(email: str, password: str):
    mysqlSession.query(User).filter(User.email == email).update({User.password: password})
    mysqlSession.commit()

    return True


# 注销账号
def deleteUser(userId: str, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update({User.status: 1})

    return True


def updatePasswordByUserId(userId: str, password: str, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update({User.password: password})

    return True


def selectUserInfoByUserIdAndPassword(userId, password, sql: mysqlSession = None):
    user = sql.query(User).filter(
        User.userId == userId, User.password == password, User.status == 0).first()

    return user


def updateemErgencyContact(userId: str, status: int, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update({User.emergencyContact: status})

    return True


# 修改用户卡
def updateUserCard(userId: str, userCard: str, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update({User.setting: userCard})

    return True


def selectUserInfo():
    user_results = mysqlSession.execute(text("SELECT * FROM user"))
    # 获取列名
    columns = user_results.keys()

    # 获取所有结果行，并将其转换为字典
    return [dict(zip(columns, row)) for row in user_results.fetchall()]


# 修改头像地址
def updateAvatar(userId, avatar):
    mysqlSession.query(User).filter(User.userId == userId).update({User.avatar: avatar})
    mysqlSession.commit()

    return True


# 根据用户id与角色id查询与当前角色的成就表
def selectUserRoleAchievement(userId, roleId, sql=None):
    result = sql.query(UserRoleAchievement).filter(UserRoleAchievement.userId == userId,
                                                   UserRoleAchievement.roleId == roleId).all()

    return result


async def asyncSelectUserRoleAchievement(userId, roleId):
    result = mysqlSession.query(UserRoleAchievement).filter(UserRoleAchievement.userId == userId,
                                                            UserRoleAchievement.roleId == roleId).all()

    return result


def addAchievementDetails(userRoleAchievement, sql: mysqlSession = None):
    sql.add(userRoleAchievement)

    return True


# 增加用户角色表的亲密度值
def addIntimacy(userId, roleId, intimacy, sql: mysqlSession = None):
    userRole = sql.query(UserRole).filter(UserRole.userId == userId, UserRole.roleId == roleId, UserRole.status == 0,
                                          UserRole.intimacy < 100).first()
    if userRole is None:
        return False
    if userRole.intimacy + intimacy >= 100:
        userRole.intimacy = 100
    else:
        userRole.intimacy = userRole.intimacy + intimacy
    mq = mqttCo
    me = MessageObject(clear=True, content="亲密度发生变化", messageType=3)
    me_dict = me.to_dict()
    js = json.dumps(me_dict)
    mq.publish(topic=userId, message=str(js))
    return True


# 减少用户角色表的亲密度值
def reduceIntimacy(userId, roleId, intimacy, sql: mysqlSession = None):
    sql.query(UserRole).filter(UserRole.userId == userId, UserRole.roleId == roleId, UserRole.status == 0,
                               UserRole.intimacy > 20).update(
        {UserRole.intimacy: UserRole.intimacy - intimacy})
    mq = mqttCo
    me = MessageObject(clear=True, content="亲密度发生变化", messageType=3)
    me_dict = me.to_dict()
    js = json.dumps(me_dict)
    mq.publish(topic=userId, message=str(js))
    return True


# 添加亲密度变动记录
def addIntimacyDetails(intimacyDetails, sql: mysqlSession = None):
    sql.add(intimacyDetails)

    return True


# 查询亲密度变动记录
def selectTodayIntimacyDetails(userId, roleId):
    # 获取今天的日期和明天的日期
    today_date = datetime.datetime.now().date()
    tomorrow_date = today_date + datetime.timedelta(days=1)
    result = mysqlSession.query(IntimacyLog).filter(IntimacyLog.userId == userId, IntimacyLog.roleId == roleId,
                                                    IntimacyLog.createTime >= today_date,
                                                    IntimacyLog.createTime < tomorrow_date,
                                                    IntimacyLog.type == 0,
                                                    IntimacyLog.triggerType == 0).all()

    return result


# 添加反馈
def addFeedBack(sql, feedBack):
    sql.add(feedBack)
    sql.commit()
    return True


# 根据用户id修改用户聊天模式
def updateUserChatModel(userId, chatMode,sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.model: chatMode})

    return True


def updateUserSoSEmail(userId, emergencyEmail, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.emergencyEmail: emergencyEmail})

    return True


# 减少用户能量
def reduceUserEnergy(userId, energy, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId, User.energy > 0).update(
        {User.energy: energy})
    return True


def reduceUserEnergyBy0(userId, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.energy: 0})
    return True


async def asyncReduceUserEnergy(userId, energy, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.energy: energy})
    return True


# 更改用户引导选项
def updateUserGuide(userId, chooseRoleId, oneChoose, towChoose, threeChoose, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.oneChoose: oneChoose, User.towChoose: towChoose, User.threeChoose: threeChoose,
         User.chooseRoleId: chooseRoleId})
    return True


# 新增用户能量
def addUserEnergy(userId, energy, sql: mysqlSession = None):
    sql.query(User).filter(User.userId == userId).update(
        {User.energy: User.energy + energy})
    return True


if __name__ == '__main__':
    print(selectUserInfo())
