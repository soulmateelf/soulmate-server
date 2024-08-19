# -*- coding: utf-8 -*-
# 能量

from fastapi import APIRouter, Depends, Request

from soulmate_server.common.mysql_tool import Session, get_db
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.coupon import select_coupon_by_user_id
from soulmate_server.mapper.energy import getEnergyLogList

router = APIRouter(prefix='/energy', tags=["能量模块"])


# 查询当前用户所有能量获取记录分页
@router.get("/energyHistoryList", summary="能量历史获取列表", description="能量历史获取列表")
def energyHistoryList(request: Request, page: int = 1, size: int = 10,
                      sql: Session = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success",
            "data": getEnergyLogList(userId=userId, sql=sql, pageNum=page, pageSize=size)}
