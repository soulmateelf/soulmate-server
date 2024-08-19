import datetime

from fastapi import Request, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi.responses import JSONResponse
import jwt
from soulmate_server.conf.systemConf import SALT, headers
from starlette import status

from soulmate_server.common.redis_tool import redis_exist, redis_refreshTime
import asyncio

# 不需要登录信息验证的地址
exclude_routes = ['/login', '/logout', '/redoc', '/sendCode', "/sendEmail", "/verify",
                  "/register", '/aysncTest',
                  "/forgetPassword", "/docs", "/openapi.json", "/emailExist", "/googleLogin", "/appleLogin",
                  "/createImage", "/cancelAccount", "/order/iosPurchaseNotification",
                  "/order/androidPurchaseNotification","/test/**","/appVersion"]

# 全局校验token
# 定义 OAuth2 依赖项
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 用于存储 token 的类
class Global_userId:
    def __init__(self):
        self.userId = None


# 创建 TokenHolder 实例
global_userId = Global_userId()


# 定义一个全局中间件
async def check_token(request: Request, call_next):
    # 在这里进行令牌验证
    currentPath = request.url.path
    if currentPath in exclude_routes or currentPath.startswith("/static"):
        # 不需要验证登录信息的接口，往下走
        response = await call_next(request)
    else:
        # 这里需要验证登录信息
        # 先定义未验证登录信息时的返回体
        response = JSONResponse(
            content={"message": "401 Unauthorized"},
            status_code=401,
        )
        token = None
        try:
            # 获取令牌
            token = await oauth2_scheme(request)

        except Exception as exception:
            return response
        if not token:
            return response
        # 验证令牌在redis中存在与否，返回的是1 和 0
        authorized = await redis_exist(token, prefix='login:')
        if authorized == 0:
            # 不存在，返回401的response
            return response
        else:
            # 存在，继续往下走，request.state可以存储自定义的额外参数，token传递下去
            request.state.token = token
            response = await call_next(request)
            # 刷新token的时间，重新变成7天,异步操作
            # background_task是基于fastapi的接口response的，接口返回之后会自动执行
            # 那么在普通函数中，不依赖于response的地方，python自带的asyncio执行异步任务就非常棒
            timeExpired = 7 * 24 * 60 * 60
            asyncio.create_task(redis_refreshTime(
                token, prefix='login:', expireTime=timeExpired))
    return response


# 构造header

# 密钥


# 创建token
def create_token(userId):
    # 构造payload
    payload = {
        'userId': userId,
        'createTokenTime': int(datetime.datetime.now().timestamp() * 1000)
    }
    result = jwt.encode(payload=payload, key=SALT,
                        algorithm="HS256", headers=headers)

    return result


def get_userId(request: Request):
    token = request.state.token
    try:
        payload = jwt.decode(token, SALT, algorithms=[
            "HS256"], headers=headers)
        userId: str = payload.get("userId")
        if userId is None:
            return "0"
    except Exception as e:
        return "0"
    return userId

async def get_userId1(request: Request):
    token = request.state.token
    try:
        payload = jwt.decode(token, SALT, algorithms=[
            "HS256"], headers=headers)
        userId: str = payload.get("userId")
        if userId is None:
            return "0"
    except Exception as e:
        return "0"
    return userId

# 使用 Depends 获取 Authorization 头中的 Bearer 令牌
def get_token(authorization: str = Header(...)):
    if authorization.startswith('Bearer '):
        # 提取令牌部分
        bearer_token = authorization.split(' ')[1]
        return bearer_token
    else:
        # 如果 Authorization 头不是以 Bearer 开头，抛出 HTTP 异常
        raise HTTPException(status_code=401, detail='Invalid Bearer token')


async def async_get_userId(request: Request):
    token = request.state.token
    try:
        payload = jwt.decode(token, SALT, algorithms=[
            "HS256"], headers=headers)
        userId: str = payload.get("userId")
        if userId is None:
            return "0"
    except Exception as e:
        return "0"
    return userId


def get_userToken(request: Request):
    return request.state.token


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6Imp3dCJ9.eyJ1c2VySWQiOiJiZjQzYTU0MGIwZDA0NjY1ODA1MWIyYzdhOTcyZjdlNyIsImNyZWF0ZVRva2VuVGltZSI6MTcwNTQ3MzUwMTIxN30.NaNDSJ8mKasdlBPOTSncFeXhlyBREKwFXrIAUvhqfU8"
    payload = jwt.decode(token, SALT, algorithms=[
        "HS256"], headers=headers)
    print(payload)
