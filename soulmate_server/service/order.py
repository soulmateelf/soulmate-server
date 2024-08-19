# 支付 订单 逻辑层
import base64
import json
import time
import uuid

from sqlalchemy import asc

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.conf.dataConf import environment
from soulmate_server.conf.systemConf import developGoogleRollBack
from soulmate_server.mapper.energy import add_subscrib, addEnergyLog, end_sub, getSubscriptionByOrderId, start_sub, \
    getSubByUserIdAndProductId
from soulmate_server.mapper.message import addMessageByType
from soulmate_server.mapper.order import createIosPayment, createIosPaymentVerificationData, createOrderByUser
from soulmate_server.mapper.product import select_product_by_id
from soulmate_server.mapper.user import addUserEnergy
from soulmate_server.models.energy import Payment, PaymentVerificationData, Order, Product, Subscription, Coupon, \
    EnergyLog, googleSubRollBackLog, appleSubRollBackLog
from soulmate_server.models.user import RechargeEvent
from soulmate_server.utils.googleUtil import googleSub


# async def iosPay(param={}):


# 处理苹果支付回调信息
def app_ios(mysql, userId, orderId, receipt, purchaseID, appleProductID, transactionDate, verificationData=None):
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
    createIosPayment(Payment=iosPay, mysql=mysql)
    if verificationData is not None:
        verData = verificationData
        if verData.get('localVerificationData') is not None and verData.get('serverVerificationData'):
            VerificationData = PaymentVerificationData(
                PaymentVerificationDataId=verificationId,
                PaymentId=PaymentId,
                localVerificationData=verData.get('localVerificationData'),
                serverVerificationData=verData.get('serverVerificationData'),
                createTime=int(time.time() * 1000),
            )
            createIosPaymentVerificationData(mysql, VerificationData)


# 充值后回调处理
def recharge(orderId, userId, sql: mysqlSession = None):
    date = int(time.time() * 1000)
    order = sql.query(Order).filter(Order.orderId == orderId, Order.userId == userId, Order.result == 0).first()
    if order is None:
        return
    product = sql.query(Product).filter(Product.productId == order.productId).first()
    # 倍数
    multiple = 1
    if order.couponId is not None:
        # 查询卡券
        coupon = sql.query(Coupon).filter(Coupon.couponId == order.couponId).first()
        if coupon is not None:
            if coupon.ratio is not None:
                # 查询卡券类型
                multiple = coupon.ratio
    # 循环
    for i in range(order.productNum):
        if product.type == 0:
            # 新增用户能量
            addUserEnergy(userId=userId, energy=product.energy * multiple, sql=sql)
            addEnergyLog(EnergyLog(
                energyLogId=uuid.uuid4().hex,
                userId=userId,
                value=product.energy * multiple,
                origin=0,
                orderId=orderId,
                createTime=date,
                remark='虚拟商品'
            ), sql=sql)
        if product.type == 1:
            addUserEnergy(userId=userId, energy=product.energy * multiple, sql=sql)
            # 添加订阅表
            add_subscrib(sub=Subscription(
                subscriptionId=uuid.uuid4().hex,
                userId=userId,
                payType=order.paymentMethodType,
                productId=product.productId,
                startTime=date,
                createTime=date,
                orderId=orderId,
                unit=1
            ), sql=sql)
            addEnergyLog(EnergyLog(
                energyLogId=uuid.uuid4().hex,
                userId=userId,
                value=product.energy * multiple,
                origin=1,
                orderId=orderId,
                createTime=date,
                remark='订阅'
            ), sql=sql)
    if product.type == 0:
        # 添加信息
        addMessageByType(userId=userId, num=product.energy * multiple, messageType=RechargeEvent.RECHARGE.value,
                         sql=sql)
    if product.type == 1:
        addMessageByType(userId=userId, num=product.energy * multiple, messageType=RechargeEvent.SUBSCRIPTION.value,
                         sql=sql)
    if order.couponId is not None:
        sql.query(Coupon).filter(Coupon.couponId == order.couponId).update({Coupon.status: 1})


