import datetime
import json
import threading
import traceback
import uuid
from typing import List

from fastapi import APIRouter, Request, UploadFile, Form, Body, Depends, BackgroundTasks
from slowapi.util import get_remote_address
from sqlalchemy import desc

from soulmate_server.aysnc import process_background_task
from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db
from soulmate_server.common.redis_tool import setExKey, existsKey, redis_get, redis_delete
from soulmate_server.common.token import get_userId, get_userToken, get_token
from soulmate_server.conf.systemConf import file_path
from soulmate_server.mapper.chat import addChatMessage
from soulmate_server.mapper.role import selectRoleByRoleId, addRoleMemoryNotify

from soulmate_server.mapper.user import updatePassword, registerUser, queryUserInfoByEmail, updateAvatar, \
    queryUserInfoById, addFeedBack, updateUserChatModel, updateUserSoSEmail, queryUserInfoByAppId, \
    updatePasswordByUserId, selectUserInfoByUserIdAndPassword, deleteUser, updateUserGuide
from soulmate_server.models import createDynamicTable
from soulmate_server.models.other import FeedBack, MessageObject, ShareLog, AppVersion
from soulmate_server.models.role import RoleMemory, RoleMemoryNotify, Role, RoleMemoryActivity

from soulmate_server.models.user import User, UserRole, UserRoleImage
from soulmate_server.service.base import loginService, loginServiceType
from soulmate_server.service.other import share_success
from soulmate_server.utils.chat import get_embedding, init_api
from soulmate_server.utils.emailUtils import sendEmail
from soulmate_server.utils.fileUtil import upload_file
from soulmate_server.utils.limitUtil import limiter
from soulmate_server.utils.mp3 import ensure_directory_exists
from soulmate_server.utils.mqtt import MqttClient, get_mq, mqttCo

from soulmate_server.utils.tool import isNotEmpty, md5Util
from soulmate_server.utils.vector import searchData

router = APIRouter(tags=["base"])


@router.post("/login", summary="登录", description="这个接口只负责邮箱密码登录")
def login(request: Request, email: str = Body(..., description="邮箱"), password: str = Body(..., description="密码")
          , pushId: str = Body(None), platform: str = Body(None)
          , buildNumber: str = Body(None), sdkVersion: str = Body(None), sql: Session = Depends(get_db)):
    # 如果没传body参数，request.json() 会报错，真尼玛坑
    # params = await request.json()
    if isNotEmpty(email) and isNotEmpty(password):
        userInfo = queryUserInfoByEmail(email, sql=sql)
        if userInfo is None:
            return {'code': 400, 'message': 'The email address is incorrect '}
        result = loginService(email, password, sql=sql)
        sql.commit()
        if result == None:
            return {"code": 500, "message": "The  password is incorrect", "data": None}
        return {"code": 200, "message": "success",
                "data": {"userInfo": result.get("userInfo"), "token": result.get("token")}}
    else:
        return {"code": 500, "message": "error", "data": {"userInfo": "parameter is empty"}}


@router.post("/logout", summary="退出登录")
def logout(request: Request, token: str = Depends(get_token)):
    redis_delete('login:' + token)
    return {"code": 200, "message": "success", "data": "success"}


@router.get("/aysncTest", summary="测试异步")
def ay(request: Request, sql: Session = Depends(get_db)):
    try:
        # # 查出所有的角色
        # roles = sql.query(Role).all()
        # # 循环角色
        # for role in roles:
        #     newId = uuid.uuid4().hex
        #     sql.query(RoleMemory).filter(RoleMemory.roleId == role.roleId).update({RoleMemory.roleId: newId})
        #     sql.query(RoleMemoryNotify).filter(RoleMemoryNotify.roleId == role.roleId).update(
        #         {RoleMemoryNotify.roleId: newId})
        #     sql.query(UserRole).filter(UserRole.roleId == role.roleId).update({UserRole.roleId: newId})
        #     sql.query(UserRoleImage).filter(UserRoleImage.roleId == role.roleId).update({UserRoleImage.roleId: newId})
        #     sql.query(Role).filter(Role.roleId == role.roleId).update({Role.roleId: newId})
        # sql.commit()

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
    except Exception as e:
        sql.rollback()
        print(e)
    return


