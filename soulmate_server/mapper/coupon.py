# 查询当前用户所有卡卷并分页
from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import Coupon


def select_coupon_by_user_id(user_id, pageNum, pageSize, sql: mysqlSession = None):
    # 查询全部角色id
    result = sql.query(Coupon).filter(Coupon.userId == user_id, Coupon.status == 0).offset(
        (pageNum - 1) * pageSize).limit(pageSize).all()
    return result
