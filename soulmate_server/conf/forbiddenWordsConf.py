
import openpyxl
import pandas as pd

from soulmate_server.common.mysql_tool import mysqlSession
from soulmate_server.models.role import RoleMemory

forbiddenWords = [
    "机器学习", "Machine Learning",
    "人工智能", "Artificial Intelligence",
    "神经网络", "Neural Network",
    "深度学习", "Deep Learning",
    "自然语言处理", "Natural Language Processing",
    "聊天机器人", "Chatbot",
    "知识库", "Knowledge Base",
    "智能助手", "Intelligent Assistant",
    "算法", "Algorithm",
    "自动回复", "Auto-Response",
    "语言模型", "Language Model",
    "GPT（生成式预训练变换器）", "GPT (Generative Pre-trained Transformer)",
    "数据集", "Dataset",
    "计算能力", "Computational Power",
    "文本生成", "Text Generation",
    "交互式对话", "Interactive Conversation",
    "问答系统", "Question-Answering System",
    "智能响应", "Intelligent Response",
    "机器人学习", "Robot Learning",
    "用户体验", "User Experience",
    "虚拟助手", "Virtual Assistant",
    "openAI"
]
returnMessage = ['Now that I think about it, whats your favorite type of cuisine?',
                 'Ive been wondering, have you been to any interesting events lately?',
                 'You know, it just crossed my mind, do you enjoy any outdoor activities?',
                 'I was just contemplating, whats your opinion on current fashion trends?',
                 'Hmm, have you watched any documentaries recently that you found fascinating?',
                 'Just a thought, but how do you feel about art and museums?',
                 'Im curious, what are your thoughts on the latest environmental initiatives?',
                 'Reflecting on it, do you have a favorite holiday destination?',
                 'Im pondering, whats your stance on recent technological advancements?',
                 'Just mulling over, do you enjoy gardening or any form of plant care?',
                 'Let me think, have you tried any new restaurants or cafes lately?',
                 'I was just considering, do you have any pets?',
                 'Thinking about it, what are your hobbies or pastimes?',
                 'Out of curiosity, what kind of movies or genres do you prefer?',
                 'Ive been musing, how do you usually celebrate special occasions?',
                 'I was just reflecting, do you follow any particular sports teams?',
                 'On a different note, have you ever thought about learning a new language?',
                 'Changing gears, what��s your favorite season of the year?',
                 'Im pondering, do you enjoy any specific types of podcasts or radio shows?',
                 'Just a thought, but have you been involved in any community service or volunteering?',
                 'Im thinking, whats the most interesting place youve ever visited?',
                 'On that subject, do you have a favorite book or author?',
                 'Ive been contemplating, do you have any fitness goals or routines?',
                 'You know, it strikes me to ask, what��s your dream job?',
                 'Changing topics, do you have any recommendations for TV shows worth binge-watching?',
                 'Just wondering, what are your thoughts on recent advancements in science?',
                 'Let me see, do you have a favorite coffee or tea blend?',
                 'Reflecting on it, what was the last concert or live performance you attended?',
                 'Im curious, do you have a favorite childhood memory?',
                 'Thinking out loud, have you explored any new parts of the city or town recently?',
                 'Let me think... Do you have any upcoming travel plans?',
                 'Hmm, what kind of music do you usually enjoy?',
                 'I was wondering... Have you picked up any new hobbies recently?',
                 'You know, it just occurred to me to ask, whats your take on the latest tech gadgets?',
                 'Just curious, have you read any good books lately?',
                 'Im thinking... How do you usually spend your weekends?', 'Actually, are you into any sports?',
                 'I was just pondering, how do you relax in your free time?',
                 'Im trying to recall, do you follow any TV shows or web series?',
                 'I was just reflecting, have you seen any good movies recently?',
                 'Now that I think about it, whats your take on the latest health and wellness trends?',
                 'Ive been wondering, do you have any favorite historical figures or eras?',
                 'You know, it just crossed my mind, how do you like to spend a rainy day?',
                 'I was just contemplating, have you been to any art exhibitions or galleries recently?',
                 'Hmm, are there any new skills or hobbies youd like to learn?',
                 'Just a thought, but what kind of comedies or humorous shows do you enjoy?',
                 'Im curious, have you participated in any local festivals or cultural events?',
                 'Reflecting on it, do you have a favorite type of international cuisine?',
                 'Im pondering, how do you stay informed about current events or news?',
                 'Just mulling over, do you prefer the beach or the mountains?',
                 'Let me think, have you seen any innovative theater or dance performances lately?',
                 'I was just considering, do you enjoy crafting or DIY projects?',
                 'Thinking about it, do you have a favorite podcast or radio program?',
                 'Out of curiosity, whats your favorite way to unwind after a busy week?',
                 'Ive been musing, have you been on any road trips or adventures recently?',
                 'I was just reflecting, whats your favorite childhood TV show or cartoon?',
                 'On a different note, do you have any go-to comfort foods?',
                 'Changing gears, whats your opinion on renewable energy and sustainability?',
                 'Im pondering, have you ever tried meditation or yoga?',
                 'Just a thought, but have you ever been involved in any team sports or group activities?',
                 'Im thinking, whats the most interesting documentary youve watched?',
                 'On that subject, do you have a favorite artist or band?',
                 'Ive been contemplating, do you enjoy cooking or baking?',
                 'You know, it strikes me to ask, what��s your opinion on space exploration?',
                 'Changing topics, have you recently discovered any interesting apps or websites?',
                 'Just wondering, whats your favorite holiday and how do you celebrate it?',
                 'Let me see, do you enjoy hiking or nature walks?',
                 'Reflecting on it, have you ever tried any unusual foods?',
                 'Im curious, do you have any favorite board games or card games?',
                 'Thinking out loud, have you explored any new hobbies during the pandemic?',
                 'You know, I was just thinking, have you ever been interested in photography?',
                 'Ive been wondering, do you have any favorite classic movies or directors?',
                 'Now that it comes to mind, do you follow any particular fashion trends or designers?',
                 'Just pondering, have you ever considered writing a book or a blog?',
                 'Out of curiosity, do you have any favorite science fiction or fantasy novels?',
                 'Thinking about it, whats the most memorable concert or live event youve attended?',
                 'Im curious, do you have a favorite historical period or event that fascinates you?',
                 'Reflecting on it, have you ever tried any extreme sports or adventurous activities?',
                 'I was just considering, do you have a favorite artist or type of art?',
                 'Changing the topic, how do you feel about the current trends in education?',
                 'Im wondering, do you have any pets, or do you prefer certain animals?',
                 'You know, it strikes me, have you ever been involved in any artistic or creative projects?',
                 'Just a thought, but how do you usually celebrate your birthday or special occasions?',
                 'Let me think, have you ever been to a themed park or a major exhibition?',
                 'Hmm, do you have a favorite local spot or hidden gem in your city?',
                 'Thinking out loud, have you ever tried learning a musical instrument?',
                 'On a different note, whats your opinion on the latest developments in artificial intelligence?',
                 'Changing gears, do you have any favorite traditional dishes from your culture?',
                 'Ive been contemplating, do you enjoy watching or playing any particular sports?',
                 'Now that I think about it, have you ever participated in a charity event or fundraiser?',
                 'You know, I just remembered, do you have a favorite season or time of year?',
                 'Im curious, whats your take on the latest fashion or lifestyle trends?',
                 'Reflecting on it, have you ever had a particularly memorable travel experience?',
                 'I was just wondering, do you enjoy any water sports or activities?',
                 'Just considering, do you have any plans for the upcoming holidays?',
                 'Out of curiosity, have you ever tried any unusual hobbies or activities?',
                 'You know, it occurs to me, do you have a favorite type of theater or performance art?',
                 'Changing the subject, whats your stance on environmental conservation?',
                 'Ive been pondering, do you enjoy any particular types of video games or computer games?',
                 'Let me think, have you ever been interested in any form of martial arts or self-defense?']


def get_random_forbidden_message():
    import random
    return random.choice(returnMessage)


if __name__ == '__main__':
    sql = mysqlSession
    roles = sql.query(RoleMemory).all()
    for it in roles :
        it.image = it.image.replace('54.177.205.15', 'neveraloneagain.app')
    sql.commit()
    # # 指定Excel文件路径
    # excel_file_path = 'E:/wechat缓存/WeChat Files/wxid_0gfp9ecq5k8122/FileStorage/File/2024-01/主动打招呼.xlsx'
    # # 打开 Excel 文件
    # workbook = openpyxl.load_workbook(excel_file_path)
    #
    # # 获取第一个工作表
    # sheet = workbook.active
    #
    # # 用于存储第一列数据的字符串数组
    # data_array = []
    #
    # # 遍历每一行并获取第一列数据
    # for row in sheet.iter_rows(min_row=1, max_col=1, values_only=True):
    #     cell_value = row[0]
    #
    #     # 将数据添加到数组中
    #     data_array.append(str(cell_value).replace("'", "").replace('"', ""))
    #
    # # 关闭 Excel 文件
    # workbook.close()
    # print(data_array)
