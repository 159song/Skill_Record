import os
import hashlib
import json
from list_voice import get_group_voice
import concurrent.futures
import requests


def generate_tts(voice_id, text, language):
    # Text to Speech (Bytes) (POST /tts/bytes)
    response = requests.post(
        "https://api.cartesia.ai/tts/bytes",
        headers={
            "X-API-Key": "",
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json",
        },
        json={
            "model_id": "sonic-2",
            "transcript": text,
            "voice": {"mode": "id", "id": voice_id},
            "output_format": {
                "container": "wav",
                "sample_rate": 24000,
                "encoding": "pcm_s16le",
            },
            "language": language,
        },
    )

    return response.json()


def is_same_language(code1, code2):
    # 取语言代码的前缀部分
    prefix1 = code1.split("-")[0]
    prefix2 = code2.split("-")[0]
    return prefix1 == prefix2


language_text_file = {
    "en": "en-US.txt",
    "es": "es-ES.txt",
    "ko": "ko-KR.txt",
    "zh": "zh-CN.txt",
    "fi": "en-US.txt",
}


def get_text_hash(text):
    return hashlib.md5(text.encode()).hexdigest()


def save_wav(voice_id, text, output_dir, language):
    text_hash = get_text_hash(text)
    wav_filename = f"{text_hash}.txt"
    wav_filepath = os.path.join(output_dir, voice_id, wav_filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(wav_filepath), exist_ok=True)

    wav_data = generate_tts(voice_id, text, language)
    with open(wav_filepath, "wb") as wav_file:
        wav_file.write(wav_data)

    print(f"WAV file saved: {wav_filepath}")


def process_file(name, texts_path, voices, output_dir):
    file_path = os.path.join(texts_path, name)

    # 读取文本文件
    with open(file_path, "r") as file_text:
        texts = file_text.readlines()
    language = name.split(".")[0]

    for voice_group, voice_list in voices.items():
        for voice in voice_list:
            if is_same_language(voice["language"], language):
                for text in texts:
                    text = text.strip()  # 去除行末的换行符
                    if text:  # 确保文本不为空
                        save_wav(voice["id"], text, output_dir, voice["language"])


def main():
    texts_path = "./voice_text"
    if not os.path.exists(texts_path):
        os.makedirs(texts_path)
    output_dir = "./voices"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_names = os.listdir(texts_path)
    voices = get_group_voice()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_file, name, texts_path, voices, output_dir)
            for name in file_names
        ]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
