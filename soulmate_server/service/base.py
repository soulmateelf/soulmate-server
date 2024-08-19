from fastapi.responses import JSONResponse

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.common.token import create_token
from soulmate_server.mapper.user import addLoginLog, queryUserInfo, queryLoginLog, queryUserInfoByEmail
from soulmate_server.models.user import LoginLog
from soulmate_server.utils.tool import isNotEmpty, md5Util
from soulmate_server.common.redis_tool import redis_set, redis_delete
import datetime
import asyncio
import uuid


# 登录
def loginService(email, password, pushId: str = None, platform: str = None
                 , buildNumber: str = None, sdkVersion: str = None, sql: mysqlSession = None, ):
    # 1、根据用户名密码从mysql数据库查询用户信息
    # 密码md5
    encodePwd = md5Util(password)
    userInfo = queryUserInfo(email, encodePwd, sql=sql)
    if userInfo == None:
        return None
    # 2、毫秒时间戳加userId,md5加密得出登录信息token

    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    token = create_token(userInfo.userId)
    # 3、用这个token作为key,userInfo作为value存到redis，过期时间设置为7天，异步存储
    # 这里有个优化逻辑，登录的时候设置有效期7天，每次用户交互请求接口的时候，刷新token的有效期，这一步异步操作在中间件验证登录信息之后做
    timeExpired = 7 * 24 * 60 * 60
    redis_set(token, userInfo.translateString(), prefix='login:', expireTime=timeExpired)
    # 4、查询上次的登录日志，异步删除掉之前存在redis的token
    lastLoginLog = queryLoginLog(userInfo.userId, sql=sql)
    # if lastLoginLog and isNotEmpty(lastLoginLog.token):
    #     asyncio.create_task(redis_delete(lastLoginLog.token, prefix='login:'))
    # 5、新增一条登录日志
    loginLogRecord = LoginLog(
        loginLogId=uuid.uuid4().hex,
        userId=userInfo.userId,
        loginType=0,
        pushId=pushId,
        token=token,
        # # version=params.get("version"),
        buildNumber=buildNumber,
        platform=platform,
        # deviceUuid=params.get("deviceUuid"),
        # deviceModel=params.get("deviceModel"),
        sdkVersion=sdkVersion,
        createTime=timestamp,
        updateTime=timestamp)
    addLoginLog(loginLogRecord, sql=sql)
    return {"userInfo": userInfo, "token": token}


def loginServiceType(params={}, pushId: str = None, platform: str = None
                     , buildNumber: str = None, sdkVersion: str = None,loginType :int =0, sql: mysqlSession = None):
    # 1、根据用户名密码从mysql数据库查询用户信息
    # 密码md5
    userInfo = params.get('userInfo')
    if userInfo == None:
        print("没进入日志")
        return None
    # 2、毫秒时间戳加userId,md5加密得出登录信息token

    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    token = create_token(userInfo.userId)
    # 3、用这个token作为key,userInfo作为value存到redis，过期时间设置为7天，异步存储
    # 这里有个优化逻辑，登录的时候设置有效期7天，每次用户交互请求接口的时候，刷新token的有效期，这一步异步操作在中间件验证登录信息之后做
    timeExpired = 7 * 24 * 60 * 60
    redis_set(token, userInfo.translateString(), prefix='login:', expireTime=timeExpired)
    # 4、查询上次的登录日志，异步删除掉之前存在redis的token
    lastLoginLog = queryLoginLog(userInfo.userId, sql=sql)
    if lastLoginLog is not None:
        redis_delete(lastLoginLog.token, prefix='login:')
    # if lastLoginLog and isNotEmpty(lastLoginLog.token):
    #     asyncio.create_task(redis_delete(lastLoginLog.token, prefix='login:'))
    # 5、新增一条登录日志
    loginLogRecord = LoginLog(
        loginLogId=uuid.uuid4().hex,
        userId=userInfo.userId,
        loginType=loginType,
        pushId=pushId,
        token=token,
        version=params.get("version"),
        buildNumber=buildNumber,
        platform=platform,
        deviceUuid=params.get("deviceUuid"),
        deviceModel=params.get("deviceModel"),
        sdkVersion=sdkVersion,
        createTime=timestamp,
        updateTime=timestamp)
    addLoginLog(loginLogRecord, sql=sql)
    return {"userInfo": userInfo, "token": token}


if __name__ == '__main__':
    print(md5Util("123456"))
