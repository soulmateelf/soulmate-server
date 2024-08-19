# 分享成功后处理逻辑
import time
import uuid

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import Coupon
from soulmate_server.models.other import ShareLog


def share_success(userId, shareLog, sql: mysqlSession = None):
    # 给用户新增一个双倍卡券
    log = sql.query(ShareLog).filter(ShareLog.userId == userId).first()
    sql.add(shareLog)
    if log is None:
        sql.add(Coupon(couponId=uuid.uuid4().hex,
                       userId=userId,
                       ratio=2,
                       origin=0,
                       title="Share to get",
                       expiredTime=int(time.time() * 1000) + 7 * 24 * 60 * 60 * 1000,
                       createTime=int(time.time() * 1000),
                       updateTime=int(time.time() * 1000)
                       ))

        return "Share successful! Your reward has been sent to your gift backpack, please check it!"
    return "Share successful! Thank you for your support."