@router.post("/sendEmail", summary="发送验证码（用于登录或者注册使用或者其他业务 通用接口）目前1是登录2是注册3是找回密码")
# @limiter.limit("1/minute", error_message='Try again in a minute')
def send(request: Request,
         type: int = Body(..., description="验证码类型,1是登录2是注册3是找回密码4是注销账号"),
         email: str = Body(..., description="邮箱")):
    # 获取参数
    print(request.headers.get("X-Real-IP"))
    print(request.client)
    if isNotEmpty(email) is False:
        return {'code': 400, 'message': 'Please enter email！'}
    if isNotEmpty(type) is False:
        return {'code': 400, 'message': 'Wrong parameters！'}

    code = sendEmail(email, type)
    email = str(str(type) + '_' + email)
    setExKey(email, 300, code)
    return {'code': 200, 'message': 'Get email successfully！'}


@router.post("/verify", tags=["校验验证码（用于登录或者注册使用或者其他业务 通用接口）目前1是登录2是注册3是找回密码"])
def verifyEmail(request: Request, email: str = Body(..., description="邮箱")
                , codeType: int = Body(..., description="验证码类型"), code: str = Body(..., description="验证码")
                , sql: Session = Depends(get_db)):
    # 获取参数

    if email is False:
        return {'code': 400, 'message': 'Please enter email！'}
    if codeType is False:
        return {'code': 400, 'message': 'Wrong parameters！'}
    if code is False:
        return {'code': 400, 'message': 'Please enter code！'}
    emailKey = str(str(codeType)) + '_' + email
    if existsKey(emailKey) == 0:
        return {'code': 400, 'message': 'The verification code is expired or incorrect'}
    redisCode = str(redis_get(emailKey))
    if code == redisCode:
        return {'code': 200, 'message': 'Verification code successfully！'}
    else:
        return {'code': 400, 'message': 'Verification code error！'}


# 注册账号
@router.post("/register", summary="注册账号")
def register(request: Request, params: dict = Body(..., description="参数"), sql: Session = Depends(get_db)):
    # 邮箱号
    if isNotEmpty(params.get("email")) is False:
        return {'code': 400, 'message': 'Please enter email！'}
    # 名称
    if isNotEmpty(params.get("nickName")) is False:
        return {'code': 400, 'message': 'Wrong parameters！'}
    # 验证码
    if isNotEmpty(params.get("code")) is False:
        return {'code': 400, 'message': 'Please enter code！'}
    # 密码
    if isNotEmpty(params.get("password")) is False:
        return {'code': 400, 'message': 'Please enter password！'}
    # 验证码类型type
    emailKey = str(params.get("codeType")) + '_' + params.get("email")
    if existsKey(emailKey) == 0:
        return {'code': 400, 'message': 'The verification code has expired or expired'}
    redisCode = redis_get(emailKey)
    if params.get("code").casefold() == str(redisCode).casefold():
        userInfo = queryUserInfoByEmail(params.get("email"), sql=sql)
        if userInfo is not None:
            return {'code': 400, 'message': 'already exist！'}
        # 注册账号
        userInfo = User(
            password=md5Util(params.get("password")),
            email=params.get("email"),
            nickName=params.get("nickName"),
            userId=uuid.uuid4().hex,
            createTime=int(datetime.datetime.now().timestamp() * 1000)
        )

        registerUser(userInfo, sql=sql)
        sql.commit()
        return {'code': 200, 'message': 'successfully！'}
    else:
        return {'code': 400, 'message': 'Verification code error！'}


# 忘记密码
@router.post("/forgetPassword", summary="忘记密码")
def forgetPassword(request: Request, email: str = Body(..., description="邮箱"),
                   newPassword: str = Body(..., description="密码"),
                   code: str = Body(..., description="验证码"), codeType: int = Body(..., description="验证码类型")):
    # 邮箱
    if isNotEmpty(email) is False:
        return {'code': 400, 'message': 'Please enter email！'}
    # 验证码
    if isNotEmpty(code) is False:
        return {'code': 400, 'message': 'Please enter code！'}
    # 密码
    if isNotEmpty(newPassword) is False:
        return {'code': 400, 'message': 'Please enter password！'}
    emailKey = str(str(codeType) + '_' + email)
    if existsKey(emailKey) == 0:
        return {'code': 400, 'message': 'The verification code has expired or expired'}
    redisCode = redis_get(emailKey)
    if code.casefold() == redisCode.casefold():
        # 修改密码
        updatePassword(email, md5Util(newPassword))
        return {'code': 200, 'message': 'update successfully！'}
    else:
        return {'code': 400, 'message': 'update error！'}


