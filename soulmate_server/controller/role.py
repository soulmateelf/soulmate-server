import datetime
import uuid

from fastapi import APIRouter, UploadFile, Body, Depends
from fastapi import Request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.chat import deleteChatMessage
from soulmate_server.mapper.role import selectRoleByUser, selectRoleDetails, selectUserRoleBy, deleteUserRoleByUser, \
    updateUserRoleImage, selectRoleBackgroundImage, selectUserByRoleMemory, addRoleMemoryActivity, selectUserByIdMemory
from soulmate_server.mapper.user import queryUserInfoById
from soulmate_server.models.role import RoleMemory, RoleMemoryActivity

router = APIRouter(prefix='/role', tags=["role"])


@router.get("/roleList", summary="角色列表", description="用户的定制角色和系统角色")
def roleList(request: Request, page: int = 1, size: int = 10, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success", "data": selectRoleByUser(userId, page, size, sql=sql)}


@router.get("/roleListByUser", summary="聊过天的角色列表", description="用于展示聊过天的角色列表")
def roleList(request: Request, page: int = 1, size: int = 10, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    result = selectUserRoleBy(userId, page, size, sql=sql)
    return {"code": 200, "message": "success", "data": result}


@router.get("/roleInfo", summary="角色详情")
def roleInfo(request: Request, roleId: str, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success", "data": selectRoleDetails(roleId, userId, sql=sql)}


@router.get("/roleEventList", summary="角色事件(朋友圈)")
def roleEventList(request: Request, roleId: str = None, page: int = 1, size: int = 10,
                  sql: Session = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success", "data": selectUserByRoleMemory(userId, roleId, sql=sql,pageNum=page,pageSize=size)}


@router.get("/roleEventById", summary="角色事件详情(朋友圈)")
def roleEventList(request: Request, memoryId: str = None, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success", "data": selectUserByIdMemory(memoryId, sql=sql)}


# 发送朋友圈评论
@router.post("/sendComment", summary="发送朋友圈评论")
def sendComment(request: Request, roleId: str = Body(..., description='角色id'),
                comment: str = Body(None, description='评论内容')
                , memoryId: str = Body(..., description='朋友圈id'),
                isAdd: bool = Body(..., description='指示是添加还是删除评论'),
                activityId: str = Body(None, description='评论id')
                , sql: Session = Depends(get_db)):
    userId = get_userId(request)
    if roleId is None:
        return {'code': 400, 'message': 'Please enter roleId！'}
    if memoryId is None:
        return {'code': 400, 'message': 'Please enter memoryId！'}

    if isAdd:
        activityId = uuid.uuid4().hex

        userInfo = queryUserInfoById(userId, sql=sql)
        if userInfo is None:
            addRoleMemoryActivity(
                RoleMemoryActivity(type=1, activityId=activityId, userId=userId, memoryId=memoryId,
                                   content=comment,
                                   createTime=int(datetime.datetime.now().timestamp() * 1000)), sql=sql)
        else:
            addRoleMemoryActivity(
                RoleMemoryActivity(type=1, activityId=activityId, userId=userId, memoryId=memoryId,
                                   content=comment, avatar=userInfo.avatar or '', userName=userInfo.nickName or '',
                                   createTime=int(datetime.datetime.now().timestamp() * 1000)), sql=sql)
    if isAdd is False:
        # 删除评论
        sql.query(RoleMemoryActivity).filter(RoleMemoryActivity.activityId == activityId).delete()

    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": "success"}


# 朋友圈点赞
@router.post("/sendLike", summary="朋友圈点赞")
def sendLike(request: Request, roleId: str = Body(..., description='角色id'),
             memoryId: str = Body(..., description='朋友圈id'),
             isAdd: bool = Body(..., description='指示是添加还是删除点赞'),
             activityId: str = Body(None, description='点赞id'), sql: Session = Depends(get_db)
             ):
    userId = get_userId(request)
    if roleId is None:
        return {'code': 400, 'message': 'Please enter roleId！'}
    if memoryId is None:
        return {'code': 400, 'message': 'Please enter memoryId！'}

    if isAdd:
        activityId = uuid.uuid4().hex

        userInfo = queryUserInfoById(userId, sql=sql)
        if userInfo is None:
            addRoleMemoryActivity(
                RoleMemoryActivity(type=0, activityId=activityId, userId=userId, memoryId=memoryId,

                                   createTime=int(datetime.datetime.now().timestamp() * 1000)), sql=sql)
        else:
            addRoleMemoryActivity(
                RoleMemoryActivity(type=0, activityId=activityId, avatar=userInfo.avatar or '', userId=userId,
                                   memoryId=memoryId, userName=userInfo.nickName or '',
                                   createTime=int(datetime.datetime.now().timestamp() * 1000)), sql=sql)
    if isAdd is False:
        # 删除点赞
        sql.query(RoleMemoryActivity).filter(RoleMemoryActivity.activityId == activityId).delete()

    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": "success"}


# 删除聊过天角色关系
@router.post("/deleteUserRole", summary="删除聊过天角色关系")
def deleteUserRole(request: Request, params: dict = Body(..., description="参数"), sql: Session = Depends(get_db)):
    if params.get("roleId") is None:
        return {'code': 400, 'message': 'Please enter roleId！'}
    userId = get_userId(request)
    deleteUserRoleByUser(userId, params.get("roleId"), sql=sql)
    deleteChatMessage(userId, params.get("roleId"), sql=sql)
    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": "success"}


# 设置用户角色聊天背景板
@router.post("/setRoleChatBackground", summary="设置用户角色聊天背景板")
def setRoleChatBackground(request: Request, roleId: str = Body(..., description="角色id"),
                          imagesId: str = Body(..., description="图片id"), sql: Session = Depends(get_db)):
    userId = get_userId(request)
    if roleId is None:
        return {'code': 400, 'message': 'Please enter roleId！'}
    if imagesId is None:
        return {'code': 400, 'message': 'Please enter imagesId！'}
    if userId is None:
        return {'code': 400, 'message': 'Please enter userId！'}
    # fileName = uuid.uuid4().hex
    # filePath = '/data/roleBackground/' + fileName
    # with open(filePath, "wb") as f:
    #     f.write(file.file.read())
    # savaPath = 'http://54.177.82.194/api/static/roleBackground/' + fileName

    res = updateUserRoleImage(userId, roleId, imagesId, sql=sql)
    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": "success"}


# 查询当前角色所有背景
@router.get("/selectRoleBackgroundImage", summary="查询当前角色所有背景")
def selectRoleBackgroundImageByRoleId(roleId: str):
    if roleId is None:
        return {'code': 400, 'message': 'Please enter roleId！'}
    return {"code": 200, "message": "success", "data": selectRoleBackgroundImage(roleId)}
