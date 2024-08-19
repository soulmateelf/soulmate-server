from sqlalchemy import Column, Integer, String, BigInteger, Double, Text
from sqlalchemy.orm import relationship

from soulmate_server.common.mysql_tool import Base


# 商品表---看完 google pay 还需要修改
# 虚拟商品(能量包),订阅(月),定制角色
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    productId = Column(String(255), primary_key=True, index=True, nullable=False)
    amount = Column(Double, comment='商品金额')
    energy = Column(Integer, comment='能量值')
    productName = Column(String(100), comment='商品名称')
    type = Column(Integer, nullable=False, comment='商品类型,0能量包,1订阅,2定制角色')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    iosId = Column(String(255), comment='苹果商品id')
    androidId = Column(String(255), comment='安卓商品id')
    # 商品原始价格
    rawAmount = Column(Double, comment="商品原始金额")
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 订单表---看完 google pay 还需要修改
# 虚拟商品(能量包),订阅(月),定制角色
class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    orderAmount = Column(Double, comment='订单金额')
    productAmount = Column(Double, comment='商品金额')
    #商品原始金额
    rawProductAmount = Column(Double, comment='商品原始金额')
    productEnergy = Column(Integer, comment='商品能量值')
    productName = Column(String(100), comment='商品名称')
    productType = Column(Integer, nullable=False, comment='商品类型,0能量包,1订阅,2定制角色')
    productIosId = Column(String(255), comment='苹果商品id')
    productAndroidId = Column(String(255), comment='安卓商品id')
    type = Column(Integer, nullable=False, comment='订单类型,0能量包,1订阅,2定制角色')
    productId = Column(String(255), nullable=False)
    couponId = Column(String(100), comment='卡券id')
    result = Column(String(100), server_default='0', comment='订单状态,0进行中,1成功,2失败,3取消')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    paymentMethodType = Column(Integer, comment='支付方式 0：ios,1.google')
    moneyType = Column(String(255), comment='货币类型 $,待定')
    currencySymbol = Column(String(255), comment='货币符号 $,待定')
    # 产品数量
    productNum = Column(Integer, comment='产品数量')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 支付后第三方传输参数表
class Payment(Base):
    __tablename__ = "Payment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    PaymentId = Column(String(500), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    orderId = Column(String(500), index=True, nullable=False)
    receipt = Column(String(100), comment='订单金额')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    createTime = Column(BigInteger, nullable=False)
    purchaseID = Column(Text, comment='苹果返回的purchaseID')
    appleProductID = Column(Text, comment='苹果返回的appleProductID')
    transactionDate = Column(Text, comment='苹果返回的transactionDate')
    verificationDataId = Column(String(1000),
                                comment='苹果返回的verificationData 因为是个数据字段格式 不清楚是不是会有数组就做个关联id 用个单独的表存这些数据')
    updateTime = Column(BigInteger)


# 支付后第三方传输参数表子数据
class PaymentVerificationData(Base):
    __tablename__ = "PaymentVerificationData"
    id = Column(Integer, primary_key=True, autoincrement=True)
    PaymentVerificationDataId = Column(String(500), primary_key=True, index=True, nullable=False)
    PaymentId = Column(String(500), index=True, nullable=False)
    localVerificationData = Column(Text, comment='本地存储的verificationData')
    serverVerificationData = Column(Text, comment='服务器存储的verificationData')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 卡券
class Coupon(Base):
    __tablename__ = "coupon"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couponId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    title = Column(String(100), comment='卡券标题')
    ratio = Column(Integer, nullable=False, server_default='1', comment='倍率')
    origin = Column(Integer, nullable=False, server_default='0', comment='卡券来源,0分享,1订阅')
    expiredTime = Column(BigInteger, comment='卡券过期时间')
    couponStatus = Column(Integer, nullable=False, server_default='0', comment='卡券状态,0未使用,1已使用,2已过期')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 能量获取记录表
# ---看完 广告对接 还需要修改
class EnergyLog(Base):
    __tablename__ = "energyLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    energyLogId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    value = Column(Integer, nullable=False, comment='获取了多少能量')
    origin = Column(Integer, nullable=False, comment='获取来源,0虚拟商品,1订阅的每月发放,2看广告,3聊天赠送')
    orderId = Column(String(100), comment='虚拟商品和订阅记录orderId')
    advertLogId = Column(String(100), comment='看广告记录advertLogId')
    roleId = Column(String(100), comment='聊天赠送记录roleId')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 广告播放记录表
class AdvertLog(Base):
    __tablename__ = "advertLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    advertLogId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 订阅表
class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscriptionId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    productId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    payType = Column(Integer, nullable=False, comment='支付类型,0苹果,1安卓')
    # 订阅开启时间
    startTime = Column(BigInteger, nullable=False)
    # 结束时间
    endTime = Column(BigInteger)
    # 订阅单位
    orderId = Column(String(255), comment='orderId')
    unit = Column(Integer, nullable=False, comment='订阅单位,0天,1月,2年')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 订阅回调日志表
class googleSubRollBackLog(Base):
    __tablename__ = "subRollBackLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    logId = Column(String(255), primary_key=True, index=True, nullable=False)
    rollBackResponse = Column(Text, comment='回调返回信息')
    subInfoResponse = Column(Text, comment='查询订阅返回信息')
    googleOrderId = Column(String(400), comment='googleOrderId')
    orderId = Column(String(400), comment='orderId')
    subResultType = Column(Integer, nullable=False, comment='回调类型')
    googleToken = Column(Text, comment="查询google订阅信息的token")
    exception = Column(Text, comment='异常信息')
    status = Column(Integer, nullable=False, server_default='0', comment='0成功1失败')
    createTime = Column(BigInteger, nullable=False)


class appleSubRollBackLog(Base):
    __tablename__ = "appleSubRollBackLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    logId = Column(String(255), primary_key=True, index=True, nullable=False)
    rollBackResponse = Column(Text, comment='回调返回信息')
    notificationType = Column(String(400), comment='回调类型')
    notificationUUID = Column(String(400), comment='notificationUUID')
    subType = Column(Text, comment="子类型")
    transactionId = Column(Text, comment="交易id")
    originalTransactionId = Column(Text, comment="原始交易id")
    productId = Column(Text, comment="产品id")
    exception = Column(Text, comment='异常信息')
    status = Column(Integer, nullable=False, server_default='0', comment='0成功1失败')
    createTime = Column(BigInteger, nullable=False)
