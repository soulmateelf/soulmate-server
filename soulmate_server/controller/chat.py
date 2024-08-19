import asyncio
import os
import threading

from fastapi import APIRouter, Request, UploadFile, Form, Depends, Body, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
import asyncio

from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db
from soulmate_server.common.token import get_userId

from soulmate_server.mapper.chat import getChatMessage, getChatMessageNoReadCount
from soulmate_server.service.chat import chatService, chatRollBackSendGpt, syncData, updateAllMessageReadStatus
from soulmate_server.utils.fileUtil import get_file_extension, upload_file
from soulmate_server.utils.mp3 import ensure_directory_exists, convert_m4a_to_wav
from soulmate_server.utils.tool import isNotEmpty

router = APIRouter(prefix='/chat', tags=["chat"])

# Create ThreadPoolExecutor
executor = ThreadPoolExecutor()


@router.get("/chatList", summary="聊天列表", description="首页的聊天列表")
def chatList(page: int = 1, limit: int = 10):
    return {"code": 200, "message": "success", "data": ['1', '2', '3']}


@router.post("/sendMessage", summary="聊天",
             description="支持文本和语音聊天 body 传 message=内容 roleId=角色id ,type标识是文本还是语音 0是文本 1是语音")
def sendMessage(request: Request, file: UploadFile = None, roleId: str = Form(..., description="邮箱")
                , message_type: int = Form(..., description="类型 0是文本 1是语音"),
                lockId: str = Form(None, description="锁id"),
                messages: str = Form(None, description="文本内容"), sql: Session = Depends(get_db)):
    if isNotEmpty(message_type) is False:
        return {'code': 400, 'message': 'Please enter type！'}
    if lockId is not None:
         print("进来的锁"+lockId)
    userId = get_userId(request)
    if message_type == 0:
        if isNotEmpty(roleId) is False:
            return {'code': 400, 'message': 'Please enter roleId！'}
        if isNotEmpty(messages) is False:
            return {'code': 400, 'message': 'Please enter message！'}

        result = chatService(userId=userId, message=messages, roleId=roleId,
                             role='user', message_type=0, sql=sql, lockId=lockId)
        if result is False:
            return {"code": 200, "message": "prompt of insufficient balance", "data": None}

        return {"code": 200, "message": "success", "data": result}
    else:
        # 走语音的逻辑
        if isNotEmpty(roleId) is False:
            return {'code': 400, 'message': 'Please enter roleId！'}

        savePath = upload_file(file, 'wav', srcType=1)
        convert = convert_m4a_to_wav(savePath.get('srcPath'))

        result = chatService(userId=userId, voiceUrl=convert.get('url'), srcVoiceUrl=convert.get('srcPath'),
                             roleId=roleId,
                             role='user', message_type=1, sql=sql, lockId=lockId)
        os.remove(savePath.get('srcPath'))
        # result = await chatService(userId=userId, voiceUrl=fileSrc + '/wav/' + 'kkk.wav',
        #                            srcVoiceUrl=file_path + '/wav/' + 'kkk.wav',
        #
        #                            roleId=roleId,
        #                            role='user', message_type=1)
        if result is False:
            return {"code": 200, "message": "prompt of insufficient balance", "data": None}
        return {"code": 200, "message": "success", "data": result}


@router.get("/getMessageList", summary="聊天记录", description="查询聊天记录")
def getMessageList(request: Request, roleId: str, page: int, size: int, sql: Session = Depends(get_db)):
    userId = get_userId(request)
    result = getChatMessage(userId, roleId, page, size, sql=sql)
    return {"code": 200, "message": "success", "data": result}


# 查询所有未读聊天记录总数
@router.get("/getNoReadMessageCount", summary="查询所有未读聊天记录总数", description="查询所有未读聊天记录总数")
def getNoReadMessageCount(request: Request, sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    return {"code": 200, "message": "success", "data": getChatMessageNoReadCount(userId, sql=sql)}


# @router.get("/chatRollBack", summary="消息回调", description="收到回调后端提取消息发送gpt")
@router.post("/chatRollBack", summary="消息回调", description="收到回调后端提取消息发送gpt")
def chatRollBack(request: Request, background_tasks: BackgroundTasks,
                 roleId: str = Body(..., description="角色Id"),
                 lockId=Body(..., description="锁Id"), sql: Session = Depends(get_db)):
    if isNotEmpty(roleId) is False:
        return {'code': 400, 'message': 'Please enter roleId！'}
    userId = get_userId(request)
    print("用户id" + userId)
    t = threading.Thread(target=chatRollBackSendGpt, args=[userId, roleId, lockId])
    t.start()
    return {"code": 200, "message": "success", "data": []}


def start_background_task(userId: str, roleId: str, lockId: str):
    chatRollBackSendGpt(userId, roleId, lockId)


# 前端返回状态就行发送gpt返回消息


# 同步数据
@router.post("/chatSync", summary="同步数据", description="同步数据")
def chatSync(request: Request, roleAndChat: dict = Body(..., description="键值对 键放角色Id,值放要从那开始查的chatId"),
             sql: Session = Depends(get_db)):
    userId = get_userId(request)
    result = syncData(userId=userId, roleAndChat=roleAndChat, sql=sql)
    return {"code": 200, "message": "success", "data": result}


# 将一个角色的所有未读改成已读
@router.post("/chatRead", summary="将一个角色的所有未读改成已读", description="将一个角色的所有未读改成已读")
def chatRead(request: Request, roleId: str = Body(..., description="角色Id"),
             userId: str = Body(None, description="不用传"), sql: Session = Depends(get_db)):
    userId = get_userId(request)
    print("此次进来的roleId"+roleId)
    result = updateAllMessageReadStatus(userId=userId, roleId=roleId, sql=sql)
    return {"code": 200, "message": "success", "data": result}
