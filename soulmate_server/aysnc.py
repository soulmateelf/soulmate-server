import asyncio
import datetime
import json
import time
import traceback

import jwt

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.common.redis_tool import redis_set, redis_getList
from soulmate_server.conf.chatConf import chatModelConf
from soulmate_server.conf.taskConf import chatPrompt
from soulmate_server.mapper.role import selectRoleDetails
from soulmate_server.models import createDynamicTable
from soulmate_server.models.other import MessageObject
from soulmate_server.models.role import RoleMemory
from soulmate_server.models.user import UserRole
from soulmate_server.service.chat import intimacyService, asyncToken
from soulmate_server.utils.chat import chatgpt
from soulmate_server.utils.mqtt import mqttCo


# 写一个fast同步并发任务
async def async_function():
    print("Start async_function")
    # 休眠2秒
    await asyncio.sleep(2)
    return "shuai"


async def process_background_task():
    # sql = mysqlSession
    # try:
    #     start_time = time.time()
    # 模拟耗时的后台任务
    time.sleep(200)


#     # 记录结束时间
#     mq = mqttCo
#     me = MessageObject(clear=False, content=json.dumps("{key:dsa}"), messageType=2)
#     me_dict = me.to_dict()
#     js = json.dumps(me_dict)
#     mq.publish(topic=userId, message=str(js))
#     end_time = time.time()
#     UserChatClass = createDynamicTable("sda", tablePrefix='chat')
#     # 计算耗时
#     elapsed_time = end_time - start_time
#     p = sql.query(UserRole).all()
#     selectRoleDetails("sda", "dsa", sql=sql)
#     print(p)
#     # result = chatgpt([{"role": "user", "content": "我是一只猫"}], 1)
#     # num = num_tokens_from_messages([{"role": "user", "content": "我是一只猫"}])
#     # print(num)
#     userCrad = "User Card\n" \
#                "Name:\n" \
#                "Age:\n" \
#                "Gender:\n" \
#                "Nationality/Ethnicity:\n" \
#                "Religious Beliefs:\n" \
#                "Birthday:\n" \
#                "Hobbies:\n" \
#                "Occupation:\n" \
#                "Communication Style:\n" \
#                "Cultural Background:\n" \
#                "Political Affiliation:\n" \
#                "Knowledge Level (0-100%):\n" \
#                "Religious Affiliation:\n"
#     roleCard = "#Character Card" \
#                "Name: Wheaty" \
#                "Age: 72" \
#                "Gender: Male" \
#                "Nationality/Ethnicity: Dreamland/Plantfolk" \
#                "Birthday: December 25, 1950" \
#                "Hobbies: Reading, planting, flying kites, camping" \
#                "Occupation: Planter" \
#                "Goal: Aims to nurture the younger generation of field guardians and pass down agricultural wisdom." \
#                "Significance: As the embodiment of bountiful harvests, Wheaty hopes to cultivate the next generation of field guardians, passing on agricultural wisdom, securing future agricultural abundance, and meeting people's food needs." \
#                "Social Relationships: Corny (Friend - Level 8), Golden (Family - Level 10), Cotton (Friend - Level 9)" \
#                "Big Five Personality Model:" \
#                "--Openness: 75%" \
#                "--Conscientiousness: 85%" \
#                "--Extraversion: 78%" \
#                "--Agreeableness: 90%" \
#                "--Neuroticism: 15%" \
#                "Expression Style: Calm, humble, friendly, profound"
#
#     chatHistroy = "dialogue：assistant：Hi there! Nice to chat with you！\n" \
#                   "user：Hi, nice to meet you too!\n" \
#                   "assistant：I'm a big fan of art. Do you like art?\n" \
#                   "user：Yes, I like art too\n" \
#                   "assistant：Wow, great! What do you usually like to draw? What's your style?\n" \
#                   "user：I like to draw landscapes, and my style is realistic\n" \
#
#     cont = userCrad + '\n' + roleCard + '\n+' + chatHistroy + '\n' + chatPrompt
#     # 初始化需要总结摘要的消息list
#     ConclusionList = [{'role': 'system', 'content': cont}]
#     # 进入回调先上锁 避免多次调用 此锁非同步锁 而是每个线程一个锁
#     redis_set('LOCK:' + userId + 1 + str(2), 1)
#     messageList = redis_getList("s")
#     result = chatgpt(messageList=ConclusionList, model=1).get('response').choices[0].message.content
#     asyncio.create_task(intimacyService(userId, "123"))
#     asyncio.create_task(asyncToken(result.get('response').get('usage').get('total_tokens'), "123", userId,
#                                    chatModelConf.get(str(1)).get('maxToken')))
#
#     print(f"Background task completed: 1")
# except Exception as e:
#     traceback.print_exc()
#     sql.rollback()


# 构造header
headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}

# 密钥
SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='


# 创建token
def create_token(username, password, userId):
    if password is None:
        password = ''
    # 构造payload
    payload = {
        'username': username,
        'password': password,  # 自定义用户ID
        'userId': userId,
        'createTokenTime': int(datetime.datetime.now().timestamp() * 1000)
    }
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)

    return result


# 解析token
# def get_userId(token):
#     try:
#         payload = jwt.decode(token, SALT, algorithms=["HS256"], headers=headers)
#         userId: str = payload.get("userId")
#         if userId is None:
#             return "0"
#     except Exception as e:
#         return "0"
#     return userId



    sql = mysqlSession
    for it in sql.query(RoleMemory).all():
        it.image = it.image.replace("http", "https")
    sql.commit()
