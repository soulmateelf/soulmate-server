
import os

import firebase_admin
import jwt
from firebase_admin import credentials, messaging
import json

from soulmate_server.conf.systemConf import SALT, headers

# 获取脚本所在目录
script_directory = os.path.dirname(os.path.abspath(__file__))

# 构建文件的绝对路径,替换为您的服务账号密钥文件路径
# SERVICE_ACCOUNT_FILE = os.path.join(script_directory, 'soulmatesg-serverApi.json')
SERVICE_ACCOUNT_FILE = os.path.join(
    script_directory, "soulmate-firebase-admin.json")
# 初始化 Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(cred)


def send(subType, pushId, content, title):
    try:
        print("进入推送")
        if pushId is None:
            print("没有pushId无法推送")
            return

        # 构建消息
        message = messaging.Message(
            data={
                "subType": str(subType)
            },
            notification=messaging.Notification(
                title=title,
                body=content,
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='high_importance_channel',
                    title=title,
                    body=content,
                    visibility='public',
                ),
            ),
            # token='cqI-UCg7wU6on2UXHrjKdY:APA91bFx8x87FHn9BoMe7zPCHLmwV1ZOlGS-VuRpFuHq1askJ9u_8jFPFk4tLBNOAeF08WgXaKyc4lzgv9IbSj5BV46IKIffVuOm7WaPjrbRhSj3_4Q6_01Pvf4mRX6JKDFiDrOBVxJs',  # 这是你要发送消息的设备的 FCM 设备标记
            token=pushId
            # 这是你要发送消息的设备的 FCM 设备标记
        )
        # 发送消息
        print("推送Id" + pushId)
        response = messaging.send(message)
        print(response)
        print('Successfully sent message:', response)
    except Exception as e:
        print("推送失败" + e.__str__())


if __name__ == '__main__':
    # 构建消息
    message = messaging.Message(
        data={
            "subType": str(1)
        },
        notification=messaging.Notification(
            title="123",
            body="123",
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='high_importance_channel',
                title="123",
                body="123",
                visibility='public',
            ),
        ),
        # token='cqI-UCg7wU6on2UXHrjKdY:APA91bFx8x87FHn9BoMe7zPCHLmwV1ZOlGS-VuRpFuHq1askJ9u_8jFPFk4tLBNOAeF08WgXaKyc4lzgv9IbSj5BV46IKIffVuOm7WaPjrbRhSj3_4Q6_01Pvf4mRX6JKDFiDrOBVxJs',  # 这是你要发送消息的设备的 FCM 设备标记
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6Imp3dCJ9.eyJ1c2VySWQiOiI1MWZkNDE0NmFmNDQ0MmVhYmQ5YTAyNDk5NWVmNDRkYSIsImNyZWF0ZVRva2VuVGltZSI6MTcwNTMxMzg5OTE0NH0.tpdnDUuDZ1FuQde7rYppDHZ7BtCG51n8-rG-K9iMFGw"
        # 这是你要发送消息的设备的 FCM 设备标记
    )
    # 发送消息

    response = messaging.send(message)
    print(response)
    print('Successfully sent message:', response)
