# ��ѯ��ǰ�û����п�����ҳ
from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import Coupon


def select_coupon_by_user_id(user_id, pageNum, pageSize, sql: mysqlSession = None):
    # ��ѯȫ����ɫid
    result = sql.query(Coupon).filter(Coupon.userId == user_id, Coupon.status == 0).offset(
        (pageNum - 1) * pageSize).limit(pageSize).all()
    return result
