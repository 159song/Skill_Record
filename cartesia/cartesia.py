import eng_to_ipa as ipa
import re

# 自定义发音词典
custom_pronunciations = {
    "BBQ": "barbecue",
}


def phrase_to_sonic_ipa(phrase):
    """
    将短语拆分为单词，并逐个转换为符合 Cartesia Sonic 要求的 IPA 格式。
    """
    words = phrase.split()  # 拆分短语为单词
    formatted_words = []
    for word in words:
        ipa_transcription = ipa.convert(word)  # 转换单词为 IPA
        if not ipa_transcription:
            ipa_transcription = word  # 若无法转换，保留原单词
        # 将 IPA 音标中的每个字符用 '|' 分隔，并去除空格
        formatted_ipa = "|".join(ipa_transcription.replace(" ", ""))
        formatted_words.append(f"<<{formatted_ipa}|>>")
    return " ".join(formatted_words)


def word_to_sonic_ipa(word):
    """
    将单词或短语转换为符合 Cartesia Sonic 要求的 IPA 格式。
    """
    # 检查自定义发音词典
    if word.upper() in custom_pronunciations:
        target_phrase = custom_pronunciations[word.upper()]
        return phrase_to_sonic_ipa(target_phrase)  # 处理短语
    else:
        ipa_transcription = ipa.convert(word)  # 默认转换单词
        if not ipa_transcription:
            ipa_transcription = word  # 若无法转换，保留原单词
        formatted_ipa = "|".join(ipa_transcription.replace(" ", ""))
        return f"<<{formatted_ipa}|>>"


def replace_word_with_ipa(text, target_word):
    """
    替换文本中的目标单词为 Sonic IPA 格式。
    """
    # 使用正则表达式，忽略大小写地匹配目标单词
    pattern = re.compile(re.escape(target_word), re.IGNORECASE)
    # 将匹配的单词替换为 Sonic IPA 格式
    return pattern.sub(lambda match: word_to_sonic_ipa(match.group()), text)


def replace_all_custom_words(text):
    """
    替换文本中的所有自定义单词为 Sonic IPA 格式。
    """
    for word in custom_pronunciations.keys():
        text = replace_word_with_ipa(text, word)
    return text


if __name__ == "__main__":
    input_text = "LOL, BBQ is ready ASAP. BTW, AI is the future FYI."
    output_text = replace_all_custom_words(input_text)
    print(output_text)
