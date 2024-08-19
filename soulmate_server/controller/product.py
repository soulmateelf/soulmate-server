# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request, Depends

from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db

from soulmate_server.mapper.product import select_product_page

router = APIRouter(prefix='/product', tags=["product"])


@router.get("/productList", summary="产品列表", description="产品列表")
def orderList(request: Request, page: int = 1, size: int = 10, productType: str = None, sql: Session = Depends(get_db)):
    # 将字符串productType根据,分割成int数组
    if productType is not None:
        productType = productType.split(',')
    else:
        productType = []
    productType = list(map(int, productType))
    return {"code": 200, "message": "success",
            "data": select_product_page(page=page, size=size, sql=sql, productType=productType)}
