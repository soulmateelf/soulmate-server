# -*- coding: utf-8 -*-

# poetry add google-api-python-client google-auth-oauthlib google-auth-httplib2

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build


def googleSub(token):
    # 获取脚本所在目录
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # 构建文件的绝对路径,替换为您的服务账号密钥文件路径
    # SERVICE_ACCOUNT_FILE = os.path.join(script_directory, 'soulmatesg-serverApi.json')
    SERVICE_ACCOUNT_FILE = os.path.join(
        script_directory, 'soulmatesg-google-play-api.json')

    # 替换为您的应用程序包名
    PACKAGE_NAME = 'cn.soulmate.elf'

    # 替换为您的订阅ID
    SUBSCRIPTION_ID = 'month_package'

    # 用服务账号密钥文件创建API客户端
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/androidpublisher'],
    )

    service = build('androidpublisher', 'v3', credentials=credentials)

    # 使用subscriptions.get方法获取订阅信息
    response = service.purchases().subscriptions().get(
        packageName=PACKAGE_NAME,
        subscriptionId=SUBSCRIPTION_ID,
        token=token,
    ).execute()

    # 打印订阅信息
    print(response)
    return response
    # 待补类型逻辑

# 太他妈的离谱了，一直报错401没有权限，最后新增了一个应用内商品，然后删除它，就好了，服了，新增了还不行，必须要删除才行
# 参考链接：https://stackoverflow.com/questions/43536904/google-play-developer-api-the-current-user-has-insufficient-permissions-to-pe
