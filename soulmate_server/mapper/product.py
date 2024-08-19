# ��ѯ���в�Ʒ�ӷ�ҳ
import base64
import json

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.energy import Product


def select_product_page(page, size, productType, sql: mysqlSession = None):
    return sql.query(Product).filter(Product.status == 0, Product.type.in_(productType)).order_by(
        Product.createTime.desc()).offset(
        (page - 1) * size).limit(size).all()


def select_product_by_id(productId, sql: mysqlSession = None):
    return sql.query(Product).filter(Product.productId == productId, Product.status == 0).first()


if __name__ == '__main__':
    s = base64.b64decode(
        "eyJ2ZXJzaW9uIjoiMS4wIiwicGFja2FnZU5hbWUiOiJjbi5zb3VsbWF0ZS5lbGYiLCJldmVudFRpbWVNaWxsaXMiOiIxNzAzOTI0OTA1OTk5Iiwic3Vic2NyaXB0aW9uTm90aWZpY2F0aW9uIjp7InZlcnNpb24iOiIxLjAiLCJub3RpZmljYXRpb25UeXBlIjozLCJwdXJjaGFzZVRva2VuIjoiZW5saGVtYWdhYW1nZm9qbGFta2xraW1jLkFPLUoxT3puSW1hNTQtNVkwM0dhNTlfMklSUTJpbWo4X3JkWF9UWE4zOWxBeG5rYUhaYmRXUFpjQ3QzTk1Ecmt0alpyNWtDZ01wZHNTQ25UekdSMnl0N3l0WjJGRndWVjB3Iiwic3Vic2NyaXB0aW9uSWQiOiJtb250aF9wYWNrYWdlIn19")
    # 将解码后的数据转换为字符串
    decoded_string = s.decode("utf-8")
    # 将字符串转换为字典
    decoded_json = json.loads(decoded_string)
    print(decoded_string)