def create_order(userId, orderType, productId, paymentMethodType, moneyType, orderAmount, productNum, couponId,currencySymbol,
                 sql: mysqlSession = None):
    product = select_product_by_id(productId, sql=sql)
    print(productId)
    sub = getSubByUserIdAndProductId(userId=userId, productId=productId, sql=sql)
    print("userI等于" + userId)
    print(sub)
    if sub is not None:
        print("已经订阅过了")
        return None
    if product is not None:
        order = Order(
            orderId=uuid.uuid4().hex,
            userId=userId,
            orderAmount=orderAmount,
            type=orderType,
            productId=productId,
            paymentMethodType=paymentMethodType,
            moneyType=moneyType,
            createTime=int(time.time() * 1000),
            result=0,
            couponId=couponId
            , productNum=productNum,
            productAmount=product.amount,
            productEnergy=product.energy,
            productName=product.productName,
            productType=product.type,
            productIosId=product.iosId,
            productAndroidId=product.androidId,
            rawProductAmount=product.rawAmount,
            currencySymbol=currencySymbol
        )
        createOrderByUser(order, sql=sql)
        return order.orderId
    else:
        return "productId is error"


async def call_fastapi_endpoint():
    # 定义你的接口路径
    endpoint_url = "http://localhost:8000/androidPurchaseNotification"  # 请替换为你的实际路径

    # 准备你的参数
    params = {
        "key1": "value1",
        "key2": "value2",
        # 添加你的其他参数
    }

    # 发送HTTP POST请求
    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint_url, json={"params": params})

    # 处理响应
    if response.status_code == 200:
        print("接口调用成功")
        print(response.json())
    else:
        print(f"接口调用失败，状态码：{response.status_code}")
        print(response.text)


import httpx


def googleRollBackSub(params: dict, sql: mysqlSession = None):
    # 解码Base64
    decoded_data = base64.b64decode(params.get('message').get('data'))
    # 将解码后的数据转换为字符串
    decoded_string = decoded_data.decode("utf-8")
    # 将字符串转换为字典
    decoded_json = json.loads(decoded_string)
    re = googleSub(decoded_json.get("subscriptionNotification").get('purchaseToken'))
    if re.get("purchaseType") is not None:
        if environment == 'production':
            if int(re.get("purchaseType")) == 0:
                # 本次回调 用的是测试账号需要跳转测试服务器
                with httpx.AsyncClient() as client:
                    response = client.post(developGoogleRollBack, json={params})
                    # 处理响应
                    if response.status_code == 200:
                        print("接口调用成功")
                        print(response.json())
                    else:
                        print(f"接口调用失败，状态码：{response.status_code}")
                        print(response.text)
                return
    subResultType = int(decoded_json.get("subscriptionNotification").get('notificationType'))
    orderId = re.get('obfuscatedExternalAccountId')
    notification_type = decoded_json.get("subscriptionNotification").get('notificationType')
    print("回调类型" + str(notification_type))
    # 取消订阅
    if subResultType == 3:
        print("取消订阅")
        end_sub(orderId, sql=sql)
    # 订阅过期 取消订阅
    if subResultType == 13:
        print("订阅过期")
        end_sub(orderId, sql=sql)
    # 订阅续订
    if subResultType == 2:
        print("订阅续订")
        # 添加能量 先获取订阅的产品id

        subInfo = getSubscriptionByOrderId(orderId, sql=sql)
        if subInfo is not None:
            productInfo = select_product_by_id(subInfo.productId, sql=sql)
            # 给用户添加能量
            addUserEnergy(userId=subInfo.userId, energy=productInfo.energy, sql=sql)
    # 恢复续订
    if subResultType == 1 or subResultType:
        print("恢复续订")
        # 先将订阅状态改成恢复
        start_sub(orderId, sql=sql)
    subRollBackLog = googleSubRollBackLog(
        logId=uuid.uuid4().hex,
        createTime=int(time.time() * 1000),
        rollBackResponse=str(params),
        subInfoResponse=str(re),
        subResultType=subResultType,
        googleToken=decoded_json.get("subscriptionNotification").get('purchaseToken'),
        orderId=orderId
    )
    sql.add(subRollBackLog)


