# -*- coding: utf-8 -*-

# 卡卷
from fastapi import APIRouter, Depends, Request

from soulmate_server.common.mysql_tool import Session, get_db
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.coupon import select_coupon_by_user_id

router = APIRouter(prefix='/coupon', tags=["卡卷模块"])


# 查询当前用户所有卡卷分页
@router.get("/couponList", summary="卡卷列表", description="卡卷列表")
def couponList(request: Request, page: int = 1, size: int = 10, sql: Session = Depends(get_db)):
    userId = get_userId(request)
    return {"code": 200, "message": "success",
            "data": select_coupon_by_user_id(user_id=userId, sql=sql, pageNum=page, pageSize=size)}
