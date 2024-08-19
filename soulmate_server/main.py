from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from soulmate_server.common.handle_error import handle_error
from soulmate_server.conf.chatConf import roleIds

from soulmate_server.conf.systemConf import file_path
# 路由
from soulmate_server.controller.base import router as baseRouter
from soulmate_server.controller.user import router as userRouter
from soulmate_server.controller.role import router as roleRouter
from soulmate_server.controller.chat import router as chatRouter
from soulmate_server.controller.order import router as orderRouter
from soulmate_server.controller.message import router as messageRouter
from soulmate_server.controller.product import router as product
from soulmate_server.controller.coupon import router as coupon
from soulmate_server.controller.energy import router as energy
from soulmate_server.controller.Test import router as test
from pathlib import Path
# 中间件
from soulmate_server.common.token import check_token
from soulmate_server.mapper.role import getSystemRole
from soulmate_server.utils.mqtt import MqttClient
from soulmate_server.utils.scheduler import SchedulerManager
from soulmate_server.utils.vector import ConnectionManager

main_directory = Path(__file__).parent
# app


app = FastAPI()

# 路由
app.include_router(baseRouter)
app.include_router(userRouter)
app.include_router(roleRouter)
app.include_router(chatRouter)
app.include_router(orderRouter)
app.include_router(messageRouter)
app.include_router(coupon)
app.include_router(product)
app.include_router(energy)
app.include_router(test)
app.mount("/static", StaticFiles(directory=file_path), name="data")
# 中间件
# CORSMiddleware 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# token验证
app.middleware("http")(check_token)

# 初始化调度器
scheduler_manager = SchedulerManager()
# 初始化向量数据库链接
connectionManager = ConnectionManager()


# # Initialize and connect MQTT client
# mqtt_client = MqttClient(broker_host="139.224.60.241", broker_port=1883)
# mqtt_client.connect()


# def get_mqtt_client():
#     return mqtt_client


@app.on_event("startup")
def startup_event():
    # 初始化全部角色id
    roles = getSystemRole()

    for role in roles:
        roleIds.append(role.roleId)


# 在应用退出时停止调度器
@app.on_event("shutdown")
def shutdown_event():
    scheduler_manager.stop_scheduler()


app.middleware("http")(handle_error)


# 程序运行起来之后，有两种风格的文档会自动生成
# Swagger: http://127.0.0.1:8080/docs
# ReDoc: http://127.0.0.1:8080/redoc
def main():
    uvicorn.run("soulmate_server.main:app",
                host="0.0.0.0",
                port=9999,
                reload=True)