# 注销账号
@router.post("/cancelAccount", summary="注销账号")
def cancelAccount(request: Request, email: str = Body(..., description="邮箱"),
                  code: str = Body(..., description="验证码")
                  , codeType: int = Body(..., description="验证码类型"), sql: Session = Depends(get_db)):
    if isNotEmpty(email) is False:
        return {'code': 400, 'message': 'Please enter email！'}
    # 验证码
    if isNotEmpty(code) is False:
        return {'code': 400, 'message': 'Please enter code！'}
    userInfo = queryUserInfoByEmail(email, sql=sql)
    if userInfo is None:
        return {'code': 400, 'message': 'The account does not exist！'}
    emailKey = str(str(codeType) + '_' + email)
    if existsKey(emailKey) == 0:
        return {'code': 400, 'message': 'The verification code has expired or expired'}
    redisCode = redis_get(emailKey)
    if code.casefold() == redisCode.casefold():
        # 修改密码
        deleteUser(userInfo.userId, sql=sql)
        sql.commit()
        sql.expire_all()
        return {'code': 200, 'message': 'successfully deleted！'}
    else:
        return {'code': 400, 'message': 'Verification code error！ '}


@router.get("/emailExist", summary="验证邮箱是否已注册")
def emailExists(email: str, sql: Session = Depends(get_db)):
    """验证邮箱是否已注册
             @@@
             ### args
             |  args | nullable | request type | type |  remarks |
             |-------|----------|--------------|------|----------|
             | email |  false   |    request      | str  |  邮箱    |
             ### body
             ```json
              {
               "email":"礼"
                 }
             ```

             ### return
             ```json
                "code":"200",
                “message":"Does not exist！"
                "exists" :true=已存在，false=不存在
             ```
             @@@
       """

    userInfo = queryUserInfoByEmail(email, sql=sql)
    if userInfo is not None:
        return {'code': 200, 'message': 'already exist！', 'data': True}
    return {'code': 200, 'message': 'Does not exist！', 'data': False}


@router.post("/googleLogin", summary="谷歌登录接口")
def loginType(request: Request, email: str = Body(..., description="邮箱"),
              avatar: str = Body(..., description="头像地址"),
              nickName: str = Body(..., description="用户昵称"),
              threePartId: str = Body(..., description="平台登录id"),
              pushId: str = Body(None), platform: str = Body(None)
              , buildNumber: str = Body(None), sdkVersion: str = Body(None)
              , sql: Session = Depends(get_db)):
    # print("邮箱" + email + "头像" + avatar + "昵称" + nickName + "平台登录id" + threePartId, "推送pushId：\n" + pushId)

    # 校验参数
    if not isNotEmpty(email):
        print("邮箱为空")
        return {'code': 400, 'message': 'parameter error'}

    if not isNotEmpty(avatar):
        print("txiang为空")
        return {'code': 400, 'message': 'parameter error'}
    if not isNotEmpty(nickName):
        print("mc为空")
        return {'code': 400, 'message': 'parameter error'}
    if not isNotEmpty(threePartId):
        return {'code': 400, 'message': 'parameter error'}
    # 查询用户信息是否存在
    userInfo = queryUserInfoByEmail(email, sql=sql)
    params = {}
    try:
        # 查询出错
        if userInfo is None:
            print("进入注册")

            # 注册账号
            userInfo = User(
                password=md5Util("123456789"),
                email=email,
                nickName=nickName,
                userId=uuid.uuid4().hex,
                registerType=1,
                avatar=avatar,
                createTime=int(datetime.datetime.now().timestamp() * 1000)
            )

            registerUser(userInfo, sql=sql)
            params.update({'userInfo': userInfo})
            result = loginServiceType(params, pushId=pushId, platform=platform, buildNumber=buildNumber,
                                      sdkVersion=sdkVersion, loginType=1, sql=sql)
            print(result)
            sql.commit()
            sql.expire_all()
            return {'code': 200, 'message': 'login successfully', 'token': result.get('token'),
                    'data': queryUserInfoByEmail(email, sql=sql)}


        elif userInfo is not None:
            print("进入登录")
            params.update({'userInfo': userInfo})
            result = loginServiceType(params, pushId=pushId, platform=platform, buildNumber=buildNumber,
                                      sdkVersion=sdkVersion, loginType=1, sql=sql)
            print(result)
            print(userInfo)
            sql.commit()
            return {'code': 200, 'message': 'login successfully', 'token': result.get('token'), 'data': userInfo}
        sql.commit()
        sql.expire_all()
    except Exception as e:
        sql.rollback()
        print(e)
        return {'code': 500, 'message': 'login failure', 'data': {}}


