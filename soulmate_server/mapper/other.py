# ��Ӷ�����Ϣ
from soulmate_server.common.mysql_tool import mysqlSession


def insertCustomization(customization, sql: mysqlSession = None):
    sql.add(customization)


# ����ɹ�����Ӽ�¼
def insertShareLog(shareLog, sql: mysqlSession = None):

    sql.add(shareLog)
