import tiktoken

# 使用名字加载 encoding
# 第一次运行时，可能需要连接互联网来下载；下一次不需要联网
encoding = tiktoken.get_encoding("cl100k_base")

# 对于给定的模型名，自动加载正确的 encoding
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# 将文本转化为 tokens 列表
encoding.encode("tiktoken is great!")


# [83, 1609, 5963, 374, 2294, 0]
# 计算 encode 返回列表的长度
def num_tokens_from_messages(messages, num_model:int = 0):
    model = "gpt-4"
    if num_model == 0:
        model = "gpt-3.5-turbo-0301"
    elif num_model == 1:
        model = "gpt-4-0314"
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


if __name__ == '__main__':
    it = []
    it.append({"role": "user", "content": "帮我生成一个一千字的文章"})
    print(num_tokens_from_messages(it))
