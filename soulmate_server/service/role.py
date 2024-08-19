# 定制角色逻辑
import time
import uuid

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.mapper.other import insertCustomization
from soulmate_server.mapper.user import queryUserInfoById
from soulmate_server.models.other import Customization
from soulmate_server.utils.emailUtils import sendRoleEmail


def user_customization(userId, age, orderId, gender, name, head_image, hobby, characterIntroduction, remark):
    sql = mysqlSession
    try:

        userInfo = queryUserInfoById(userId,sql=sql)
        insertCustomization(Customization(
            userId=userId,
            orderId=orderId,
            name=name,
            age=age,
            gender=gender,
            avatar=head_image,
            hobby=hobby,
            description=characterIntroduction,
            message=remark,
            createTime=int(time.time() * 1000),
            customId=uuid.uuid4().hex

        ), sql=sql)
        # 发送邮箱
        param = {'roleName': name, 'age': age
            , 'gender': gender, 'roleCharacter': hobby, 'roleIntroduction': characterIntroduction, 'replenish': remark
            , 'email': userInfo.email, 'userId': userId, 'url': head_image}
        sendRoleEmail(email='sunsun@soulmate.health', Subject='customizationRole', params=param)
        sql.commit()
        sql.expire_all()
    except Exception as e:
        sql.rollback()
        print(e)
