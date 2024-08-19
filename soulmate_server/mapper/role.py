# 角色数据查询类
import datetime
import time
import uuid

from sqlalchemy import text, or_, desc

from sqlalchemy.orm import joinedload

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.role import Role, RoleMemory, RoleMemoryNotify
from soulmate_server.models.user import UserRole, User


def selectRoleByUser(userId, pageNum, pageSize, sql: mysqlSession = None):
    now = int(datetime.datetime.now().timestamp() * 1000)

    # Step 2: Join the results with the role table
    query = text(
        "SELECT a.roleId, a.name, a.age, a.gender, a.avatar, a.hobby, a.description, a.setting, a.origin, a.remark, a.userId AS roleUser,b.imageId, b.intimacy,IFNULL(c.readCount,0) as readCount "
        "FROM role a "
        "LEFT JOIN userRole b ON b.roleId = a.roleId AND b.userId = :user_id and b.status=0 "
        "LEFT JOIN (SELECT userId, roleId, count(notifyId) as readCount FROM roleMemoryNotify WHERE status = 0 AND readStatus = 0 AND publishTime <= :now GROUP BY userId, roleId) c ON c.userId = :user_id AND c.roleId = b.roleId "
        "WHERE a.status = 0 AND (a.userId=:user_id OR a.userId IS NULL)"
        "ORDER BY b.intimacy DESC"
    )

    # Execute the query
    user_results = sql.execute(query, {"user_id": userId, "now": now})

    # Get the results as a list of dictionaries
    columns = user_results.keys()
    results = [dict(zip(columns, row)) for row in user_results.fetchall()]

    return results


def selectRoleDetails(roleId, userId, sql: mysqlSession = None):
    query = text(
        "SELECT c.imageId,c.imageUrl as backgroundImageUrl,a.roleId, a.name,a.voice, a.age, a.gender, a.avatar, a.hobby, a.description, a.setting, a.origin, a.remark, a.userId AS roleUser, b.intimacy "
        "FROM role a "
        "LEFT JOIN userRole b ON b.roleId = a.roleId AND b.userId = :user_id and b.status=0 "
        "LEFT JOIN backgroundImage c on c.imageId = b.imageId "
        "WHERE a.roleId = :role_id"
    )

    user_results = sql.execute(query, {"user_id": userId, "role_id": roleId})

    columns = user_results.keys()

    # 获取第一行并将其转换为字典
    result_dict = dict(zip(columns, user_results.first()))
    return result_dict


async def asyncSelectRoleDetails(roleId, userId, sql: mysqlSession = None):
    query = text(
        "SELECT c.imageId,c.imageUrl as backgroundImageUrl,a.roleId, a.name,a.voice, a.age, a.gender, a.avatar, a.hobby, a.description, a.setting, a.origin, a.remark, a.userId AS roleUser, b.intimacy "
        "FROM role a "
        "LEFT JOIN userRole b ON b.roleId = a.roleId AND b.userId = :user_id "
        "LEFT JOIN backgroundImage c on c.imageId = b.imageId "
        "WHERE a.roleId = :role_id"
    )

    user_results = sql.execute(query, {"user_id": userId, "role_id": roleId})

    columns = user_results.keys()

    # 获取第一行并将其转换为字典
    result_dict = dict(zip(columns, user_results.first()))
    return result_dict