@router.post("/uploadHeadImg", summary="上传头像")
def uploadHeadImg(file: UploadFile, userId: str, sql: Session = Depends(get_db)):
    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}

    savePath = upload_file(file, 'photo')
    res = updateAvatar(userId, savePath)
    sql.expire_all()
    return {"code": 200, "message": "modify successfully", "data": queryUserInfoById(userId, sql=sql)}


@router.post('/feedback', summary="反馈")
def feedback(request: Request, email: str = Form(None, description="邮箱"),
             content: str = Form(..., description="反馈内容"), files: List[UploadFile] = None,
             sql: Session = Depends(get_db)):
    userId = get_userId(request)

    if not isNotEmpty(content):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    urls = []
    if files is not None:
        for file in files:
            savePath = upload_file(file, 'feedback')
            urls.append(savePath)
    if isNotEmpty(email):
        res = addFeedBack(feedBack=FeedBack(
            userId=userId,
            feedBackId=uuid.uuid4().hex,
            content=content,
            sendEmail=email,
            createTime=int(datetime.datetime.now().timestamp() * 1000),
            notify=1,
            imageList=",".join(urls) if len(urls) > 0 else ''
        ), sql=sql)
    else:
        res = addFeedBack(feedBack=FeedBack(
            userId=userId,
            content=content,
            feedBackId=uuid.uuid4().hex,
            createTime=int(datetime.datetime.now().timestamp() * 1000),
            notify=0,
            imageList=",".join(urls) if len(urls) > 0 else ''
        ), sql=sql)
    return {'code': 200, 'message': 'succeed'}


# 切换聊天设置接口
@router.post('/settingModel', summary="切换聊天设置接口 用于切换模式")
def settingModel(request: Request, model: int = Body(..., description="模式,0简单,1普通,2高级", embed=True),sql: Session = Depends(get_db)):
    userId = get_userId(request)
    print("输出")
    print(model)
    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(model):
        return {"code": 500, "message": "parameter error"}
    updateUserChatModel(userId, model,sql =sql)
    sql.commit()
    sql.expire_all()
    return {'code': 200, 'message': 'succeed'}


# 设置紧急邮箱
@router.post('/settingEmergencyEmail', summary="设置紧急邮箱")
def setEmergencyEmail(request: Request, emergencyEmail: str = Body(..., description="紧急邮箱", embed=True),sql :mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(emergencyEmail):
        return {"code": 500, "message": "parameter error"}
    updateUserSoSEmail(userId, emergencyEmail,sql = sql )
    sql.commit()

    return {'code': 200, 'message': 'succeed'}


# app登录
@router.post("/appleLogin", summary="app登录")
def appLogin(request: Request, email: str = Body(None, description="邮箱"),
             appleLoginId: str = Body(..., description="苹果登录返回Id"), nickName: str = Body(None
            , description="用户昵称"), pushId: str = Body(None), platform: str = Body(None)
             , buildNumber: str = Body(None), sdkVersion: str = Body(None), sql: Session = Depends(get_db)):
    # 查询用户信息是否存在
    userInfo = queryUserInfoByAppId(appleLoginId, sql=sql)

    params = {}
    if email is None:
        print("邮箱为空")
    try:
        # 查询出错
        if userInfo is None:
            if email is None:
                print("邮箱为空")
                return {'code': 200, 'message': 'login failure', 'token': '', 'data': ''}
            # 注册账号
            print("进入注册")
            userInfo = User(
                password=md5Util("123456789"),
                email=email,
                nickName=nickName,
                userId=uuid.uuid4().hex,
                registerType=3,
                avatar='',
                appLoginId=appleLoginId,
                createTime=int(datetime.datetime.now().timestamp() * 1000)
            )

            registerUser(userInfo, sql=sql)
            params.update({'userInfo': userInfo})
            result = loginServiceType(params, pushId=pushId, platform=platform, buildNumber=buildNumber,
                                      sdkVersion=sdkVersion, loginType=2, sql=sql)
            sql.commit()
            sql.expire_all()
            return {'code': 200, 'message': 'login successfully', 'token': result.get('token'),
                    'data': queryUserInfoByAppId(appleLoginId, sql=sql)}
        elif userInfo is not None:
            print("进入登录")
            params.update({'userInfo': userInfo})
            result = loginServiceType(params, pushId=pushId, platform=platform, buildNumber=buildNumber,
                                      sdkVersion=sdkVersion, loginType=2, sql=sql)
            sql.commit()
            return {'code': 200, 'message': 'login successfully', 'token': result.get('token'), 'data': userInfo}
    except Exception as e:
        sql.rollback()
        print(e)
        traceback.print_exc()
        return {'code': 500, 'message': 'login failure', 'data': {}}


# 根据原密码修改账号
@router.post("/updatePasswordByOld", summary="根据原密码修改账号")
def updatePassWordByOld(request: Request, oldPassword: str = Body(None, description="旧密码"),
                        newPassword: str = Body(None, description="新密码"), sql: Session = Depends(get_db)):
    userId = get_userId(request)

    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(oldPassword):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(newPassword):
        return {"code": 500, "message": "parameter error"}
    userInfo = selectUserInfoByUserIdAndPassword(userId, md5Util(oldPassword), sql=sql)
    # 未查出就表示密码错误
    if userInfo is None:
        return {"code": 500, "message": "password error"}
    userInfo.password = md5Util(newPassword)

    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "succeed"}