def appleRollBackSub(params: dict, sql: mysqlSession = None):
    print('ios支付回调通知接口-start')
    header, payload, signature = params.get("signedPayload").split('.')
    res = base64.b64decode(payload + "==").decode('utf-8')
    json_data = json.loads(res)
    notificationType = json_data.get('notificationType')

    subType = json_data.get('subtype')

    notificationUUID = json_data.get('notificationUUID')
    signedTransactionInfo = json_data['data']['signedTransactionInfo']
    transactionInfoHeader, transactionInfoPayload, transactionInfoSignature = signedTransactionInfo.split(
        '.')
    transactionInfoPayload = base64.b64decode(
        transactionInfoPayload + "==").decode('utf-8')
    transactionInfoJson = json.loads(transactionInfoPayload)
    transactionId = transactionInfoJson['transactionId']
    originalTransactionId = transactionInfoJson['originalTransactionId']
    productId = transactionInfoJson['productId']
    if notificationType is not None:
        if str(notificationType).lower() == "did_change_renewal_status".lower():
            if str(subType).lower() == "auto_renew_disabled".lower():
                print("自动续订已关闭")
                orderId = selectOrderByAppleRollBackLog(originalTransactionId=originalTransactionId, sql=sql)
                if orderId is None:
                    return
                end_sub(orderId=orderId, sql=sql)
            if str(subType).lower() == "auto_renew_enabled".lower():
                print("自动续订已开启")
                orderId = selectOrderByAppleRollBackLog(originalTransactionId=originalTransactionId, sql=sql)
                if orderId is None:
                    return
                start_sub(orderId=orderId, sql=sql)
        if str(notificationType).lower() == "SUBSCRIBED".lower():
            if str(subType).lower() == "INITIAL_BUY".lower():
                print("首次订阅")

        if str(notificationType).lower() == "expired".lower():
            if str(subType).lower() == "voluntary".lower():
                print("订阅过期")
                orderId = selectOrderByAppleRollBackLog(originalTransactionId=originalTransactionId, sql=sql)
                if orderId is None:
                    return
                end_sub(orderId=orderId, sql=sql)

    sql.add(appleSubRollBackLog(
        logId=uuid.uuid4().hex,
        rollBackResponse=str(params),
        createTime=int(time.time() * 1000),
        notificationType=notificationType,
        subType=subType,
        notificationUUID=notificationUUID,
        transactionId=transactionId,
        originalTransactionId=originalTransactionId,
        productId=productId,
        status=0
    ))


def selectOrderByAppleRollBackLog(originalTransactionId, sql: mysqlSession = None):
    # Example query ordered by originalTransactionId in ascending order
    logs = sql.query(appleSubRollBackLog).filter(
        appleSubRollBackLog.originalTransactionId == originalTransactionId).order_by(
        asc(appleSubRollBackLog.createTime)).all()
    # Get the earliest log
    if logs:
        earliest_log = logs[0]
        payment = sql.query(Payment).filter(Payment.purchaseID == earliest_log.transactionId).first()
        return payment.orderId
    else:
        return None


if __name__ == '__main__':
    s = base64.b64decode(
        "eyJ2ZXJzaW9uIjoiMS4wIiwicGFja2FnZU5hbWUiOiJjbi5zb3VsbWF0ZS5lbGYiLCJldmVudFRpbWVNaWxsaXMiOiIxNzAzOTI0OTA1OTk5Iiwic3Vic2NyaXB0aW9uTm90aWZpY2F0aW9uIjp7InZlcnNpb24iOiIxLjAiLCJub3RpZmljYXRpb25UeXBlIjozLCJwdXJjaGFzZVRva2VuIjoiZW5saGVtYWdhYW1nZm9qbGFta2xraW1jLkFPLUoxT3puSW1hNTQtNVkwM0dhNTlfMklSUTJpbWo4X3JkWF9UWE4zOWxBeG5rYUhaYmRXUFpjQ3QzTk1Ecmt0alpyNWtDZ01wZHNTQ25UekdSMnl0N3l0WjJGRndWVjB3Iiwic3Vic2NyaXB0aW9uSWQiOiJtb250aF9wYWNrYWdlIn19")
    # 将解码后的数据转换为字符串
    decoded_string = s.decode("utf-8")
    # 将字符串转换为字典
    decoded_json = json.loads(decoded_string)
    print(decoded_string)