def selectUserRoleBy(userId, pageNum, pageSize, sql: mysqlSession = None):
    # 计算偏移量
    offset = (pageNum - 1) * pageSize
    tablePrefix = 'chat'
    tableName = '`' + f'{tablePrefix}{userId}' + '`'
    existsTableName = f'{tablePrefix}{userId}'
    # 使用带占位符的SQL查询
    # 检查表是否存在
    table_c_exists = check_table_exists(existsTableName, sql=sql)
    table_d_exists = check_table_exists(existsTableName, sql=sql)
    now = int(datetime.datetime.now().timestamp() * 1000)

    if table_c_exists and table_d_exists:
        query = text(
            "SELECT a.roleId,IFNULL(e.readCount,0) as readCount ,b.imageId,c.voiceSize,c.inputType, a.name, a.age, a.gender, a.avatar, a.hobby, a.description, a.setting, a.origin, a.remark, a.userId AS roleUser, b.intimacy, c.content,Ifnull(f.countSize,0) as countSize,c.createTime as endSendTime "
            "FROM userRole b "
            "LEFT JOIN role a ON b.roleId = a.roleId "
            f"LEFT JOIN (SELECT roleId, MAX(createTime) AS max_date FROM {tableName} GROUP BY roleId) d ON b.roleId = d.roleId "
            f"LEFT JOIN {tableName} c ON b.roleId = c.roleId AND c.createTime = d.max_date and c.status =0 "
            f"LEFT JOIN (SELECT roleId,count(id) as countSize FROM {tableName} where readStatus = 0 GROUP BY roleId ) f ON b.roleId = f.roleId "
            "LEFT JOIN (SELECT userId, roleId, count(notifyId) as readCount FROM roleMemoryNotify WHERE status = 0 AND readStatus = 0 AND publishTime <= :now GROUP BY userId, roleId) e ON e.userId = :user_id AND e.roleId = b.roleId "
            "WHERE b.userId = :user_id and b.status = 0 and c.content is not null "
            "ORDER BY endSendTime DESC "
            # "LIMIT :page_size OFFSET :offset"
        )
    else:
        return None
        # query = text(
        #     "SELECT a.roleId,IFNULL(c.readCount,0) as readCount , b.imageId,a.name, a.age, a.gender, a.avatar, a.hobby, a.description, a.setting, a.origin, a.remark, a.userId AS roleUser, b.intimacy,b.createTime, NULL AS content,0 AS countSize, null as endSendTime "
        #     "FROM userRole b "
        #     "LEFT JOIN role a ON b.roleId = a.roleId "
        #     "LEFT JOIN (SELECT userId, roleId, count(notifyId) as readCount FROM roleMemoryNotify WHERE status = 0 AND readStatus = 0 AND publishTime <= :now GROUP BY userId, roleId) c ON c.userId = :user_id AND c.roleId = b.roleId "
        #     "WHERE b.userId = :user_id and b.status = 0 "
        #     "ORDER BY createTime DESC "
        #     # "LIMIT :page_size OFFSET :offset"
        # )

    # 执行查询时传入参数
    user_results = sql.execute(query, {"user_id": userId, "page_size": pageSize, 'now': now})

    # 获取列名
    columns = user_results.keys()

    # Convert the results to a JSON object
    results = [dict(zip(columns, row)) for row in user_results.fetchall()]

    return results


def check_table_exists(table_name, sql: mysqlSession = None):
    # 查询是否存在指定表
    query = text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table_name")
    result = sql.execute(query, {"table_name": table_name})
    return result.scalar() > 0


# 查出所有系统角色 排除定制角色：
def getSystemRole():
    # 查询全部角色id
    result = mysqlSession.query(Role).filter(Role.userId == None, Role.status == 0).all()

    return result


def getAllRole():
    # 查询全部角色id
    result = mysqlSession.query(Role).filter(Role.status == 0).all()

    return result


def addUserRole(sql, userRole):
    oldUserRole = sql.query(UserRole).filter(UserRole.userId == userRole.userId,
                                             UserRole.roleId == userRole.roleId,
                                             UserRole.status == 0).first()
    if oldUserRole is not None:
        return False
    else:
        sql.add(userRole)
    return True


def deleteUserRoleByUser(userId, roleId, sql: mysqlSession = None):
    sql.query(UserRole).filter(UserRole.userId == userId, UserRole.roleId == roleId).update(
        {UserRole.status: 1})
    return True


def selectUserByRoleMemory(userId, roleId, pageNum, pageSize, sql: mysqlSession = None):
    try:
        # userRole = selectRoleDetails(roleId=roleId, userId=userId, sql=sql)
        # intimacy = userRole.get('intimacy')
        # result = None

        # if intimacy is None:
        #     intimacy = 0
        #
        # if int(intimacy) >= 20:
        offset = (pageNum - 1) * pageSize
        limit = pageSize

        result = (
            sql.query(RoleMemory)
            .options(joinedload(RoleMemory.activities))
            .filter(RoleMemory.roleId == roleId, RoleMemory.status == 0,
                    or_(
                        RoleMemory.publishTime <= int(datetime.datetime.now().timestamp() * 1000),
                        RoleMemory.publishTime == None
                    ), or_(
                    RoleMemory.userId == userId,
                    RoleMemory.userId == None
                )
                    )
            .order_by(desc(RoleMemory.publishTime))
            .offset(offset)
            .limit(limit)
            .all()
        )

        for it in result:
            sql.query(RoleMemoryNotify).filter(RoleMemoryNotify.roleId == roleId,
                                               RoleMemoryNotify.userId == userId).update(
                {"readStatus": 1})

        sql.commit()

        return result
    except Exception as e:
        print(e)
        sql.rollback()
        return None


