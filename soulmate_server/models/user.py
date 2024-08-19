from enum import Enum

from sqlalchemy import Column, Integer, String, BigInteger, Double, Text
from soulmate_server.common.mysql_tool import Base


# 用户表
# 能量都是整数---聊天扣除向上取整
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(100), primary_key=True, index=True, nullable=False)
    email = Column(String(100), primary_key=True, index=True, nullable=False, comment='邮箱')
    password = Column(String(100), comment='密码')
    nickName = Column(String(100), comment='昵称')
    avatar = Column(String(255), comment='头像地址')
    registerType = Column(Integer, comment='原始注册类型,0自主注册,1google,2facebook,3app')
    model = Column(Integer, nullable=False, server_default='1', comment='聊天模式,0简单,1普通,2高级')
    setting = Column(String(2000),
                     default='###User Card'
                             '*Name:'
                             '*Age:'
                             '*Gender:'
                             '*Nationality/Ethnicity:'
                             '*Beliefs:'
                             '*Birthday:'
                             '*Hobbies:'
                             '*Occupation:'
                             '*Communication Style:'
                             '*Cultural Background:'
                             '*Political Orientation:'
                             '*Knowledge (0-100%):'
                             '*Religious Beliefs:'
                             '####Social Relations'
                             '####Big Five Personality Model'
                             '--Openness: '
                             '--Conscientiousness: '
                             '--Extraversion: '
                             '--Agreeableness: '
                             '--Neuroticism: ',
                     comment='用户设定,根据用户的聊天数据总结的用户卡')
    energy = Column(Double, default="10", comment='用户当前能量')
    evaluate = Column(Integer, server_default='0', comment='用户是否已经评价过app,0未评价, 1已评价')
    emergencyContact = Column(Integer, server_default='0', comment='用户是否开启紧急联系人选项,0未开启, 1已开启')
    emergencyEmail = Column(String(100), comment='紧急联系人邮箱')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    appLoginId = Column(String(500), comment='app登录id')
    chooseRoleId = Column(String(100), comment='用户引导选择的角色id')
    oneChoose = Column(String(255), server_default='0', comment='引导第一个,0选择chatNow, 1选择Test')
    towChoose = Column(String(255), server_default='0', comment='引导第二个,0选择chatNow, 1选择Test')
    threeChoose = Column(String(255), server_default='0', comment='引导第三个,0选择chatNow, 1选择Test')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 登录日志表
class LoginLog(Base):
    __tablename__ = "loginLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    loginLogId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    loginType = Column(Integer, comment='登录类型,0自主登录,1google,2apple')
    threePartId = Column(Integer, comment='第三方登录的平台id')
    pushId = Column(Text, comment='推送id')
    token = Column(String(500), comment='登录信息token')
    version = Column(String(100), comment='当前软件版本')
    buildNumber = Column(String(100), comment='当前软件buildNumber')
    platform = Column(String(100), comment='当前平台,判断android,ios')
    deviceUuid = Column(String(100), comment='设备uuid')
    deviceModel = Column(String(100), comment='设备型号,比如Android 10和IOS14.5')
    sdkVersion = Column(String(100), comment='设备sdkVersion')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 用户角色关联表
class UserRole(Base):
    __tablename__ = "userRole"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userRoleId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(100), index=True, nullable=False, comment='关联user表userId')
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    intimacy = Column(Integer, server_default='0', comment='亲密度')
    imageId = Column(String(255), comment='角色背景图,关联BackgroundImage表imageId')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 角色与背景图片关系表
class UserRoleImage(Base):
    __tablename__ = "userRoleImage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roleImageId = Column(String(255), primary_key=True, index=True, nullable=False)
    roleId = Column(String(100), index=True, nullable=False, comment='关联role表roleId')
    imageId = Column(String(255), index=True, nullable=False, comment='关联BackgroundImage表imageId')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    remark = Column(String(255), comment='备注')
    createTime = Column(BigInteger, nullable=False)
    updateTime = Column(BigInteger)


