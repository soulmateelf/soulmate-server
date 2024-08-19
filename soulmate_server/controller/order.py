# -*- coding: utf-8 -*-
import asyncio
import base64
import json
import threading
import time
import traceback
import uuid

from fastapi import APIRouter, Request, Body, Form, UploadFile, Depends

from soulmate_server.common.mysql_tool import mysqlSession, Session, get_db
from soulmate_server.common.token import get_userId
from soulmate_server.mapper.message import addMessageByType
from soulmate_server.mapper.order import queryOrderList, createOrderByUser, createIosPayment, \
    createIosPaymentVerificationData, updateOrderStatus, updateOrderFailureStatus, queryCardList
from soulmate_server.models.energy import Order, Payment, PaymentVerificationData, googleSubRollBackLog, \
    appleSubRollBackLog
from soulmate_server.models.user import RechargeEvent
from soulmate_server.service.order import app_ios, recharge, create_order, googleRollBackSub, appleRollBackSub
from soulmate_server.service.role import user_customization
from soulmate_server.utils.fileUtil import upload_file

router = APIRouter(prefix='/order', tags=["order"])


@router.get("/orderList", summary="订单列表", description="订单列表")
def orderList(request: Request, page: int = 1, size: int = 10, sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)

    return {"code": 200, "message": "success", "data": queryOrderList(userId, page, size, sql=sql)}


# 创建订单
@router.post("/createOrder", summary="创建订单", description="创建订单")
def createOrder(request: Request, orderAmount: float = Body(..., description="订单金额", embed=True),
                orderType: int = Body(...,
                                      description="订单类型", embed=True),
                productId: str = Body(...,
                                      description="商品id", embed=True),
                paymentMethodType: int = Body(...,
                                              description="支付方式", embed=True),
                moneyType: str = Body(...,
                                      description="货币类型", embed=True),
                couponId: str = Body(None),
                productNum: int = Body(
                    1, description="商品数量", embed=True),
                currencySymbol: str = Body(None, description="货币符号 $,待定"),
                sql: mysqlSession = Depends(get_db)):
    """创建订单接口
           @@@
           ### args
           |  args | nullable | request type | type |  remarks |
           |-------|----------|--------------|------|----------|
           | orderAmount |  false   |    body    | Integer  |  订单金额    |
            | type |  false   |    body    | Integer  |  订单类型    |
            | productId |  false   |    body    | Integer  |  商品id    |
            | paymentMethodType |  false   |    body    | Integer  |  支付方式    |
            | moneyType |  false   |    body    | Integer  |  货币类型    |
                            | couponId |  false   |    body    | Integer  |  卡券id    |
              ### return orderId

    """
    if orderAmount is None:
        return {'code': 400, 'message': 'Please enter orderAmount！'}
    if orderType is None:
        return {'code': 400, 'message': 'Please enter type！'}
    if productId is None:
        return {'code': 400, 'message': 'Please enter productId！'}
    if paymentMethodType is None:
        return {'code': 400, 'message': 'Please enter paymentMethodType！'}
    if moneyType is None:
        return {'code': 400, 'message': 'Please enter moneyType！'}
    orderId = create_order(userId=get_userId(request), orderAmount=orderAmount, orderType=orderType,
                           productId=productId,
                           paymentMethodType=paymentMethodType, moneyType=moneyType, couponId=couponId,
                           productNum=productNum,
                          currencySymbol=currencySymbol, sql=sql)
    if orderId is None:
        return {"code": 200, "message": "You've already subscribed", "data": None}
    sql.commit()
    sql.expire_all()
    return {"code": 200, "message": "success", "data": orderId}