def selectUserByRoleMemoryLimit3(userId, roleId, sql: mysqlSession = None):
    try:
        # userRole = selectRoleDetails(roleId=roleId, userId=userId, sql=sql)
        # intimacy = userRole.get('intimacy')
        # result = None

        # if intimacy is None:
        #     intimacy = 0
        #
        # if int(intimacy) >= 20:
        offset = 0 * 3

        result = (
            sql.query(RoleMemory)
            .options(joinedload(RoleMemory.activities))
            .filter(RoleMemory.roleId == roleId, RoleMemory.status == 0,
                    or_(
                        RoleMemory.publishTime <= int(datetime.datetime.now().timestamp() * 1000),
                        RoleMemory.publishTime == None
                    ), or_(
                    RoleMemory.userId == userId,
                    RoleMemory.userId == None
                )
                    )
            .order_by(desc(RoleMemory.publishTime))
            .offset(offset)
            .limit(3)
            .all()
        )

        return result
    except Exception as e:
        print(e)
        return None


def selectUserByIdMemory(memoryId, sql: mysqlSession = None):
    try:
        # 使用原始 SQL 查询
        sql_query = """
        SELECT a.id, a.memoryId, a.roleId, a.content, a.image, a.startTime, a.endTime, a.publishTime, a.public, a.userId,
        a.gptLogId, a.explanation, a.experience, a.status, a.remark, a.createTime, a.updateTime,b.memoryId as b_memoryId
        , b.activityId, b.type , b.content as b_content , b.avatar, b.nickName,b.createTime as b_createTime ,b.userId as b_userId, b.remark as b_remark
        ,b.updateTime as b_updateTime
        ,b.status as b_status,b.id as b_id,b.status as b_status
        FROM roleMemory a
        	LEFT JOIN (SELECT	c.createTime,c.memoryId,c.activityId,c.type,c.content,c.id,c.userId,c.status,c.remark,c.updateTime,	d.avatar,d.nickName FROM	roleMemoryActivity c LEFT JOIN user d ON c.userId = d.userId ) b ON b.memoryId = a.memoryId
        WHERE a.memoryId = :memory_id AND a.status = 0
        """

        # 执行查询
        # 获取查询结果，并设置返回的结果集为 KeyedTuple
        result_set = sql.execute(text(sql_query), {'memory_id': memoryId}).fetchall()

        # 处理结果集，将其组织成字典
        memory_data = {}

        for row in result_set:
            row_dict = dict(row._asdict())
            memory_id = row_dict['id']  # 假设 id 是 RoleMemory 表的 ID
            if memory_id not in memory_data:
                memory_data[memory_id] = {
                    'id': row_dict['id'],
                    'memoryId': row_dict['memoryId'],
                    'roleId': row_dict['roleId'],
                    'content': row_dict['content'],
                    'image': row_dict['image'],
                    'startTime': row_dict['startTime'],
                    'endTime': row_dict['endTime'],
                    'publishTime': row_dict['publishTime'],
                    'public': row_dict['public'],
                    'userId': row_dict['userId'],
                    'gptLogId': row_dict['gptLogId'],
                    'explanation': row_dict['explanation'],
                    'experience': row_dict['experience'],
                    'status': row_dict['status'],
                    'remark': row_dict['remark'],
                    'createTime': row_dict['createTime'],
                    'updateTime': row_dict['updateTime'],
                    'activities': []
                }

            activity_dict = {
                'memoryId': row_dict['b_memoryId'] if row_dict['b_memoryId'] is not None else None,
                'activityId': row_dict['activityId'] if row_dict['activityId'] is not None else None,
                'type': row_dict['type'] if row_dict['type'] is not None else None,
                'content': row_dict['b_content'] if row_dict['b_content'] is not None else None,
                'avatar': row_dict['avatar'] if row_dict['avatar'] is not None else None,
                'userName': row_dict['nickName'] if row_dict['nickName'] is not None else None,
                'createTime': row_dict['b_createTime'] if row_dict['b_createTime'] is not None else None,
                'id': row_dict['b_id'] if row_dict['b_id'] is not None else None,
                'userId': row_dict['b_userId'] if row_dict['b_userId'] is not None else None,
                'remark': row_dict['b_remark'] if row_dict['b_remark'] is not None else None,
                'updateTime': row_dict['b_updateTime'] if row_dict['b_updateTime'] is not None else None,
                'status': row_dict['b_status'] if row_dict['b_status'] is not None else None,
            }
            if activity_dict['memoryId'] is not None:
                memory_data[memory_id]['activities'].append(activity_dict)

        return list(memory_data.values())[0]

    except Exception as e:
        print(f"发生错误：{e}")
        if sql:
            sql.rollback()
        return None


