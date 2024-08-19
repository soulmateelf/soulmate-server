# -*- coding: utf-8 -*-
import re

# 添加订阅表内容
from sqlalchemy import desc

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import EnergyLog, Subscription


def add_subscrib(sub, sql: mysqlSession = None):
    sql.add(sub)


# 将订阅表的状态改成结束
def end_sub(orderId, sql: mysqlSession = None):
    sql.query(Subscription).filter(Subscription.orderId == orderId).update({Subscription.status: 1})


def getSubByUserIdAndProductId(userId, productId, sql: mysqlSession = None):
    return sql.query(Subscription).filter(Subscription.userId == userId, Subscription.productId == productId,
                                          Subscription.status == 0).first()


def start_sub(orderId, sql: mysqlSession = None):
    sql.query(Subscription).filter(Subscription.orderId == orderId).update({Subscription.status: 0})


# 通过订单id 获取订阅信息
def getSubscriptionByOrderId(orderId, sql: mysqlSession = None):
    return sql.query(Subscription).filter(Subscription.orderId == orderId, Subscription.status == 0).first()


# 查询获取能力表记录
def getEnergyLogList(userId, pageNum, pageSize, sql: mysqlSession = None):
    offset = (pageNum - 1) * pageSize
    result = sql.query(EnergyLog).filter(EnergyLog.userId == userId).order_by(desc(EnergyLog.createTime)).limit(
        pageSize).offset(offset).all()
    return result


# 新增获取能量记录
def addEnergyLog(energyLog, sql: mysqlSession = None):
    sql.add(energyLog)


if __name__ == '__main__':
    def find_prohibited_words(text, prohibited_words):
        found_words = []
        for word in prohibited_words:
            pattern = re.compile(fr'\b{re.escape(word)}\b', flags=re.IGNORECASE)
            match = pattern.search(text)
            if match:
                found_words.append(match.group())
        return found_words


    prohibited_words_list = ["违禁词1", "违禁词2", "违禁词3"]
    input_text = "这是一段违包含 违禁词1。"

    found_words = find_prohibited_words(input_text, prohibited_words_list)

    if found_words:
        print("文字包含违禁词:", found_words)
    else:
        print("文字没有违禁词。")