@router.get("/createImage", summary="生成图片")
def createImage(request: Request, text: str):
    if not isNotEmpty(text):
        return {"code": 500, "message": "parameter error"}
    return {"code": 200, "message": init_api(text)}


# 校验密码是否正确
@router.get("/verifyPassword", summary="校验密码是否正确")
def verifyPassword(request: Request, password: str,sql: Session = Depends(get_db)):
    userId = get_userId(request)

    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(password):
        return {"code": 500, "message": "parameter error"}
    userInfo = selectUserInfoByUserIdAndPassword(userId, md5Util(password),sql = sql)
    # 未查出就表示密码错误
    if userInfo is None:
        return {"code": 500, "message": "password error"}
    return {"code": 200, "message": "succeed"}


# 初始引导
@router.post("/guide", summary="初始引导")
def guide(request: Request, chooseRoleId: str = Body(..., description="选择的角色id")
          , oneChoose: str = Body(..., description="第一个选项"),
          towChoose: str = Body(..., description="第二个选项")
          , threeChoose: str = Body(..., description="第三个选项")
          , chooseType: int = Body(..., description="选择类型 0走招呼语 1不需要"), sql: Session = Depends(get_db)):
    userId = get_userId(request)
    if not isNotEmpty(oneChoose):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(chooseRoleId):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(threeChoose):
        return {"code": 500, "message": "parameter error"}
    if not isNotEmpty(towChoose):
        return {"code": 500, "message": "parameter error"}
    if chooseType == 1:
        updateUserGuide(userId, chooseRoleId, oneChoose, towChoose, threeChoose, sql=sql)
    if chooseType == 0:
        print("这是进来的RoleId 引导"+chooseRoleId)
        updateUserGuide(userId, chooseRoleId, oneChoose, towChoose, threeChoose, sql=sql)
        role = selectRoleByRoleId(chooseRoleId, sql)
        if role is not None:
            # 创建动态表,返回动态类
            if role.guide is not None:
                UserChatClass = createDynamicTable(userId, tablePrefix='chat')
                chatRecord = UserChatClass(chatId=uuid.uuid4().hex, roleId=chooseRoleId, content=role.guide,
                                           role='assistant',
                                           createTime=int(datetime.datetime.now().timestamp() * 1000),
                                           updateTime=int(datetime.datetime.now().timestamp() * 1000), inputType=0)
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
                mq.publish(topic=userId, message=str(js))
                addChatMessage(sql, chatRecord)

    sql.commit()
    return {"code": 200, "message": "succeed", "data": ""}


@router.get("/share")
def share(request: Request, sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    if not isNotEmpty(userId):
        return {"code": 500, "message": "parameter error"}
    result = share_success(sql=sql, userId=userId, shareLog=ShareLog(
        shareId=uuid.uuid4().hex,
        userId=userId,
        result=0,
        createTime=int(datetime.datetime.now().timestamp() * 1000)
    ))
    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": result, "data": True}


@router.get("/appVersion")
def getAppVersion(request: Request, platform, buildId, sql: mysqlSession = Depends(get_db)):
    version = (
        sql.query(AppVersion)
        .filter(AppVersion.platform == platform, AppVersion.buildId > buildId,AppVersion.status==0)
        .order_by(desc(AppVersion.createTime))
        .first()
    )
    if version is None:
        return {"code": 200, "message": "succeed", "data": None}

    return {"code": 200, "message": "succeed", "data": version}


if __name__ == '__main__':
    user = User(userId='123', password='123', email='123', nickName='123', registerType=1, avatar='123')

    # 将user 转成json
    print()
