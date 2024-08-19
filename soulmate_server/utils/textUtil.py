import re


def find_prohibited_words(text, prohibited_words):
    found_words = []
    for word in prohibited_words:
        pattern = re.compile(fr'\b{re.escape(word)}\b', flags=re.IGNORECASE)
        match = pattern.search(text)
        if match:
            found_words.append(match.group())
    return found_words