def selectUserByRoleMemoryCount3(roleId):
    result = (
        mysqlSession.query(RoleMemory)
        .filter(RoleMemory.roleId == roleId)
        .filter(RoleMemory.createTime <= int(
            datetime.datetime.now().timestamp() * 1000))  # Assuming timestamp is stored as a numeric value
        .order_by(desc(RoleMemory.createTime))
        .limit(3)
        .all()
    )
    return result


def selectUserByRoleMemoryCount1(roleId):
    result = (
        mysqlSession.query(RoleMemory)
        .filter(RoleMemory.roleId == roleId)
        .filter(RoleMemory.createTime <= int(
            datetime.datetime.now().timestamp() * 1000))  # Assuming timestamp is stored as a numeric value
        .order_by(desc(RoleMemory.createTime))
        .limit(1)
        .all()
    )
    return result


# 修改userRole中的背景图片地址
def updateUserRoleImage(userId, roleId, imagesId, sql: mysqlSession = None):
    userRole = sql.query(UserRole).filter(UserRole.userId == userId, UserRole.roleId == roleId,
                                          UserRole.status == 0).first()
    if userRole is None:
        sql.add(UserRole(userRoleId=uuid.uuid4().hex, userId=userId, roleId=roleId, imageId=imagesId,
                         createTime=int(time.time() * 1000)))
    else:
        userRole.imageId = imagesId

    # newImagesId = uuid.uuid4().hex
    # if userRole is None:
    #     imagesId = userRole.get('imageId')
    #     if imagesId is None:
    #
    #         back = BackgroundImage(
    #             imageId=newImagesId,
    #             imageUrl=url,
    #             createTime=int(time.time() * 1000)
    #         )
    #         mysqlSession.add(back)
    #     else:
    #         mysqlSession.query(BackgroundImage).filter(BackgroundImage.imageId == imagesId).update(
    #             {BackgroundImage.status: 1})
    #         back = BackgroundImage(
    #             imageId=newImagesId,
    #             imageUrl=url,
    #             createTime=int(time.time() * 1000)
    #         )
    #         mysqlSession.add(back)
    #     mysqlSession.query(UserRole).filter(UserRole.userId == userId, UserRole.roleId == roleId).update(
    #         {UserRole.imageId: newImagesId})

    return True


# 根据角色查询所有背景图片
def selectRoleBackgroundImage(roleId):
    query = text(
        "SELECT a.imageId, a.imageUrl "
        "FROM backgroundImage a "
        "LEFT JOIN userRoleImage b ON b.imageId = a.imageId "
        "WHERE b.roleId = :role_id and a.status = 0 and b.status = 0 "
    )

    user_results = mysqlSession.execute(query, {"role_id": roleId})

    columns = user_results.keys()

    # Convert the results to a JSON object
    results = [dict(zip(columns, row)) for row in user_results.fetchall()]

    return results


# 添加朋友圈的评论
def addRoleMemoryActivity(roleMemoryActivity, sql: mysqlSession = None):
    sql.add(roleMemoryActivity)

    return True


# 添加朋友圈的未读消息
def addRoleMemoryNotify(roleMemoryNotify, sql: mysqlSession = None):
    sql.add(roleMemoryNotify)

    return True


# 根据roleId 查询亲密度大于20的userRole
def selectUserRoleByRoleId(roleId, sql: mysqlSession = None):
    try:
        result = (
            sql.query(UserRole)
            .filter(UserRole.status == 0, UserRole.roleId == roleId, UserRole.intimacy >= 20)
            .all()
        )
        return result
    except Exception as e:
        print(e)
        sql.rollback()
        return None


def selectRoleByRoleId(roleId, sql: mysqlSession = None):
    return sql.query(Role).filter(Role.roleId == roleId, Role.status == 0).first()
