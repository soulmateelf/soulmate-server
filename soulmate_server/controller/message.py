# ��Ϣ�ӿ�
import copy
import threading

from fastapi import APIRouter, Request, UploadFile, Form, Body, Depends

from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.message import queryMessageByUserId, queryMessageByUserIdAndReadStatusCount, \
    updateMessageStatusBatch, queryMessageReadUpdate

router = APIRouter(prefix='/message', tags=["message"])


@router.get("/messageList", summary="消息", description="列表")
def messageList(request: Request, page: int = 1, limit: int = 10, messageType: int = 0, sql: Session = Depends(get_db)):
    userId = get_userId(request)
    result = queryMessageByUserId(userId=userId, sql=sql, pageNum=page, pageSize=limit, messageType=messageType)
    user_copy = copy.deepcopy(result)
    queryMessageReadUpdate(userId=userId, sql=sql,updateList=result)
    sql.commit()
    return {"code": 200, "message": "success", "data": user_copy}


# 查看消息总未读数
@router.get("/messageNoReadCount", summary="查看消息总未读数", description="列表")
def messageNoReadCount(request: Request, sql: Session = Depends(get_db)):
    userId = get_userId(request)
    result = queryMessageByUserIdAndReadStatusCount(userId=userId, readStatus=0, sql=sql)
    return {"code": 200, "message": "success", "data": result}


# 修改消息已读未读状态
@router.post("/updateMessageStatus", summary="修改消息已读", description="列表")
def updateMessageStatus(request: Request, messageIds: list = Form(..., description="消息id"),
                        sql: Session = Depends(get_db)):
    userId = get_userId(request)
    result = updateMessageStatusBatch(messageIds=messageIds, userId=userId, sql=sql)
    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": result}
