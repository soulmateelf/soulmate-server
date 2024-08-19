
import datetime
import json
import uuid

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models import BaseChat, createDynamicTable
from soulmate_server.models.user import User
from sqlalchemy import and_, desc, func, text


# 新增聊天消息
def addChatMessage(mysql, chatRecord):
    mysql.add(chatRecord)
    return True

async def asyncAddChatMessage(mysql, chatRecord):
    mysql.add(chatRecord)
    return True


#
# 查询聊天记录
def getChatMessage(userId, roleId, pageNum, pageSize, sql: mysqlSession = None):
    tablePrefix = 'chat'
    offset = (pageNum - 1) * pageSize
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = sql.query(UserChatClass).filter(UserChatClass.roleId == roleId,
                                               UserChatClass.status == 0).order_by(
        desc(UserChatClass.createTime)).limit(pageSize).offset(offset)

    # 执行查询

    return list(reversed(UserChat.all()))


# 查询总未读聊天记录数
def getChatMessageNoReadCount(userId, sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = sql.query(UserChatClass).filter(
                                               UserChatClass.status == 0,
                                               UserChatClass.readStatus == 0).count()

    # 执行查询

    return UserChat

if __name__ == '__main__':
    UserChatClass = createDynamicTable('51fd4146af4442eabd9a024995ef44da', tablePrefix='chat')
    chatRecord = UserChatClass(chatId=uuid.uuid4().hex, roleId='roleId', content='1', role='role',
                               createTime=123,
                               updateTime=321, inputType=0,
                               tokenSize=214)
    ps = json.dumps(chatRecord.translateString())
    print(ps)
# 查询为总结的聊天记录
def getChatMessageForConclusion(userId, roleId):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = mysqlSession.query(UserChatClass).filter(UserChatClass.roleId == roleId,
                                                        UserChatClass.status == 0,
                                                        UserChatClass.conclusionState == 0).order_by(
        desc(UserChatClass.createTime))

    # 执行查询

    return list(reversed(UserChat.all()))


# 批量通过chatId修改聊天记录为已总结
def updateChatMessageForConclusion(userId, chatIds, sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = sql.query(UserChatClass).filter(UserChatClass.chatId.in_(chatIds)).update(
        {UserChatClass.conclusionState: 1}, synchronize_session=False)

    return True


def getChatMessage10Count(userId, roleId):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = mysqlSession.query(UserChatClass).filter(UserChatClass.roleId == roleId,
                                                        UserChatClass.status == 0).order_by(
        desc(UserChatClass.createTime))

    # 执行查询
    chat_messages = UserChat.limit(10).all()

    return list(reversed(chat_messages))


# 根据token上限查询记录
def getChatMessageByToken(userId, roleId, tokenSumLimit, sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = f'`{tablePrefix}{userId}`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    # 初始化变量 @prev_token
    init_query = text('SELECT @prev_token := 0')
    sql.execute(init_query)

    # 原始SQL查询
    sql_query = text(f'''
        SELECT *
        FROM (
            SELECT 
                id,
                tokenSize,
                roleId,
                role,
                status,
                content,
                @prev_token AS prev_token,
                @prev_token := tokenSize AS current_token
            FROM {tableName} AS subquery
            WHERE subquery.roleId = :roleId
            AND subquery.status = 0
            ORDER BY subquery.createTime DESC
        ) AS t
        WHERE (prev_token + current_token) <= :dynamic_value
          AND t.roleId = :roleId
          AND t.status = 0
    ''')

    # 执行查询
    result_proxy = sql.execute(sql_query, {'dynamic_value': tokenSumLimit, 'roleId': roleId})

    columns = result_proxy.keys()

    # Convert the results to a JSON object
    results = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
    # Return the list of chat messages
    return list(reversed(results))

async def asynGetChatMessageByToken(userId, roleId, tokenSumLimit, sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = f'`{tablePrefix}{userId}`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    # 初始化变量 @prev_token
    init_query = text('SELECT @prev_token := 0')
    sql.execute(init_query)

    # 原始SQL查询
    sql_query = text(f'''
        SELECT *
        FROM (
            SELECT 
                id,
                tokenSize,
                roleId,
                role,
                status,
                content,
                @prev_token AS prev_token,
                @prev_token := tokenSize AS current_token
            FROM {tableName} AS subquery
            WHERE subquery.roleId = :roleId
            AND subquery.status = 0
            ORDER BY subquery.createTime DESC
        ) AS t
        WHERE (prev_token + current_token) <= :dynamic_value
          AND t.roleId = :roleId
          AND t.status = 0
    ''')

    # 执行查询
    result_proxy = sql.execute(sql_query, {'dynamic_value': tokenSumLimit, 'roleId': roleId})

    columns = result_proxy.keys()

    # Convert the results to a JSON object
    results = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
    # Return the list of chat messages
    return list(reversed(results))

def deleteChatMessage(userId, roleId, sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')
    UserChat = sql.query(UserChatClass).filter(UserChatClass.roleId == roleId).update(
        {UserChatClass.status: 1})
    print(UserChat)

    return True


def getTodayMessage(userId, roleId,sql: mysqlSession = None):
    tablePrefix = 'chat'
    # 获取当前日期时间
    now_datetime = datetime.datetime.now()

    # 获取当前日期的零点时间
    today_start_datetime = datetime.datetime.combine(now_datetime.date(), datetime.time())

    # 获取明天日期的零点时间
    tomorrow_start_datetime = today_start_datetime + datetime.timedelta(days=1)

    # 将当前日期时间和明天日期时间转换为 13 位时间戳
    today_timestamp = int(today_start_datetime.timestamp() * 1000)
    tomorrow_timestamp = int(tomorrow_start_datetime.timestamp() * 1000)

    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')

    # 筛选今天的消息
    UserChat = sql.query(UserChatClass).filter(
        UserChatClass.roleId == roleId,
        UserChatClass.status == 0,
        UserChatClass.createTime >= today_timestamp,
        UserChatClass.createTime < tomorrow_timestamp
    ).count()

    return UserChat

async def asyncGetTodayMessage(userId, roleId):
    tablePrefix = 'chat'
    # 获取当前日期时间
    now_datetime = datetime.datetime.now()

    # 获取当前日期的零点时间
    today_start_datetime = datetime.datetime.combine(now_datetime.date(), datetime.time())

    # 获取明天日期的零点时间
    tomorrow_start_datetime = today_start_datetime + datetime.timedelta(days=1)

    # 将当前日期时间和明天日期时间转换为 13 位时间戳
    today_timestamp = int(today_start_datetime.timestamp() * 1000)
    tomorrow_timestamp = int(tomorrow_start_datetime.timestamp() * 1000)

    # 创建动态表
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')

    # 筛选今天的消息
    UserChat = mysqlSession.query(UserChatClass).filter(
        UserChatClass.roleId == roleId,
        UserChatClass.status == 0,
        UserChatClass.createTime >= today_timestamp,
        UserChatClass.createTime < tomorrow_timestamp
    ).count()

    return UserChat
def getYesterdayMessage(userId, roleId,sql:mysqlSession=None):
    tablePrefix = 'chat'

    # 获取昨天的日期和今天的日期
    today_date = datetime.datetime.now().date()
    yesterday_date = today_date - datetime.timedelta(days=1)

    # 创建动态表
    tableName = f'`{tablePrefix}{userId}`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')

    # 筛选昨天的消息数量
    yesterday_messages_count = sql.query(UserChatClass).filter(
        UserChatClass.roleId == roleId,
        UserChatClass.status == 0,
        UserChatClass.createTime >= yesterday_date,
        UserChatClass.createTime < today_date
    ).count()

    return yesterday_messages_count


def getMessagesForDaysAgo(userId, roleId, days_ago, sql:mysqlSession = None):
    tablePrefix = 'chat'

    # 获取今天的日期和前N天的日期
    today_date = datetime.datetime.now().date()
    days_ago_date = today_date - datetime.timedelta(days=days_ago)

    # 创建动态表
    tableName = f'`{tablePrefix}{userId}`'
    UserChatClass = createDynamicTable(userId, tablePrefix='chat')

    # 筛选前N天的消息数量
    messages_count = sql.query(UserChatClass).filter(
        UserChatClass.roleId == roleId,
        UserChatClass.status == 0,
        UserChatClass.createTime >= days_ago_date,
        UserChatClass.createTime < today_date
    ).count()

    return messages_count
