# -*- coding: utf-8 -*-

from time import sleep

import anyio
from fastapi import APIRouter

from soulmate_server.common.redis_tool import redis_set

router = APIRouter(prefix='/test', tags=["test"])

@router.get("/testSync")
async def sync():
    #测试同步
    await te()


@router.get("/testRet")
def sync():
    #测试同步
    return {"谢谢你"}

async def te():
    await anyio.sleep(10)
    redis_set('123', '123', expireTime=10)