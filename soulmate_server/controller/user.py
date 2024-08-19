from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import JSONResponse

from soulmate_server.common.mysql_tool import Session, get_db, mysqlSession
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.user import queryUserInfoById, updateemErgencyContact, updateUserNameById, queryUserInfoList
from soulmate_server.models.user import User
from soulmate_server.utils.excelUtil import downloadUserData

router = APIRouter(prefix='/user', tags=["user"])


@router.get("/userList", summary="用户列表", description="用户列表")
def userList(page: int = 1, size: int = 10, sql: Session = Depends(get_db)):
    # 错误可以在这里处 理，如果不处理，会被全局的异常处理中间件捕获
    return {"code": 200, "message": "success", "data": queryUserInfoList(page=page, size=size, sql=sql)}


@router.get("/userInfo", summary="用户详情")
def getUserInfo(request: Request, userId: str = None, sql: Session = Depends(get_db)):
    if userId != None:
        return {"code": 200, "message": "success", "data": queryUserInfoById(userId, sql=sql)}
    else:
        return JSONResponse(content='userId is None', status_code=500)


@router.get("/updateEemergency", summary="编辑紧急联系人状态")
def getUserInfo(request: Request, status: int = None, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    updateemErgencyContact(userId, status, sql=sql)
    sql.commit()
    if userId != None:
        return {"code": 200, "message": "success", "data": 'true'}
    else:
        return JSONResponse(content='userId is None', status_code=500)


# 修改名称
@router.get("/updateName", summary="修改名称")
def updateName(request: Request, newName: str = None, sql: Session = Depends(get_db)):
    userId = get_userId(request)

    userInfo = updateUserNameById(userId, newNickName=newName, sql=sql)
    sql.commit()
    sql.expire_all()
    if userId != None:
        return {"code": 200, "message": "success", "data": 'true'}
    else:
        return JSONResponse(content='userId is None', status_code=500)


# 下载数据
@router.get("/downloadUserData", summary="下载数据")
def downloadUser(request: Request, email: str, sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    downloadUserData(userId, email, sql=sql)
    return {"code": 200, "message": "success", "data": True}


# 查询能量
@router.get("/queryEnergy", summary="查询能量")
def queryEnergy(request: Request, sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    user = sql.query(User).filter(User.userId == userId,User.status==0).first()
    if user is None:
        return {"code": 200, "message": "success", "data": 0}

    return {"code": 200, "message": "success", "data": user.energy}
