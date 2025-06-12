import re

text = "Hello, world! one! two? three. nine; zero: test?"

# 需要排除的单词列表
skip_words = {
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
}


def replacer(match):
    # match.group(1) 是符号前的单词
    # match.group(2) 是符号
    word = match.group(1)
    symbol = match.group(2)
    if word.lower() in skip_words:
        return f"{word}{symbol}"
    else:
        return f'{word}{symbol}<break time="1s"/>'


# 匹配：单词 + 符号
pattern = re.compile(r"(\w+)([^\w\s])")
result = pattern.sub(replacer, text)

print(result)
