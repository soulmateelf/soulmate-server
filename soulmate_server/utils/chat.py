'''
Author: kele
Date: 2023-03-10 09:55:08
LastEditors: kele
LastEditTime: 2024-08-16 18:06:37
Description: chatgpt
'''
import json
import re
from io import BytesIO

import openai
import requests

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.conf.taskConf import chatPrompt
from soulmate_server.models.role import RoleMemory
from soulmate_server.utils.ChatGptTokenUtil import num_tokens_from_messages

openai.api_key = '***'


def chatgpt(messageList=[], model: int = 0):
    # 公司key
    gptMode = None
    if model == 0:
        gptMode = 'gpt-3.5-turbo-1106'
    elif model == 1:
        gptMode = 'gpt-4-1106-preview'
    # messageList = [{"role": "user", "content": "先假设你是一只叫做jack的猫"}]
    response = None
    error = None
    try:

        response = openai.ChatCompletion.create(
            model=gptMode,
            messages=messageList,
            request_timeout=200,  # timeout参数暂时无效，request_timeout单次请求超时时间，单位秒，会重试3次
        )
    except Exception as e:
        error = e
        response = None

    result = {'status': True if error == None else False,
              'response': response, 'error': error}

    return result


def chatgptNoAsync(messageList=[], model: int = 0):
    # 公司key
    gptMode = None
    if model == 0:
        gptMode = 'gpt-3.5-turbo-1106'
    elif model == 1:
        gptMode = 'gpt-4-1106-preview'
    # messageList = [{"role": "user", "content": "先假设你是一只叫做jack的猫"}]
    response = None
    error = None
    try:
        response = openai.ChatCompletion.create(
            model=gptMode,
            messages=messageList,
            request_timeout=200,  # timeout参数暂时无效，request_timeout单次请求超时时间，单位秒，会重试3次
        )
    except Exception as e:
        error = e
        response = None

    result = {'status': True if error == None else False,
              'response': response, 'error': error}

    return result


# 生成图片
def init_api(txt):
    response = openai.Image.create(
        prompt=txt,
        model="dall-e-3",
        size="1024x1024",
        response_format="url"
    )
    image_url = response['data'][0]['url']
    return image_url


# 语音转文字
def to_txt(file_path):
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    # 判断文字是否是utf 编码
    try:
        if transcript.text.encode('utf-8').isalpha():
            return transcript.text
        else:
            return ""
    except:
        return ""


def get_embedding(textList, model="text-embedding-ada-002"):
    return openai.Embedding.create(input=textList, model=model)


def updateUse1r(user_card_str, api_response):
    for key, value in api_response.items():
        key = re.escape(key)
        value = re.escape(str(value)) if value is not None else ''
        pattern = re.compile(fr'({key}):(.*?)(?=\w+:|$)', re.IGNORECASE)
        user_card_str = re.sub(pattern, f'{key}: {value}', user_card_str)

    return user_card_str


def updateUser(user_card_str, api_response):
    for key, value in api_response.items():
        key = re.escape(key)
        value = re.escape(str(value)) if value is not None else ''
        pattern = re.compile(
            fr'({key}):\s*(.*?)(?=\w+:|$)', re.IGNORECASE | re.DOTALL)
        user_card_str = re.sub(
            pattern, f'{key}: {value}\n', user_card_str, count=1)

    return user_card_str


def process_string(input_str):
    # 判断字符串是否以"```json"开头并以"结尾```"结尾
    if input_str.startswith("```json") and input_str.endswith("```"):
        # 剃除字符串
        result_str = input_str[len("```json"): -len("```")]
        return result_str
    else:
        # 如果不满足条件，返回原始字符串
        return input_str


# 删除字符中的%号
def del_percent(input_str):
    if '%' in input_str:
        return input_str.replace('%', '')
    else:
        return input_str


if __name__ == '__main__':

    # 循环3000遍
    messageList = [{"role": "user", "content": "我是一只猫"}]
    for i in range(3000):
        messageList.append({"role": "user", "content": "我是一只猫"})
    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messageList,
        temperature=0.7,
    )

    print(re)
    # sql =mysqlSession
    # for it  in sql.query(RoleMemory).all():
    #     try:
    #         response = requests.head(it.image)
    #         if response.status_code == 404:
    #             it.status=1
    #             print("Image not found (404)")
    #         else:
    #             print("Image found!")
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error checking image URL: {e}")
    # sql.commit()

    # updateUser(
    #     '#User Card\nName:\nAge:\nGender:\nNationality/Ethnicity:\nReligious Beliefs:Birthday:Hobbies:Occupation:Communication Style:Cultural Background:Political Affiliation:Knowledge Level (0-100%):Religious Affiliation:',
    #     {'Name': 'dsa', "Age": 123, "Nationality/Ethnicity": "sad"})
    # # result = chatgpt([{"role": "user", "content": "我是一只猫"}], 1)
    # # num = num_tokens_from_messages([{"role": "user", "content": "我是一只猫"}])
    # # print(num)
    # userCrad = "User Card\n" \
    #            "Name:\n" \
    #            "Age:\n" \
    #            "Gender:\n" \
    #            "Nationality/Ethnicity:\n" \
    #            "Religious Beliefs:\n" \
    #            "Birthday:\n" \
    #            "Hobbies:\n" \
    #            "Occupation:\n" \
    #            "Communication Style:\n" \
    #            "Cultural Background:\n" \
    #            "Political Affiliation:\n" \
    #            "Knowledge Level (0-100%):\n" \
    #            "Religious Affiliation:\n"
    # roleCard = "#Character Card" \
    #            "Name: Wheaty" \
    #            "Age: 72" \
    #            "Gender: Male" \
    #            "Nationality/Ethnicity: Dreamland/Plantfolk" \
    #            "Birthday: December 25, 1950" \
    #            "Hobbies: Reading, planting, flying kites, camping" \
    #            "Occupation: Planter" \
    #            "Goal: Aims to nurture the younger generation of field guardians and pass down agricultural wisdom." \
    #            "Significance: As the embodiment of bountiful harvests, Wheaty hopes to cultivate the next generation of field guardians, passing on agricultural wisdom, securing future agricultural abundance, and meeting people's food needs." \
    #            "Social Relationships: Corny (Friend - Level 8), Golden (Family - Level 10), Cotton (Friend - Level 9)" \
    #            "Big Five Personality Model:" \
    #            "--Openness: 75%" \
    #            "--Conscientiousness: 85%" \
    #            "--Extraversion: 78%" \
    #            "--Agreeableness: 90%" \
    #            "--Neuroticism: 15%" \
    #            "Expression Style: Calm, humble, friendly, profound"
    #
    # chatHistroy = "dialogue：assistant：Hi there! Nice to chat with you！\n" \
    #               "user：Hi, nice to meet you too!\n" \
    #               "assistant：I'm a big fan of art. Do you like art?\n" \
    #               "user：Yes, I like art too\n" \
    #               "assistant：Wow, great! What do you usually like to draw? What's your style?\n" \
    #               "user：I like to draw landscapes, and my style is realistic\n" \
    #
    # cont = userCrad + '\n' + roleCard + '\n+' + chatHistroy + '\n' + chatPrompt
    # # 初始化需要总结摘要的消息list
    # ConclusionList = [{'role': 'system', 'content': cont          }]
    #
    # result = chatgpt(messageList=ConclusionList, model=1).get('response').choices[0].message.content
    #
    # re = process_string(result)
    # ke = json.loads(re)
    #
    # s = updateUser(userCrad, ke.get('UserCard'))
    # print(s)
    # print(ke)
