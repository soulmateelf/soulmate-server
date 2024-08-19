# 示例定时任务
import datetime
import json
import re
import traceback
import uuid

import requests

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.conf.systemConf import file_path, fileSrc
from soulmate_server.conf.taskConf import createFriends, get_random_Nochat_message
from soulmate_server.mapper.chat import getYesterdayMessage, getMessagesForDaysAgo, addChatMessage
from soulmate_server.mapper.message import addMessageByType
from soulmate_server.mapper.role import selectUserByRoleMemoryCount3, getAllRole, selectUserByRoleMemoryCount1, \
    selectUserRoleByRoleId, addRoleMemoryNotify
from soulmate_server.mapper.user import queryUserRole, addIntimacyDetails, reduceIntimacy, queryUserInfoById
from soulmate_server.models import createDynamicTable
from soulmate_server.models.other import Message, BackgroundImage
from soulmate_server.models.role import RoleRelationship, RoleMemory, RoleMemoryCreateLog, Role, RoleMemoryNotify
from soulmate_server.models.user import IntimacyLog, DailyTaskDetails, UserRoleImage
from soulmate_server.utils.ChatGptTokenUtil import num_tokens_from_messages
from soulmate_server.utils.chat import chatgptNoAsync, process_string, init_api
from soulmate_server.utils.mp3 import ensure_directory_exists


def my_job():
    print("定时任务执行了")


# 每日晚执行亲密度减少逻辑
def intimacy_job():
    print("进行每日亲密度减少逻辑")

    sql = mysqlSession
    try:
        # 获取所有的用户角色
        userRoleList = queryUserRole(sql)
        for userRole in userRoleList:
            # 获取用户角色的亲密度
            intimacy = userRole.intimacy
            # 亲密度大于0时，每日减少1点亲密度
            if intimacy > 0:
                if userRole.intimacy >= 50:
                    yesterday_messages_count = getYesterdayMessage(userRole.userId, userRole.roleId,sql = sql)
                    if yesterday_messages_count == 0:
                        reduceIntimacy(userRole.userId, userRole.roleId, 1, sql=sql)
                        addIntimacyDetails(IntimacyLog(
                            intimacyLogId=uuid.uuid4().hex,
                            userId=userRole.userId,
                            roleId=userRole.roleId,
                            intimacy=2,
                            type=1,
                            triggerType=0,
                            createTime=int(datetime.datetime.now().timestamp() * 1000),
                            triggerDetails=DailyTaskDetails.TODAYNOTTALK50.value
                        ), sql=sql)
                        addMessageByType(userId=userRole.userId, roleId=userRole.roleId,
                                         messageType=DailyTaskDetails.TODAYNOTTALK50.value, sql=sql)
                if userRole.intimacy < 50:
                    messages_count = getMessagesForDaysAgo(userRole.userId, userRole.roleId, 2,sql=sql)
                    if messages_count == 0:
                        reduceIntimacy(userRole.userId, userRole.roleId, 1, sql=sql)
                        addIntimacyDetails(IntimacyLog(
                            intimacyLogId=uuid.uuid4().hex,
                            userId=userRole.userId,
                            roleId=userRole.roleId,
                            intimacy=2,
                            type=1,
                            triggerType=0,
                            createTime=int(datetime.datetime.now().timestamp() * 1000),
                            triggerDetails=DailyTaskDetails.NOTTALK50DOWN.value
                        ), sql=sql)
                        addMessageByType(userId=userRole.userId, roleId=userRole.roleId,
                                         messageType=DailyTaskDetails.NOTTALK50DOWN.value, sql=sql)
                # 是否没有发消息主动打招呼
                if userRole.intimacy >= 80:
                    userInfo = queryUserInfoById(userId=userRole.userId, sql=sql)
                    # 模拟触发招呼次数
                    trigger_count = 1
                    # 需要查询的天数
                    days_ago = 2
                    for i in range(trigger_count):
                        days_ago = days_ago * 2
                    messages_count = getMessagesForDaysAgo(userRole.userId, userRole.roleId, days_ago,sql=sql)
                    if messages_count == 0:
                        message = get_random_Nochat_message()
                        message = message.replace('[Friends Name]', userInfo.nickName)
                        # 发送招呼语
                        UserChatClass = createDynamicTable(userRole.userId, tablePrefix='chat')
                        chatRecord = UserChatClass(chatId=uuid.uuid4().hex, roleId=userRole.roleId, content=message,
                                                   role="assistant",
                                                   createTime=int(datetime.datetime.now().timestamp() * 1000),
                                                   inputType=0,
                                                   readStatus=0,
                                                   tokenSize=0)
                        addChatMessage(mysql=sql, chatRecord=chatRecord)
        sql.commit()
    except Exception as e:
        print(e)
        sql.rollback()
    # 待定


# 每天处理订阅订单
def subscription_job():
    # 查询所有订阅关系
    num = 1


