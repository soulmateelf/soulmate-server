import uuid


def createUUid():
    return str(uuid.uuid4()).replace('-', '')


if __name__ == '__main__':
    print(uuid.uuid4().hex)