from fastapi import FastAPI
from fastapi.requests import Request
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import uvicorn
app = FastAPI()
# ʵ����һ��limiter���󣬸��ݿͻ��˵�ַ��������
limiter = Limiter(key_func=get_remote_address)
# ָ��FastApi��������Ϊlimiter
app.state.limiter = limiter
# ָ��FastApi���쳣������
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)