# 生成朋友圈任务（事件）
def createCircleOfFriends():
    print("进入每日生成朋友圈")
    sql = mysqlSession
    chat_message = ''
    try:
        roles = getAllRole()
        if roles is not None and len(roles) > 0:
            for role in roles:
                # 当前角色历史事件3条
                count3 = selectUserByRoleMemoryCount3(role.roleId)
                # 获取身边人的历史事件1条
                ships = sql.query(RoleRelationship).filter(RoleRelationship.roleIdMain == role.roleId).all()
                # 用户事件待补
                chatSystem = role.setting
                history = ''
                ship_history = ''
                if count3 is not None and len(count3) > 0:
                    for count in count3:
                        # 拼接角色历史事件 3条带换行
                        history += count.content + '\n'

                if ships is not None and len(ships) > 0:
                    for ship in ships:
                        # 查询身边的最近一条历史事件
                        shipHistory = selectUserByRoleMemoryCount1(ship.roleId)
                        if shipHistory is not None and len(shipHistory) > 0:
                            ship_history += shipHistory[0].content + '\n'
                # 拼接设定
                system = chatSystem + "\n" + '##Historical events:' + "\n" + history + "\n" + '##Historical events of people around you:' + "\n" \
                         + ship_history + '\n' + createFriends

                chat_result = chatgptNoAsync([{'role': 'system', 'content': system}], 1)
                chat_message = chat_result.get('response').choices[0].message.content if chat_result.get(
                    'status') == True else "There's been a mistake"
                process_string(chat_message)
                data = json.loads(chat_message)
                memoryId = uuid.uuid4().hex
                image_system = role.gptDescription + "\n" + data.get('roleEvents')
                chat_image_result = init_api(image_system)
                # 获得图片地址 下载保存
                url = download_image(chat_image_result)
                # 生成朋友圈事件
                sql.add(RoleMemory(
                    memoryId=memoryId,
                    roleId=role.roleId,
                    content=data.get('roleEvents'),
                    createTime=int(datetime.datetime.now().timestamp() * 1000),
                    publishTime=int(data.get('Time')),
                    explanation=data.get('explain'),
                    experience=data.get('experience'),
                    image=url,
                    status=0
                ))

                # 需要添加朋友圈未读消息的用户们
                users = selectUserRoleByRoleId(roleId=role.roleId, sql=sql)
                if users is not None and len(users) > 0:
                    for userRole in users:
                        addRoleMemoryNotify(RoleMemoryNotify(
                            notifyId=uuid.uuid4().hex,
                            userId=userRole.userId,
                            roleId=role.roleId,
                            createTime=int(datetime.datetime.now().timestamp() * 1000),
                            status=0,
                            memoryId=memoryId,
                            publishTime=int(data.get('Time'))
                        ), sql=sql)
        sql.add(RoleMemoryCreateLog(
            createLogId=uuid.uuid4().hex,
            createTime=int(datetime.datetime.now().timestamp() * 1000),
            result='success'
        ))
        sql.commit()
    except Exception as e:
        sql.rollback()
        # traceback.print_exc()
        print(e)
        sql.add(RoleMemoryCreateLog(
            createLogId=uuid.uuid4().hex,
            createTime=int(datetime.datetime.now().timestamp() * 1000),
            result=e,
            gptResult=chat_message
        ))
        sql.commit()


def download_image(url):
    try:
        name = uuid.uuid4().hex
        file_name = file_path + '/' + 'CircleOfFriends' + '/' + name + ".png"
        ensure_directory_exists(file_path + '/' + 'CircleOfFriends' + '/')
        # 发送GET请求获取图片数据
        response = requests.get(url)
        # 检查响应状态码是否为200，表示请求成功
        if response.status_code == 200:
            # 以二进制模式写入图片数据到本地文件
            with open(file_name, 'wb') as file:
                file.write(response.content)
                print(f"图片已成功下载到 {file_name}")
            return fileSrc + 'CircleOfFriends' + '/' + name + ".png"
        else:
            print("无法下载图片")
    except Exception as e:
        print(f"发生异常: {str(e)}")


def generate_next_week(date_str):
    # 解析输入的日期字符串
    start_date_str, end_date_str = date_str.split('-')
    start_date = datetime.datetime.strptime(start_date_str, '%Y.%m.%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y.%m.%d')

    # 计算下一周的起始日期和结束日期
    next_start_date = end_date + datetime.timedelta(days=1)
    next_end_date = next_start_date + datetime.timedelta(days=6)

    # 格式化日期字符串
    next_week_str = f"{next_start_date.strftime('%Y.%m.%d')}-{next_end_date.strftime('%Y.%m.%d')}"

    return next_week_str


def extract_dynamic_data(input_text, key):
    # 构建动态的正则表达式模式
    dynamic_pattern = re.escape(key) + r':\s*(.*?)\n'

    # 提取数据
    match = re.search(dynamic_pattern, input_text)
    if match:
        return match.group(1)
    else:
        return None


# 确定苹果订阅是否取消订阅
def apple_is_cancel_subscription(id, sql: mysqlSession = None):
    # 接口地址
    url = 'https://api.storekit.itunes.apple.com/inApps/v1/subscriptions/' + str(id)
    # 发送GET请求获取图片数据
    response = requests.get(url)
    # 检查响应状态码是否为200，表示请求成功
    if response.status_code == 200:
        print(response.content)
        print(response.text)


if __name__ == '__main__':
    apple_is_cancel_subscription(1703144773000)
    # createCircleOfFriends()
    # sql = mysqlSession
    # roles = sql.query(Role).all()
    # for i in range(17):
    #     imageId = uuid.uuid4().hex
    #     sql.add(BackgroundImage(
    #         imageUrl="http://54.177.205.15/api/static/" + '0' + str(i + 1) + ".png",
    #         imageId=imageId,
    #         createTime=int(datetime.datetime.now().timestamp() * 1000)
    #     ))
    #     for role in roles:
    #         sql.add(UserRoleImage(roleImageId=uuid.uuid4().hex, roleId=role.roleId, imageId=imageId,
    #                               createTime=int(datetime.datetime.now().timestamp() * 1000)))
    # sql.commit()
