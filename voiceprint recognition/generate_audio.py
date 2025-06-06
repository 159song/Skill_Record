import requests
import os
from itertools import product
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("CARTESIA_API_KEY")


def text_to_speech_with_cartesia(
    text_list, voice_list, output_dir="data", language: str = "en"
):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 新的 Cartesia API 的基本 URL
    api_url = "https://api.cartesia.ai/tts/bytes"

    # 生成文本和语音的笛卡尔积
    for index, (text, voice) in enumerate(product(text_list, voice_list)):
        if voice["language"] == language:
            # 设置请求头和数据
            headers = {
                "X-API-Key": api_key,
                "Cartesia-Version": "2024-12-12",
                "Content-Type": "application/json",
            }
            data = {
                "model_id": "sonic",
                "transcript": text,
                "voice": {"mode": "id", "id": voice["id"]},
                "output_format": {
                    "container": "wav",
                    "sample_rate": 16000,
                    "encoding": "pcm_s16le",
                },
                "language": language,
            }

            # 发送请求到 Cartesia API
            response = requests.post(api_url, headers=headers, json=data)

            if response.status_code == 200:
                # 创建以语音ID命名的文件夹
                voice_folder = os.path.join(output_dir, voice["id"])
                if not os.path.exists(voice_folder):
                    os.makedirs(voice_folder)

                # 保存音频文件到相应的文件夹，使用文本索引命名
                wav_filename = os.path.join(voice_folder, f"{index}.wav")
                counter = 1
                while os.path.exists(wav_filename):
                    wav_filename = os.path.join(voice_folder, f"{index}_{counter}.wav")
                    counter += 1
                with open(wav_filename, "wb") as f:
                    f.write(response.content)
                print(f"Generated {wav_filename}")
            else:
                print(
                    f"Failed to generate audio for {text} with voice {voice}. Status code: {response.status_code}"
                )


def get_cartesia_voices():
    # Cartesia API 的语音列表 URL
    voices_url = "https://api.cartesia.ai/voices"

    # 设置请求头
    headers = {"Cartesia-Version": "2024-06-10", "X-API-Key": api_key}

    # 发送请求到 Cartesia API
    response = requests.get(voices_url, headers=headers)

    if response.status_code == 200:
        voices_data = response.json()
        # 假设返回的数据是一个包含 voice_id 的列表
        return voices_data
    else:
        print(f"Failed to retrieve voices. Status code: {response.status_code}")
        return []


# 获取所有的 voice_id
voice_ids = get_cartesia_voices()


texts = [
    "Could I see the menu, please?",
    "What are today's specials?",
    "I would like to order the grilled chicken, please.",
    "Can I have the pasta with tomato sauce?",
    "What do you recommend?",
    "Is there a dish you suggest?",
    "Does this dish contain nuts?",
    "Is the soup gluten-free?",
    "Can I get a glass of water, please?",
    "I'd like a cup of coffee.",
    "Could we have the bill, please?",
    "Can I pay by card?",
]

text_to_speech_with_cartesia(texts, voice_ids)
