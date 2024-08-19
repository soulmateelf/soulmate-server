import hashlib
import datetime


async def isNotEmpty1(value):
    if value != None and value != '':
        return True
    return False

def isNotEmpty(value):
    if value != None and value != '':
        return True
    return False
def md5Util(value: str = '', salt: str = 'soulmate'):
    if isNotEmpty(value) == False:
        return ''
    # md5对象获取加密结果
    md5 = hashlib.md5((value + salt).encode('utf-8')).hexdigest()
    return md5
