from fastapi import Request
from fastapi.responses import JSONResponse


# 定义一个全局错误处理,业务代码未处理的错误都会在这里捕获
async def handle_error(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    # 验证通过，将请求继续传递给路由操作
    except Exception as exception:
        # 捕获异常并进行错误处理
        print(str(exception))
        error_detail = {"error": "Loading failed, please try again later"}
        # 在这里你可以记录错误、发送通知等
        return JSONResponse(content=error_detail, status_code=500)