@router.post("/iosPay", summary="苹果支付后回调存信息", description="苹果支付")
def iosPay(request: Request, orderId: str = Body(..., description="订单id", embed=True),
           receipt: float = Body(..., description="苹果支付金额", embed=True),
           purchaseID: str = Body(...,
                                  description="苹果返回的purchaseID", embed=True),
           appleProductID: str = Body(...,
                                      description="苹果返回的appleProductID", embed=True),
           transactionDate: str = Body(...,
                                       description="苹果返回的transactionDate", embed=True),
           verificationData: dict = Body(
               ..., description="苹果返回的verificationData", embed=True),
           sql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    try:
        if orderId is None:
            return {'code': 400, 'message': 'Please enter orderId！'}
        verificationId = uuid.uuid4().hex
        PaymentId = uuid.uuid4().hex
        iosPay = Payment(
            PaymentId=PaymentId,
            userId=userId,
            orderId=orderId,
            receipt=receipt,
            createTime=int(time.time() * 1000),
            purchaseID=purchaseID,
            appleProductID=appleProductID,
            transactionDate=transactionDate,
            verificationDataId=verificationId
        )
        createIosPayment(Payment=iosPay, mysql=sql)
        if verificationData is not None:
            verData = verificationData
            if verData.get('localVerificationData') is not None and verData.get('serverVerificationData'):
                VerificationData = PaymentVerificationData(
                    PaymentVerificationDataId=verificationId,
                    PaymentId=PaymentId,
                    localVerificationData=verData.get('localVerificationData'),
                    serverVerificationData=verData.get(
                        'serverVerificationData'),
                    createTime=int(time.time() * 1000),
                )
                createIosPaymentVerificationData(sql, VerificationData)

        recharge(sql=sql, orderId=orderId, userId=userId)
        updateOrderStatus(userId=userId, orderId=orderId, sql=sql)
        sql.commit()
        sql.expire_all()
    except Exception as e:
        traceback.print_exc()
        print(e)
        sql.rollback()
        updateOrderFailureStatus(userId=userId, orderId=orderId, sql=sql)
        sql.commit()
        sql.expire_all()
        return {"code": 200, "message": "failure"}

    return {"code": 200, "message": "success"}


# 订单失败 修改状态
@router.post("/orderFail")
def orderFail(request: Request, orderId: str = Body(..., description="订单id"),
              status: int = Body(..., description="订单状态"), mysql: mysqlSession = Depends(get_db)):
    userId = get_userId(request)
    updateOrderFailureStatus(
        userId=userId, orderId=orderId, status=status, sql=mysql)
    mysql.commit()
    mysql.expire_all()
    return {"code": 200, "message": "success"}


@router.post("/addCustomization", summary="定制角色付款回调接口", description="定制角色付款回调接口")
def addCustomization(request: Request, file: UploadFile = None, orderId: str = Form(..., description="订单id"),
                     receipt: float = Form(..., description="苹果支付金额"),
                     purchaseID: str = Form(...,
                                            description="苹果返回的purchaseID"),
                     appleProductID: str = Form(...,
                                                description="苹果返回的appleProductID"),
                     transactionDate: str = Form(...,
                                                 description="苹果返回的transactionDate"),
                     verificationData: str = Form(...,
                                                  description="苹果返回的verificationData"),
                     age: int = Form(..., description="年龄"),
                     gender: str = Form(..., description="性别"),
                     name: str = Form(..., description="名字"),
                     Hobby: str = Form(..., description="爱好"),
                     characterIntroduction: str = Form(
                         ..., description="性格介绍"),
                     remark: str = Form(None, description="备注（用于补充）"),
                     mysql: mysqlSession = Depends(get_db)
                     ):
    verification_data_dict = json.loads(verificationData)

    userId = get_userId(request)
    # 处理苹果支付后回调数据
    app_ios(mysql=mysql, userId=userId, orderId=orderId, receipt=receipt, purchaseID=purchaseID,
            transactionDate=transactionDate, verificationData=verification_data_dict, appleProductID=appleProductID)
    # 推送
    addMessageByType(userId=userId, messageType=RechargeEvent.role.value, roleId=None, sql=mysql)
    savePath = ""
    if file is not None:
        savePath = upload_file(file, 'customization')
    threading.Thread(target=user_customization,
                     args=[userId, age, orderId, gender, name, savePath, Hobby, characterIntroduction, remark]).start()
    mysql.query(Order).filter(Order.orderId == orderId,
                              Order.userId == userId).update({Order.result: 1})
    mysql.commit()
    mysql.expire_all()

    return {"code": 200, "message": "success"}


# ios 服务端月度订阅回调接口


@router.post("/iosPurchaseNotification", summary="apple支付回调接口(支付/订阅/取消订阅)",
             description="apple支付回调接口(支付/订阅/取消订阅)")
def addCustomization(request: Request, params: dict = Body(..., description="参数"),
                     sql: mysqlSession = Depends(get_db)):
    print('ios支付回调通知接口-start')

    print(params)
    try:
        appleRollBackSub(params, sql=sql)
        sql.commit()
        return {"code": 200, "message": "success"}
    except Exception as e:
        print(e)
        sql.rollback()
        sql.add(appleSubRollBackLog(
            logId=uuid.uuid4().hex,
            createTime=int(time.time() * 1000),
            rollBackResponse=json.dumps(params),
            status=1,
            exception=str(e.__str__())
        ))
        sql.commit()
        sql.expire_all()
        traceback.print_exc()

        return {"code": 200, "message": "failure"}


# android 服务端月度订阅回调接口


@router.post("/androidPurchaseNotification", summary="android支付回调接口", description="android支付回调接口")
def addCustomization(request: Request, params: dict = Body(..., description="参数"),
                     sql: mysqlSession = Depends(get_db)):
    print('android 服务端月度订阅回调接口-start')
    print(params)

    try:
        googleRollBackSub(params, sql=sql)
        sql.commit()
        sql.expire_all()
    except Exception as e:
        print(e)
        traceback.print_exc()
        sql.rollback()
        sql.add(googleSubRollBackLog(
            logId=uuid.uuid4().hex,
            createTime=int(time.time() * 1000),
            rollBackResponse=json.dumps(params),
            status=1,
            exception=str(e.__str__())
        ))
        sql.commit()
        # 添加日志
    return {"code": 200, "message": "success"}


if __name__ == '__main__':
    taskType = 1
    o = 1 if taskType == 1 else 0
    print(str(o))
    # base = "eyJhbGciOiJFUzI1NiIsIng1YyI6WyJNSUlFTURDQ0E3YWdBd0lCQWdJUWZUbGZkMGZOdkZXdnpDMVlJQU5zWGpBS0JnZ3Foa2pPUFFRREF6QjFNVVF3UWdZRFZRUURERHRCY0hCc1pTQlhiM0pzWkhkcFpHVWdSR1YyWld4dmNHVnlJRkpsYkdGMGFXOXVjeUJEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURUxNQWtHQTFVRUN3d0NSell4RXpBUkJnTlZCQW9NQ2tGd2NHeGxJRWx1WXk0eEN6QUpCZ05WQkFZVEFsVlRNQjRYRFRJek1Ea3hNakU1TlRFMU0xb1hEVEkxTVRBeE1URTVOVEUxTWxvd2daSXhRREErQmdOVkJBTU1OMUJ5YjJRZ1JVTkRJRTFoWXlCQmNIQWdVM1J2Y21VZ1lXNWtJR2xVZFc1bGN5QlRkRzl5WlNCU1pXTmxhWEIwSUZOcFoyNXBibWN4TERBcUJnTlZCQXNNSTBGd2NHeGxJRmR2Y214a2QybGtaU0JFWlhabGJHOXdaWElnVW1Wc1lYUnBiMjV6TVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1Rc3dDUVlEVlFRR0V3SlZVekJaTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEEwSUFCRUZFWWUvSnFUcXlRdi9kdFhrYXVESENTY1YxMjlGWVJWLzB4aUIyNG5DUWt6UWYzYXNISk9OUjVyMFJBMGFMdko0MzJoeTFTWk1vdXZ5ZnBtMjZqWFNqZ2dJSU1JSUNCREFNQmdOVkhSTUJBZjhFQWpBQU1COEdBMVVkSXdRWU1CYUFGRDh2bENOUjAxREptaWc5N2JCODVjK2xrR0taTUhBR0NDc0dBUVVGQndFQkJHUXdZakF0QmdnckJnRUZCUWN3QW9ZaGFIUjBjRG92TDJObGNuUnpMbUZ3Y0d4bExtTnZiUzkzZDJSeVp6WXVaR1Z5TURFR0NDc0dBUVVGQnpBQmhpVm9kSFJ3T2k4dmIyTnpjQzVoY0hCc1pTNWpiMjB2YjJOemNEQXpMWGQzWkhKbk5qQXlNSUlCSGdZRFZSMGdCSUlCRlRDQ0FSRXdnZ0VOQmdvcWhraUc5Mk5rQlFZQk1JSCtNSUhEQmdnckJnRUZCUWNDQWpDQnRneUJzMUpsYkdsaGJtTmxJRzl1SUhSb2FYTWdZMlZ5ZEdsbWFXTmhkR1VnWW5rZ1lXNTVJSEJoY25SNUlHRnpjM1Z0WlhNZ1lXTmpaWEIwWVc1alpTQnZaaUIwYUdVZ2RHaGxiaUJoY0hCc2FXTmhZbXhsSUhOMFlXNWtZWEprSUhSbGNtMXpJR0Z1WkNCamIyNWthWFJwYjI1eklHOW1JSFZ6WlN3Z1kyVnlkR2xtYVdOaGRHVWdjRzlzYVdONUlHRnVaQ0JqWlhKMGFXWnBZMkYwYVc5dUlIQnlZV04wYVdObElITjBZWFJsYldWdWRITXVNRFlHQ0NzR0FRVUZCd0lCRmlwb2RIUndPaTh2ZDNkM0xtRndjR3hsTG1OdmJTOWpaWEowYVdacFkyRjBaV0YxZEdodmNtbDBlUzh3SFFZRFZSME9CQllFRkFNczhQanM2VmhXR1FsekUyWk9FK0dYNE9vL01BNEdBMVVkRHdFQi93UUVBd0lIZ0RBUUJnb3Foa2lHOTJOa0Jnc0JCQUlGQURBS0JnZ3Foa2pPUFFRREF3Tm9BREJsQWpFQTh5Uk5kc2twNTA2REZkUExnaExMSndBdjVKOGhCR0xhSThERXhkY1BYK2FCS2pqTzhlVW85S3BmcGNOWVVZNVlBakFQWG1NWEVaTCtRMDJhZHJtbXNoTnh6M05uS20rb3VRd1U3dkJUbjBMdmxNN3ZwczJZc2xWVGFtUllMNGFTczVrPSIsIk1JSURGakNDQXB5Z0F3SUJBZ0lVSXNHaFJ3cDBjMm52VTRZU3ljYWZQVGp6Yk5jd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NakV3TXpFM01qQXpOekV3V2hjTk16WXdNekU1TURBd01EQXdXakIxTVVRd1FnWURWUVFERER0QmNIQnNaU0JYYjNKc1pIZHBaR1VnUkdWMlpXeHZjR1Z5SUZKbGJHRjBhVzl1Y3lCRFpYSjBhV1pwWTJGMGFXOXVJRUYxZEdodmNtbDBlVEVMTUFrR0ExVUVDd3dDUnpZeEV6QVJCZ05WQkFvTUNrRndjR3hsSUVsdVl5NHhDekFKQmdOVkJBWVRBbFZUTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVic1FLQzk0UHJsV21aWG5YZ3R4emRWSkw4VDBTR1luZ0RSR3BuZ24zTjZQVDhKTUViN0ZEaTRiQm1QaENuWjMvc3E2UEYvY0djS1hXc0w1dk90ZVJoeUo0NXgzQVNQN2NPQithYW85MGZjcHhTdi9FWkZibmlBYk5nWkdoSWhwSW80SDZNSUgzTUJJR0ExVWRFd0VCL3dRSU1BWUJBZjhDQVFBd0h3WURWUjBqQkJnd0ZvQVV1N0Rlb1ZnemlKcWtpcG5ldnIzcnI5ckxKS3N3UmdZSUt3WUJCUVVIQVFFRU9qQTRNRFlHQ0NzR0FRVUZCekFCaGlwb2RIUndPaTh2YjJOemNDNWhjSEJzWlM1amIyMHZiMk56Y0RBekxXRndjR3hsY205dmRHTmhaek13TndZRFZSMGZCREF3TGpBc29DcWdLSVltYUhSMGNEb3ZMMk55YkM1aGNIQnNaUzVqYjIwdllYQndiR1Z5YjI5MFkyRm5NeTVqY213d0hRWURWUjBPQkJZRUZEOHZsQ05SMDFESm1pZzk3YkI4NWMrbGtHS1pNQTRHQTFVZER3RUIvd1FFQXdJQkJqQVFCZ29xaGtpRzkyTmtCZ0lCQkFJRkFEQUtCZ2dxaGtqT1BRUURBd05vQURCbEFqQkFYaFNxNUl5S29nTUNQdHc0OTBCYUI2NzdDYUVHSlh1ZlFCL0VxWkdkNkNTamlDdE9udU1UYlhWWG14eGN4ZmtDTVFEVFNQeGFyWlh2TnJreFUzVGtVTUkzM3l6dkZWVlJUNHd4V0pDOTk0T3NkY1o0K1JHTnNZRHlSNWdtZHIwbkRHZz0iLCJNSUlDUXpDQ0FjbWdBd0lCQWdJSUxjWDhpTkxGUzVVd0NnWUlLb1pJemowRUF3TXdaekViTUJrR0ExVUVBd3dTUVhCd2JHVWdVbTl2ZENCRFFTQXRJRWN6TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd0hoY05NVFF3TkRNd01UZ3hPVEEyV2hjTk16a3dORE13TVRneE9UQTJXakJuTVJzd0dRWURWUVFEREJKQmNIQnNaU0JTYjI5MElFTkJJQzBnUnpNeEpqQWtCZ05WQkFzTUhVRndjR3hsSUVObGNuUnBabWxqWVhScGIyNGdRWFYwYUc5eWFYUjVNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVFzd0NRWURWUVFHRXdKVlV6QjJNQkFHQnlxR1NNNDlBZ0VHQlN1QkJBQWlBMklBQkpqcEx6MUFjcVR0a3lKeWdSTWMzUkNWOGNXalRuSGNGQmJaRHVXbUJTcDNaSHRmVGpqVHV4eEV0WC8xSDdZeVlsM0o2WVJiVHpCUEVWb0EvVmhZREtYMUR5eE5CMGNUZGRxWGw1ZHZNVnp0SzUxN0lEdll1VlRaWHBta09sRUtNYU5DTUVBd0hRWURWUjBPQkJZRUZMdXczcUZZTTRpYXBJcVozcjY5NjYvYXl5U3JNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdEZ1lEVlIwUEFRSC9CQVFEQWdFR01Bb0dDQ3FHU000OUJBTURBMmdBTUdVQ01RQ0Q2Y0hFRmw0YVhUUVkyZTN2OUd3T0FFWkx1Tit5UmhIRkQvM21lb3locG12T3dnUFVuUFdUeG5TNGF0K3FJeFVDTUcxbWloREsxQTNVVDgyTlF6NjBpbU9sTTI3amJkb1h0MlFmeUZNbStZaGlkRGtMRjF2TFVhZ002QmdENTZLeUtBPT0iXX0.eyJub3RpZmljYXRpb25UeXBlIjoiU1VCU0NSSUJFRCIsInN1YnR5cGUiOiJJTklUSUFMX0JVWSIsIm5vdGlmaWNhdGlvblVVSUQiOiJmYWM0MjY2OS0yYTM5LTRjNWUtYjYwZi0wZmRmNDA2MmM0NmUiLCJkYXRhIjp7ImFwcEFwcGxlSWQiOjY0NzM5ODM5NzMsImJ1bmRsZUlkIjoiY24uc291bG1hdGUuZWxmIiwiYnVuZGxlVmVyc2lvbiI6IjEiLCJlbnZpcm9ubWVudCI6IlNhbmRib3giLCJzaWduZWRUcmFuc2FjdGlvbkluZm8iOiJleUpoYkdjaU9pSkZVekkxTmlJc0luZzFZeUk2V3lKTlNVbEZUVVJEUTBFM1lXZEJkMGxDUVdkSlVXWlViR1prTUdaT2RrWlhkbnBETVZsSlFVNXpXR3BCUzBKblozRm9hMnBQVUZGUlJFRjZRakZOVlZGM1VXZFpSRlpSVVVSRVJIUkNZMGhDYzFwVFFsaGlNMHB6V2toa2NGcEhWV2RTUjFZeVdsZDRkbU5IVm5sSlJrcHNZa2RHTUdGWE9YVmplVUpFV2xoS01HRlhXbkJaTWtZd1lWYzVkVWxGUmpGa1IyaDJZMjFzTUdWVVJVeE5RV3RIUVRGVlJVTjNkME5TZWxsNFJYcEJVa0puVGxaQ1FXOU5RMnRHZDJOSGVHeEpSV3gxV1hrMGVFTjZRVXBDWjA1V1FrRlpWRUZzVmxSTlFqUllSRlJKZWsxRWEzaE5ha1UxVGxSRk1VMHhiMWhFVkVreFRWUkJlRTFVUlRWT1ZFVXhUV3h2ZDJkYVNYaFJSRUVyUW1kT1ZrSkJUVTFPTVVKNVlqSlJaMUpWVGtSSlJURm9XWGxDUW1OSVFXZFZNMUoyWTIxVloxbFhOV3RKUjJ4VlpGYzFiR041UWxSa1J6bDVXbE5DVTFwWFRteGhXRUl3U1VaT2NGb3lOWEJpYldONFRFUkJjVUpuVGxaQ1FYTk5TVEJHZDJOSGVHeEpSbVIyWTIxNGEyUXliR3RhVTBKRldsaGFiR0pIT1hkYVdFbG5WVzFXYzFsWVVuQmlNalY2VFZKTmQwVlJXVVJXVVZGTFJFRndRbU5JUW5OYVUwSktZbTFOZFUxUmMzZERVVmxFVmxGUlIwVjNTbFpWZWtKYVRVSk5SMEo1Y1VkVFRUUTVRV2RGUjBORGNVZFRUVFE1UVhkRlNFRXdTVUZDUlVaRldXVXZTbkZVY1hsUmRpOWtkRmhyWVhWRVNFTlRZMVl4TWpsR1dWSldMekI0YVVJeU5HNURVV3Q2VVdZellYTklTazlPVWpWeU1GSkJNR0ZNZGtvME16Sm9lVEZUV2sxdmRYWjVabkJ0TWpacVdGTnFaMmRKU1UxSlNVTkNSRUZOUW1kT1ZraFNUVUpCWmpoRlFXcEJRVTFDT0VkQk1WVmtTWGRSV1UxQ1lVRkdSRGgyYkVOT1VqQXhSRXB0YVdjNU4ySkNPRFZqSzJ4clIwdGFUVWhCUjBORGMwZEJVVlZHUW5kRlFrSkhVWGRaYWtGMFFtZG5ja0puUlVaQ1VXTjNRVzlaYUdGSVVqQmpSRzkyVERKT2JHTnVVbnBNYlVaM1kwZDRiRXh0VG5aaVV6a3paREpTZVZwNldYVmFSMVo1VFVSRlIwTkRjMGRCVVZWR1FucEJRbWhwVm05a1NGSjNUMms0ZG1JeVRucGpRelZvWTBoQ2MxcFROV3BpTWpCMllqSk9lbU5FUVhwTVdHUXpXa2hLYms1cVFYbE5TVWxDU0dkWlJGWlNNR2RDU1VsQ1JsUkRRMEZTUlhkblowVk9RbWR2Y1docmFVYzVNazVyUWxGWlFrMUpTQ3ROU1VoRVFtZG5ja0puUlVaQ1VXTkRRV3BEUW5SbmVVSnpNVXBzWWtkc2FHSnRUbXhKUnpsMVNVaFNiMkZZVFdkWk1sWjVaRWRzYldGWFRtaGtSMVZuV1c1cloxbFhOVFZKU0VKb1kyNVNOVWxIUm5wak0xWjBXbGhOWjFsWFRtcGFXRUl3V1ZjMWFscFRRblphYVVJd1lVZFZaMlJIYUd4aWFVSm9ZMGhDYzJGWFRtaFpiWGhzU1VoT01GbFhOV3RaV0VwclNVaFNiR050TVhwSlIwWjFXa05DYW1JeU5XdGhXRkp3WWpJMWVrbEhPVzFKU0ZaNldsTjNaMWt5Vm5sa1IyeHRZVmRPYUdSSFZXZGpSemx6WVZkT05VbEhSblZhUTBKcVdsaEtNR0ZYV25CWk1rWXdZVmM1ZFVsSVFubFpWMDR3WVZkT2JFbElUakJaV0ZKc1lsZFdkV1JJVFhWTlJGbEhRME56UjBGUlZVWkNkMGxDUm1sd2IyUklVbmRQYVRoMlpETmtNMHh0Um5kalIzaHNURzFPZG1KVE9XcGFXRW93WVZkYWNGa3lSakJhVjBZeFpFZG9kbU50YkRCbFV6aDNTRkZaUkZaU01FOUNRbGxGUmtGTmN6aFFhbk0yVm1oWFIxRnNla1V5V2s5RkswZFlORTl2TDAxQk5FZEJNVlZrUkhkRlFpOTNVVVZCZDBsSVowUkJVVUpuYjNGb2EybEhPVEpPYTBKbmMwSkNRVWxHUVVSQlMwSm5aM0ZvYTJwUFVGRlJSRUYzVG05QlJFSnNRV3BGUVRoNVVrNWtjMnR3TlRBMlJFWmtVRXhuYUV4TVNuZEJkalZLT0doQ1IweGhTVGhFUlhoa1kxQllLMkZDUzJwcVR6aGxWVzg1UzNCbWNHTk9XVlZaTlZsQmFrRlFXRzFOV0VWYVRDdFJNREpoWkhKdGJYTm9Ubmg2TTA1dVMyMHJiM1ZSZDFVM2RrSlViakJNZG14Tk4zWndjekpaYzJ4V1ZHRnRVbGxNTkdGVGN6VnJQU0lzSWsxSlNVUkdha05EUVhCNVowRjNTVUpCWjBsVlNYTkhhRkozY0RCak1tNTJWVFJaVTNsallXWlFWR3A2WWs1amQwTm5XVWxMYjFwSmVtb3dSVUYzVFhkYWVrVmlUVUpyUjBFeFZVVkJkM2RUVVZoQ2QySkhWV2RWYlRsMlpFTkNSRkZUUVhSSlJXTjZUVk5aZDBwQldVUldVVkZNUkVJeFFtTklRbk5hVTBKRVdsaEtNR0ZYV25CWk1rWXdZVmM1ZFVsRlJqRmtSMmgyWTIxc01HVlVSVlJOUWtWSFFURlZSVU5uZDB0UldFSjNZa2RWWjFOWE5XcE1ha1ZNVFVGclIwRXhWVVZDYUUxRFZsWk5kMGhvWTA1TmFrVjNUWHBGTTAxcVFYcE9la1YzVjJoalRrMTZXWGROZWtVMVRVUkJkMDFFUVhkWGFrSXhUVlZSZDFGbldVUldVVkZFUkVSMFFtTklRbk5hVTBKWVlqTktjMXBJWkhCYVIxVm5Va2RXTWxwWGVIWmpSMVo1U1VaS2JHSkhSakJoVnpsMVkzbENSRnBZU2pCaFYxcHdXVEpHTUdGWE9YVkpSVVl4WkVkb2RtTnRiREJsVkVWTVRVRnJSMEV4VlVWRGQzZERVbnBaZUVWNlFWSkNaMDVXUWtGdlRVTnJSbmRqUjNoc1NVVnNkVmw1TkhoRGVrRktRbWRPVmtKQldWUkJiRlpVVFVoWmQwVkJXVWhMYjFwSmVtb3dRMEZSV1VaTE5FVkZRVU5KUkZsblFVVmljMUZMUXprMFVISnNWMjFhV0c1WVozUjRlbVJXU2t3NFZEQlRSMWx1WjBSU1IzQnVaMjR6VGpaUVZEaEtUVVZpTjBaRWFUUmlRbTFRYUVOdVdqTXZjM0UyVUVZdlkwZGpTMWhYYzB3MWRrOTBaVkpvZVVvME5YZ3pRVk5RTjJOUFFpdGhZVzg1TUdaamNIaFRkaTlGV2taaWJtbEJZazVuV2tkb1NXaHdTVzgwU0RaTlNVZ3pUVUpKUjBFeFZXUkZkMFZDTDNkUlNVMUJXVUpCWmpoRFFWRkJkMGgzV1VSV1VqQnFRa0puZDBadlFWVjFOMFJsYjFabmVtbEtjV3RwY0c1bGRuSXpjbkk1Y2t4S1MzTjNVbWRaU1V0M1dVSkNVVlZJUVZGRlJVOXFRVFJOUkZsSFEwTnpSMEZSVlVaQ2VrRkNhR2x3YjJSSVVuZFBhVGgyWWpKT2VtTkROV2hqU0VKeldsTTFhbUl5TUhaaU1rNTZZMFJCZWt4WFJuZGpSM2hzWTIwNWRtUkhUbWhhZWsxM1RuZFpSRlpTTUdaQ1JFRjNUR3BCYzI5RGNXZExTVmx0WVVoU01HTkViM1pNTWs1NVlrTTFhR05JUW5OYVV6VnFZakl3ZGxsWVFuZGlSMVo1WWpJNU1Ga3lSbTVOZVRWcVkyMTNkMGhSV1VSV1VqQlBRa0paUlVaRU9IWnNRMDVTTURGRVNtMXBaemszWWtJNE5XTXJiR3RIUzFwTlFUUkhRVEZWWkVSM1JVSXZkMUZGUVhkSlFrSnFRVkZDWjI5eGFHdHBSemt5VG10Q1owbENRa0ZKUmtGRVFVdENaMmR4YUd0cVQxQlJVVVJCZDA1dlFVUkNiRUZxUWtGWWFGTnhOVWw1UzI5blRVTlFkSGMwT1RCQ1lVSTJOemREWVVWSFNsaDFabEZDTDBWeFdrZGtOa05UYW1sRGRFOXVkVTFVWWxoV1dHMTRlR040Wm10RFRWRkVWRk5RZUdGeVdsaDJUbkpyZUZVelZHdFZUVWt6TTNsNmRrWldWbEpVTkhkNFYwcERPVGswVDNOa1kxbzBLMUpIVG5OWlJIbFNOV2R0WkhJd2JrUkhaejBpTENKTlNVbERVWHBEUTBGamJXZEJkMGxDUVdkSlNVeGpXRGhwVGt4R1V6VlZkME5uV1VsTGIxcEplbW93UlVGM1RYZGFla1ZpVFVKclIwRXhWVVZCZDNkVFVWaENkMkpIVldkVmJUbDJaRU5DUkZGVFFYUkpSV042VFZOWmQwcEJXVVJXVVZGTVJFSXhRbU5JUW5OYVUwSkVXbGhLTUdGWFduQlpNa1l3WVZjNWRVbEZSakZrUjJoMlkyMXNNR1ZVUlZSTlFrVkhRVEZWUlVObmQwdFJXRUozWWtkVloxTlhOV3BNYWtWTVRVRnJSMEV4VlVWQ2FFMURWbFpOZDBob1kwNU5WRkYzVGtSTmQwMVVaM2hQVkVFeVYyaGpUazE2YTNkT1JFMTNUVlJuZUU5VVFUSlhha0p1VFZKemQwZFJXVVJXVVZGRVJFSktRbU5JUW5OYVUwSlRZakk1TUVsRlRrSkpRekJuVW5wTmVFcHFRV3RDWjA1V1FrRnpUVWhWUm5kalIzaHNTVVZPYkdOdVVuQmFiV3hxV1ZoU2NHSXlOR2RSV0ZZd1lVYzVlV0ZZVWpWTlVrMTNSVkZaUkZaUlVVdEVRWEJDWTBoQ2MxcFRRa3BpYlUxMVRWRnpkME5SV1VSV1VWRkhSWGRLVmxWNlFqSk5Ra0ZIUW5seFIxTk5ORGxCWjBWSFFsTjFRa0pCUVdsQk1rbEJRa3BxY0V4Nk1VRmpjVlIwYTNsS2VXZFNUV016VWtOV09HTlhhbFJ1U0dOR1FtSmFSSFZYYlVKVGNETmFTSFJtVkdwcVZIVjRlRVYwV0M4eFNEZFplVmxzTTBvMldWSmlWSHBDVUVWV2IwRXZWbWhaUkV0WU1VUjVlRTVDTUdOVVpHUnhXR3cxWkhaTlZucDBTelV4TjBsRWRsbDFWbFJhV0hCdGEwOXNSVXROWVU1RFRVVkJkMGhSV1VSV1VqQlBRa0paUlVaTWRYY3pjVVpaVFRScFlYQkpjVm96Y2pZNU5qWXZZWGw1VTNKTlFUaEhRVEZWWkVWM1JVSXZkMUZHVFVGTlFrRm1PSGRFWjFsRVZsSXdVRUZSU0M5Q1FWRkVRV2RGUjAxQmIwZERRM0ZIVTAwME9VSkJUVVJCTW1kQlRVZFZRMDFSUTBRMlkwaEZSbXcwWVZoVVVWa3laVE4yT1VkM1QwRkZXa3gxVGl0NVVtaElSa1F2TTIxbGIzbG9jRzEyVDNkblVGVnVVRmRVZUc1VE5HRjBLM0ZKZUZWRFRVY3hiV2xvUkVzeFFUTlZWRGd5VGxGNk5qQnBiVTlzVFRJM2FtSmtiMWgwTWxGbWVVWk5iU3RaYUdsa1JHdE1SakYyVEZWaFowMDJRbWRFTlRaTGVVdEJQVDBpWFgwLmV5SjBjbUZ1YzJGamRHbHZia2xrSWpvaU1qQXdNREF3TURRNU1qQXdOemM1TkNJc0ltOXlhV2RwYm1Gc1ZISmhibk5oWTNScGIyNUpaQ0k2SWpJd01EQXdNREEwT1RJd01EYzNPVFFpTENKM1pXSlBjbVJsY2t4cGJtVkpkR1Z0U1dRaU9pSXlNREF3TURBd01EUTNNRFk0TXpVeklpd2lZblZ1Wkd4bFNXUWlPaUpqYmk1emIzVnNiV0YwWlM1bGJHWWlMQ0p3Y205a2RXTjBTV1FpT2lKdGIyNTBhRjl3WVdOcllXZGxJaXdpYzNWaWMyTnlhWEIwYVc5dVIzSnZkWEJKWkdWdWRHbG1hV1Z5SWpvaU1qRTBNakU0TURnaUxDSndkWEpqYUdGelpVUmhkR1VpT2pFM01EUXlOVEk0TVRFd01EQXNJbTl5YVdkcGJtRnNVSFZ5WTJoaGMyVkVZWFJsSWpveE56QTBNalV5T0RFNE1EQXdMQ0psZUhCcGNtVnpSR0YwWlNJNk1UY3dOREkxTWprNU1UQXdNQ3dpY1hWaGJuUnBkSGtpT2pFc0luUjVjR1VpT2lKQmRYUnZMVkpsYm1WM1lXSnNaU0JUZFdKelkzSnBjSFJwYjI0aUxDSnBia0Z3Y0U5M2JtVnljMmhwY0ZSNWNHVWlPaUpRVlZKRFNFRlRSVVFpTENKemFXZHVaV1JFWVhSbElqb3hOekEwTWpVeU9EUXhPVFU1TENKbGJuWnBjbTl1YldWdWRDSTZJbE5oYm1SaWIzZ2lMQ0owY21GdWMyRmpkR2x2YmxKbFlYTnZiaUk2SWxCVlVrTklRVk5GSWl3aWMzUnZjbVZtY205dWRDSTZJbFZUUVNJc0luTjBiM0psWm5KdmJuUkpaQ0k2SWpFME16UTBNU0lzSW5CeWFXTmxJam96TWprNU1Dd2lZM1Z5Y21WdVkza2lPaUpWVTBRaWZRLnlHbzMxQ2JVSWRmelRhLUM0dklPeVV5OUg3MFUwQnpLS084dkU2OC1lV0JEazZBQUZWb3NRZkZhT2V4bFRoekJGUF9nYTNZODBCX2RYMktTVEJ1NzlnIiwic2lnbmVkUmVuZXdhbEluZm8iOiJleUpoYkdjaU9pSkZVekkxTmlJc0luZzFZeUk2V3lKTlNVbEZUVVJEUTBFM1lXZEJkMGxDUVdkSlVXWlViR1prTUdaT2RrWlhkbnBETVZsSlFVNXpXR3BCUzBKblozRm9hMnBQVUZGUlJFRjZRakZOVlZGM1VXZFpSRlpSVVVSRVJIUkNZMGhDYzFwVFFsaGlNMHB6V2toa2NGcEhWV2RTUjFZeVdsZDRkbU5IVm5sSlJrcHNZa2RHTUdGWE9YVmplVUpFV2xoS01HRlhXbkJaTWtZd1lWYzVkVWxGUmpGa1IyaDJZMjFzTUdWVVJVeE5RV3RIUVRGVlJVTjNkME5TZWxsNFJYcEJVa0puVGxaQ1FXOU5RMnRHZDJOSGVHeEpSV3gxV1hrMGVFTjZRVXBDWjA1V1FrRlpWRUZzVmxSTlFqUllSRlJKZWsxRWEzaE5ha1UxVGxSRk1VMHhiMWhFVkVreFRWUkJlRTFVUlRWT1ZFVXhUV3h2ZDJkYVNYaFJSRUVyUW1kT1ZrSkJUVTFPTVVKNVlqSlJaMUpWVGtSSlJURm9XWGxDUW1OSVFXZFZNMUoyWTIxVloxbFhOV3RKUjJ4VlpGYzFiR041UWxSa1J6bDVXbE5DVTFwWFRteGhXRUl3U1VaT2NGb3lOWEJpYldONFRFUkJjVUpuVGxaQ1FYTk5TVEJHZDJOSGVHeEpSbVIyWTIxNGEyUXliR3RhVTBKRldsaGFiR0pIT1hkYVdFbG5WVzFXYzFsWVVuQmlNalY2VFZKTmQwVlJXVVJXVVZGTFJFRndRbU5JUW5OYVUwSktZbTFOZFUxUmMzZERVVmxFVmxGUlIwVjNTbFpWZWtKYVRVSk5SMEo1Y1VkVFRUUTVRV2RGUjBORGNVZFRUVFE1UVhkRlNFRXdTVUZDUlVaRldXVXZTbkZVY1hsUmRpOWtkRmhyWVhWRVNFTlRZMVl4TWpsR1dWSldMekI0YVVJeU5HNURVV3Q2VVdZellYTklTazlPVWpWeU1GSkJNR0ZNZGtvME16Sm9lVEZUV2sxdmRYWjVabkJ0TWpacVdGTnFaMmRKU1UxSlNVTkNSRUZOUW1kT1ZraFNUVUpCWmpoRlFXcEJRVTFDT0VkQk1WVmtTWGRSV1UxQ1lVRkdSRGgyYkVOT1VqQXhSRXB0YVdjNU4ySkNPRFZqSzJ4clIwdGFUVWhCUjBORGMwZEJVVlZHUW5kRlFrSkhVWGRaYWtGMFFtZG5ja0puUlVaQ1VXTjNRVzlaYUdGSVVqQmpSRzkyVERKT2JHTnVVbnBNYlVaM1kwZDRiRXh0VG5aaVV6a3paREpTZVZwNldYVmFSMVo1VFVSRlIwTkRjMGRCVVZWR1FucEJRbWhwVm05a1NGSjNUMms0ZG1JeVRucGpRelZvWTBoQ2MxcFROV3BpTWpCMllqSk9lbU5FUVhwTVdHUXpXa2hLYms1cVFYbE5TVWxDU0dkWlJGWlNNR2RDU1VsQ1JsUkRRMEZTUlhkblowVk9RbWR2Y1docmFVYzVNazVyUWxGWlFrMUpTQ3ROU1VoRVFtZG5ja0puUlVaQ1VXTkRRV3BEUW5SbmVVSnpNVXBzWWtkc2FHSnRUbXhKUnpsMVNVaFNiMkZZVFdkWk1sWjVaRWRzYldGWFRtaGtSMVZuV1c1cloxbFhOVFZKU0VKb1kyNVNOVWxIUm5wak0xWjBXbGhOWjFsWFRtcGFXRUl3V1ZjMWFscFRRblphYVVJd1lVZFZaMlJIYUd4aWFVSm9ZMGhDYzJGWFRtaFpiWGhzU1VoT01GbFhOV3RaV0VwclNVaFNiR050TVhwSlIwWjFXa05DYW1JeU5XdGhXRkp3WWpJMWVrbEhPVzFKU0ZaNldsTjNaMWt5Vm5sa1IyeHRZVmRPYUdSSFZXZGpSemx6WVZkT05VbEhSblZhUTBKcVdsaEtNR0ZYV25CWk1rWXdZVmM1ZFVsSVFubFpWMDR3WVZkT2JFbElUakJaV0ZKc1lsZFdkV1JJVFhWTlJGbEhRME56UjBGUlZVWkNkMGxDUm1sd2IyUklVbmRQYVRoMlpETmtNMHh0Um5kalIzaHNURzFPZG1KVE9XcGFXRW93WVZkYWNGa3lSakJhVjBZeFpFZG9kbU50YkRCbFV6aDNTRkZaUkZaU01FOUNRbGxGUmtGTmN6aFFhbk0yVm1oWFIxRnNla1V5V2s5RkswZFlORTl2TDAxQk5FZEJNVlZrUkhkRlFpOTNVVVZCZDBsSVowUkJVVUpuYjNGb2EybEhPVEpPYTBKbmMwSkNRVWxHUVVSQlMwSm5aM0ZvYTJwUFVGRlJSRUYzVG05QlJFSnNRV3BGUVRoNVVrNWtjMnR3TlRBMlJFWmtVRXhuYUV4TVNuZEJkalZLT0doQ1IweGhTVGhFUlhoa1kxQllLMkZDUzJwcVR6aGxWVzg1UzNCbWNHTk9XVlZaTlZsQmFrRlFXRzFOV0VWYVRDdFJNREpoWkhKdGJYTm9Ubmg2TTA1dVMyMHJiM1ZSZDFVM2RrSlViakJNZG14Tk4zWndjekpaYzJ4V1ZHRnRVbGxNTkdGVGN6VnJQU0lzSWsxSlNVUkdha05EUVhCNVowRjNTVUpCWjBsVlNYTkhhRkozY0RCak1tNTJWVFJaVTNsallXWlFWR3A2WWs1amQwTm5XVWxMYjFwSmVtb3dSVUYzVFhkYWVrVmlUVUpyUjBFeFZVVkJkM2RUVVZoQ2QySkhWV2RWYlRsMlpFTkNSRkZUUVhSSlJXTjZUVk5aZDBwQldVUldVVkZNUkVJeFFtTklRbk5hVTBKRVdsaEtNR0ZYV25CWk1rWXdZVmM1ZFVsRlJqRmtSMmgyWTIxc01HVlVSVlJOUWtWSFFURlZSVU5uZDB0UldFSjNZa2RWWjFOWE5XcE1ha1ZNVFVGclIwRXhWVVZDYUUxRFZsWk5kMGhvWTA1TmFrVjNUWHBGTTAxcVFYcE9la1YzVjJoalRrMTZXWGROZWtVMVRVUkJkMDFFUVhkWGFrSXhUVlZSZDFGbldVUldVVkZFUkVSMFFtTklRbk5hVTBKWVlqTktjMXBJWkhCYVIxVm5Va2RXTWxwWGVIWmpSMVo1U1VaS2JHSkhSakJoVnpsMVkzbENSRnBZU2pCaFYxcHdXVEpHTUdGWE9YVkpSVVl4WkVkb2RtTnRiREJsVkVWTVRVRnJSMEV4VlVWRGQzZERVbnBaZUVWNlFWSkNaMDVXUWtGdlRVTnJSbmRqUjNoc1NVVnNkVmw1TkhoRGVrRktRbWRPVmtKQldWUkJiRlpVVFVoWmQwVkJXVWhMYjFwSmVtb3dRMEZSV1VaTE5FVkZRVU5KUkZsblFVVmljMUZMUXprMFVISnNWMjFhV0c1WVozUjRlbVJXU2t3NFZEQlRSMWx1WjBSU1IzQnVaMjR6VGpaUVZEaEtUVVZpTjBaRWFUUmlRbTFRYUVOdVdqTXZjM0UyVUVZdlkwZGpTMWhYYzB3MWRrOTBaVkpvZVVvME5YZ3pRVk5RTjJOUFFpdGhZVzg1TUdaamNIaFRkaTlGV2taaWJtbEJZazVuV2tkb1NXaHdTVzgwU0RaTlNVZ3pUVUpKUjBFeFZXUkZkMFZDTDNkUlNVMUJXVUpCWmpoRFFWRkJkMGgzV1VSV1VqQnFRa0puZDBadlFWVjFOMFJsYjFabmVtbEtjV3RwY0c1bGRuSXpjbkk1Y2t4S1MzTjNVbWRaU1V0M1dVSkNVVlZJUVZGRlJVOXFRVFJOUkZsSFEwTnpSMEZSVlVaQ2VrRkNhR2x3YjJSSVVuZFBhVGgyWWpKT2VtTkROV2hqU0VKeldsTTFhbUl5TUhaaU1rNTZZMFJCZWt4WFJuZGpSM2hzWTIwNWRtUkhUbWhhZWsxM1RuZFpSRlpTTUdaQ1JFRjNUR3BCYzI5RGNXZExTVmx0WVVoU01HTkViM1pNTWs1NVlrTTFhR05JUW5OYVV6VnFZakl3ZGxsWVFuZGlSMVo1WWpJNU1Ga3lSbTVOZVRWcVkyMTNkMGhSV1VSV1VqQlBRa0paUlVaRU9IWnNRMDVTTURGRVNtMXBaemszWWtJNE5XTXJiR3RIUzFwTlFUUkhRVEZWWkVSM1JVSXZkMUZGUVhkSlFrSnFRVkZDWjI5eGFHdHBSemt5VG10Q1owbENRa0ZKUmtGRVFVdENaMmR4YUd0cVQxQlJVVVJCZDA1dlFVUkNiRUZxUWtGWWFGTnhOVWw1UzI5blRVTlFkSGMwT1RCQ1lVSTJOemREWVVWSFNsaDFabEZDTDBWeFdrZGtOa05UYW1sRGRFOXVkVTFVWWxoV1dHMTRlR040Wm10RFRWRkVWRk5RZUdGeVdsaDJUbkpyZUZVelZHdFZUVWt6TTNsNmRrWldWbEpVTkhkNFYwcERPVGswVDNOa1kxbzBLMUpIVG5OWlJIbFNOV2R0WkhJd2JrUkhaejBpTENKTlNVbERVWHBEUTBGamJXZEJkMGxDUVdkSlNVeGpXRGhwVGt4R1V6VlZkME5uV1VsTGIxcEplbW93UlVGM1RYZGFla1ZpVFVKclIwRXhWVVZCZDNkVFVWaENkMkpIVldkVmJUbDJaRU5DUkZGVFFYUkpSV042VFZOWmQwcEJXVVJXVVZGTVJFSXhRbU5JUW5OYVUwSkVXbGhLTUdGWFduQlpNa1l3WVZjNWRVbEZSakZrUjJoMlkyMXNNR1ZVUlZSTlFrVkhRVEZWUlVObmQwdFJXRUozWWtkVloxTlhOV3BNYWtWTVRVRnJSMEV4VlVWQ2FFMURWbFpOZDBob1kwNU5WRkYzVGtSTmQwMVVaM2hQVkVFeVYyaGpUazE2YTNkT1JFMTNUVlJuZUU5VVFUSlhha0p1VFZKemQwZFJXVVJXVVZGRVJFSktRbU5JUW5OYVUwSlRZakk1TUVsRlRrSkpRekJuVW5wTmVFcHFRV3RDWjA1V1FrRnpUVWhWUm5kalIzaHNTVVZPYkdOdVVuQmFiV3hxV1ZoU2NHSXlOR2RSV0ZZd1lVYzVlV0ZZVWpWTlVrMTNSVkZaUkZaUlVVdEVRWEJDWTBoQ2MxcFRRa3BpYlUxMVRWRnpkME5SV1VSV1VWRkhSWGRLVmxWNlFqSk5Ra0ZIUW5seFIxTk5ORGxCWjBWSFFsTjFRa0pCUVdsQk1rbEJRa3BxY0V4Nk1VRmpjVlIwYTNsS2VXZFNUV016VWtOV09HTlhhbFJ1U0dOR1FtSmFSSFZYYlVKVGNETmFTSFJtVkdwcVZIVjRlRVYwV0M4eFNEZFplVmxzTTBvMldWSmlWSHBDVUVWV2IwRXZWbWhaUkV0WU1VUjVlRTVDTUdOVVpHUnhXR3cxWkhaTlZucDBTelV4TjBsRWRsbDFWbFJhV0hCdGEwOXNSVXROWVU1RFRVVkJkMGhSV1VSV1VqQlBRa0paUlVaTWRYY3pjVVpaVFRScFlYQkpjVm96Y2pZNU5qWXZZWGw1VTNKTlFUaEhRVEZWWkVWM1JVSXZkMUZHVFVGTlFrRm1PSGRFWjFsRVZsSXdVRUZSU0M5Q1FWRkVRV2RGUjAxQmIwZERRM0ZIVTAwME9VSkJUVVJCTW1kQlRVZFZRMDFSUTBRMlkwaEZSbXcwWVZoVVVWa3laVE4yT1VkM1QwRkZXa3gxVGl0NVVtaElSa1F2TTIxbGIzbG9jRzEyVDNkblVGVnVVRmRVZUc1VE5HRjBLM0ZKZUZWRFRVY3hiV2xvUkVzeFFUTlZWRGd5VGxGNk5qQnBiVTlzVFRJM2FtSmtiMWgwTWxGbWVVWk5iU3RaYUdsa1JHdE1SakYyVEZWaFowMDJRbWRFTlRaTGVVdEJQVDBpWFgwLmV5SnZjbWxuYVc1aGJGUnlZVzV6WVdOMGFXOXVTV1FpT2lJeU1EQXdNREF3TkRreU1EQTNOemswSWl3aVlYVjBiMUpsYm1WM1VISnZaSFZqZEVsa0lqb2liVzl1ZEdoZmNHRmphMkZuWlNJc0luQnliMlIxWTNSSlpDSTZJbTF2Ym5Sb1gzQmhZMnRoWjJVaUxDSmhkWFJ2VW1WdVpYZFRkR0YwZFhNaU9qRXNJbk5wWjI1bFpFUmhkR1VpT2pFM01EUXlOVEk0TkRFNU5Ua3NJbVZ1ZG1seWIyNXRaVzUwSWpvaVUyRnVaR0p2ZUNJc0luSmxZMlZ1ZEZOMVluTmpjbWx3ZEdsdmJsTjBZWEowUkdGMFpTSTZNVGN3TkRJMU1qZ3hNVEF3TUN3aWNtVnVaWGRoYkVSaGRHVWlPakUzTURReU5USTVPVEV3TURCOS5fYWxZc0dsYWpQbzhWLXNGd0RsR2MtWE41c2JHSHphRGY1NVNKREhWSlZxcWU1QmlaV3NGd3NJNTZHWnhtRWJPanZnUnVLU2dtUGVWeDVSRy10WUZqUSIsInN0YXR1cyI6MX0sInZlcnNpb24iOiIyLjAiLCJzaWduZWREYXRlIjoxNzA0MjUyODQzNTE0fQ.-XYFx0Nv5p3OL_09tkFosyRKc1IroXwoZPkPigueLAdOEdJ-qdRX1dAGuYZe8TIbVd9KOuFetoakqH0PEDOrnw"
    # header, payload, signature = base.split('.')
    # res = base64.b64decode(payload + "==").decode('utf-8')
    # jso = json.loads(res)
    # signedTransactionInfo = jso.get('data').get('signedTransactionInfo')
    # header2, payload2, signature2 = signedTransactionInfo.split('.')
    # res2 = base64.b64decode(payload2 + "==").decode('utf-8')
    # print(res)
    # print('===========================================================')
    # print('===========================================================')
    # print('===========================================================')
    # print('===========================================================')
    # print('===========================================================')
    # print(res2)
