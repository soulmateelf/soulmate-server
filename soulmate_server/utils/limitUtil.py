from fastapi import FastAPI
from fastapi.requests import Request
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import uvicorn
app = FastAPI()
# 实例化一个limiter对象，根据客户端地址进行限速
limiter = Limiter(key_func=get_remote_address)
# 指定FastApi的限速器为limiter
app.state.limiter = limiter
# 指定FastApi的异常拦截器
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)