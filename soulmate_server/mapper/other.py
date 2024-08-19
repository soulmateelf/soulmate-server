# 添加定制信息
from soulmate_server.common.mysql_tool import mysqlSession


def insertCustomization(customization, sql: mysqlSession = None):
    sql.add(customization)


# 分享成功后添加记录
def insertShareLog(shareLog, sql: mysqlSession = None):

    sql.add(shareLog)
