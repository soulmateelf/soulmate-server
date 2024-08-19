# 订单充值
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import Order, Coupon


# ios支付
def createOrderByUser(order, sql: mysqlSession = None):
    sql.add(order)


# 查询订单
def queryOrderList(userId, pageNum, pageSize, sql: mysqlSession = None):
    # 分页
    offset = (pageNum - 1) * pageSize
    order = sql.query(Order).filter(Order.userId == userId, Order.result != 0).order_by(desc(Order.createTime)).limit(
        pageSize).offset(offset).all()

    return order


# 删除订单
def deleteOrder(orderId, userId):
    order = mysqlSession.query(Order).filter(Order.orderId == orderId, Order.userId == userId).update({Order.status: 1})

    mysqlSession.commit()

    return order


def createIosPayment(Payment, mysql: mysqlSession = None):
    mysql.add(Payment)


def createIosPaymentVerificationData(mysql, PaymentVerificationData):
    mysql.add(PaymentVerificationData)


# 修改订单状态
def updateOrderStatus(orderId, userId, sql: mysqlSession = None):
    sql.query(Order).filter(Order.orderId == orderId, Order.userId == userId).update({Order.result: 1})


def updateOrderFailureStatus(orderId, userId, status=None, sql: mysqlSession = None):
    sql.query(Order).filter(Order.orderId == orderId, Order.userId == userId).update(
        {Order.result: 2, Order.result: status})


# 查询卡卷
def queryCardList(userId, pageNum, pageSize, sql: mysqlSession = None):
    # 分页
    offset = (pageNum - 1) * pageSize
    order = sql.query(Coupon).filter(Coupon.userId == userId).order_by(desc(Coupon.createTime)).limit(
        pageSize).offset(offset).all()

    return order
