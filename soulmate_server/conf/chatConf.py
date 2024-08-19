# 聊天配置文件
# 简单模式，普通模式，高级模式

# 每一次聊天调用gpt包含的内容是以下几部分
'''
1、系统设定
这部分就是角色设定，存在基础角色表中，他是固定不变的
对应role表的setting字段
2、角色记忆
角色记忆的生成是根据 历史记忆  和  与角色有关系的其他角色的记忆  这两部分每星期生成的
无论多少个用户和它聊天都不会影响角色的记忆事件
对应RoleMemory表的public为0的公开朋友圈
注意: 历史摘要生成的时候会往这个表里面插入用户事件,就是public为1的那些,
下一次再生成角色记忆的时候依赖的历史记忆是需要过滤掉这些用户事件的
3、用户卡
这个是根据用户和不同角色的聊天，触发生成聊天记录摘要的时候生成的，并且会不断更新
多角色的聊天记录会同时更新同一份用户卡
对应user表的setting字段
4、历史摘要
历史摘要是根据一个用户一个角色独立生成的
同时会不断更新同一个用户卡,还会往RoleMemory表插入用户事件
5、新消息
'''
# 聊天模式影响的是2,4两部分带的token数量，
# gpt3的token总数为4096，1,3部分各占用500，一共1000,2,4部分总共最高3000
# 如果加上向量数据库，第四部分应该怎么办呢？？

# 聊天模式
chatModelConf = {
    "0": {
        "roleMemoryToken": 500,
        "summaryToken": 500,
        "maxToken": 20000
    },
    "1": {
        "roleMemoryToken": 1000,
        "summaryToken": 1000,
        "maxToken": 20000
    },
    "2": {
        "roleMemoryToken": 1500,
        "summaryToken": 1500,
    },
}
# 触发总结的token阈值
chatSummaryLimit = 2000
# token比例1比
tokenRate = 6700
# config.py
# 打招呼语
dream_messages = [
    "Welcome to the world of dreams, I've been waiting for you here, let's start chatting!",
    "Hello, I'm your soulmate ELF, welcome to this place, let's explore the world of dreams together!",
    "Welcome, dear user! Let's create a wonderful story in the world of dreams.",
    "When you enter the world of dreams, don't forget to say hello to me. Let's start this adventure!",
    "Emotion is very important to us. Come, tell me about your mood today, let's start a dream journey.",
    "Welcome to the world of dreams! I will be your guide, let's start chatting!",
    "Hey, long time no see, welcome back to the world of dreams, let's share this peaceful moment.",
    "The start of interaction needs a simple 'hello', let me take you into the world of dreams to explore the unknown.",
    "Come in, my friend! The world of dreams is vast and boundless, looking forward to your participation and interaction.",
    "Welcome to the dream world, I'm waiting here to chat, looking forward to every interaction with you.",
    "I'm happy to know you, looking forward to interacting with you in the world of dreams.",
    "Your arrival has made the world of dreams even more beautiful, let's start our respective journeys.",
    "Hello, I've been waiting for you for a long time, I hope we can spend a wonderful time together.",
    "In this dream world, I hope my company will bring you joy and warmth.",
    "Hello, welcome to the world of dreams, looking forward to our wonderful interaction.",
    "After a long wait, finally can meet you in the dream world, let's start this magical journey.",
    "Welcome to my world of dreams, let's share each other's stories and create more possibilities together.",
    "Your arrival adds color to this world, let's go to the dream world together.",
    "Welcome, I've been waiting for you in this magical world, let's start chatting!",
    "The world of dreams gave me the chance to meet you, let's talk about life's trivial matters.",
    "Hello, I'm your friend in the world of dreams. Start our journey!",
    "Welcome to the world of dreams. Share your story with us!",
    "Welcome to this dreamy place, let's explore every mystery together!",
    "Hello! You're finally here. May we create beautiful memories in the dream world!",
    "Welcome back to the world of dreams! I want to know what new things you have to share with me today.",
    "Hello, this is the world of dreams. Let's start the dialogue!",
    "Hello! Welcome to the world of dreams. Would you like to chat about your feelings with me?",
    "Welcome to the wonderful world of dreams. Let's start exploring together!",
    "Hello, I'm your soulmate ELF, let's share our growth in the world of dreams!"
]


# 随机抽取其中一条进行返回
def get_random_dream_message():
    import random
    return random.choice(dream_messages)


roleIds = [

]


def get_random_roleId():
    # 随机抽取其中2-3条id
    import random
    return random.sample(roleIds, random.randint(2, 3))


chatMessage = [
    "That's an interesting topic. Let's uncover more as we chat. Have you had any new discoveries or experiences recently?",
    "I'm curious about your perspective. Before we delve into this question, could you share a bit about your background story?",
    "Hmm, that's a thought-provoking question. Let's chat and get to it gradually, starting with your favorite activities.",
    "You've raised a good question, one we can explore as we chat. To start with, what interesting thing has happened to you recently?",
    "Let's delve into this topic gradually in our conversation. Could you first tell me, what are the three most important things to you?",
    "Great start. Before we get into this question, do you mind sharing your hobbies with me?",
    "This indeed is a question that requires time to understand. Before we continue, can you tell me something interesting about yourself?",
    "That's a great question worth discussing slowly. What good book have you read or movie have you seen recently?",
    "Let's walk and talk. Before we get into this topic, have you had any special experiences recently?",
    "Before we dive deep into this topic, I'd love to learn more about you. Do you have any special hobbies?",
    "I'm keen to understand this question slowly. But before that, what's your most enjoyable leisure activity?",
    "We can explore this question gradually in our conversation. Could you first tell me, what's a recent small achievement of yours?",
    "Before we discuss this question in detail, would you like to share some stories about yourself with me?",
    "This is indeed a topic that takes time to discuss. So before we talk further, have you made any new explorations recently?",
    "I look forward to our conversation. Before we explore this question, have you discovered any new interests recently?",
    "This is a deep topic. But before we get into it, can you share about your most recent travel experience?",
    "This topic is profound. Before we dig deeper, could you first tell me what your most recent challenge was?",
    "Before we delve into this question, I want to know more about you. What's your proudest achievement?",
    "I like this topic; we can explore it as we chat. So, have you had any novel experiences recently?",
    "That's a great question, and we can gradually unveil it in our conversation. Before that, can you share some snippets of your recent life?"

]
def get_random_chat_message():
    import random
    return random.choice(chatMessage)