# 用户角色成就表
class UserRoleAchievement(Base):
    __tablename__ = "userRoleAchievement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userRoleAchievementId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(255), index=True, nullable=False, comment='关联user表userId')
    roleId = Column(String(255), index=True, nullable=False, comment='关联role表roleId')
    status = Column(Integer, nullable=False, server_default='0', comment='0正常状态, 1删除状态')
    accomplishment = Column(String(1000), comment='成就内容')
    accomplishmentType = Column(Integer, comment='成就类型,0是聊天,1是朋友圈')
    AchievementDetails = Column(String(500), comment='成就详情')
    createTime = Column(BigInteger, nullable=False)


# 定义一个成就详情枚举类
class AchievementDetails(Enum):
    COUNT10 = "聊天达到十句句+10"
    COUNT100 = "聊天达到一百句+10"
    FIRST = "初次聊天+5"
    TodayCircleOfFriends = "当天生成高质量朋友圈+5"
    # 待定


# 定义一个亲密度赋予枚举类
class IntimacyEvent(Enum):
    AMOUNT100MESSAGE = "等于一百每次发送一次消息就随机赠送1-5的能量"


# 定义一个日常任务枚举类
class DailyTaskDetails(Enum):
    TODAY = "每日聊一次就加1"
    TODAYCOUNT10 = "每日到达10句就+2"
    # 当天不聊天亲密度50以上就-1
    TODAYNOTTALK50 = "当天不聊天亲密度50以上就-1"
    # 当天不聊天亲密度50以下就两天不聊-1
    NOTTALK50DOWN = "亲密度50以下两天不聊-1"
    # 待定


# 定义一个充值枚举类
class RechargeEvent(Enum):
    RECHARGE = "能量"
    SUBSCRIPTION = "订阅"
    role = "定制角色"


# 亲密度变动记录表
class IntimacyLog(Base):
    __tablename__ = "intimacyLog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    intimacyLogId = Column(String(255), primary_key=True, index=True, nullable=False)
    userId = Column(String(255), index=True, nullable=False, comment='关联user表userId')
    roleId = Column(String(255), index=True, nullable=False, comment='关联role表roleId')
    intimacy = Column(Integer, comment='亲密度')
    type = Column(Integer, comment='亲密度变动类型,0是新增,1是减少,2是清空')
    triggerType = Column(Integer,
                         comment='触发事件类型,0是日常任务（减少的话默认是日常任务也就是当天结算）,1是成就任务,2是亲密度事件赋予')
    triggerDetails = Column(String(500), comment='触发事件详情')
    createTime = Column(BigInteger, nullable=False)

# 验证码信息存在redis中---todo
# 向量数据库怎么对接呢？？-----todo


# 定时任务规则
# 1、角色在每周日根据自己以往的历史记忆和相关的角色的历史记忆，生成下周几天(随机记忆条数和发布时间)的记忆事件(朋友圈)；
# ----这段调用gpt生成记忆的系统设定存在配置文件里
# 2、角色打招呼事件是在每周日根据一段预设的系统设定，生成之后打招呼事件((随机2-4条和发布时间)之后，新建延迟队列，
# 在到达发布时间时，判断用户是否近期和本角色有过聊天(时间规则是什么？？？)，没有的话发打招呼信息，推送并且标记未读状态
# ----如果是全球用户，在什么时间发呢？？
# 3、总结对话概要规则
# 对话满一定数量的token就触发总结，总结生成用户事件和更新用户卡,还需要对总结打分

# 亲密度规则有两个：
# 1.在每一次聊天时触发规则判断，每天第一条，条数达到几条等等；
# 2.每天凌晨判断一次，亲密度慢慢递减，延迟队列在早上发消息
# 亲密度大于20的，朋友圈才可见
