import time
import sys
import threading
from datetime import datetime
import json
import pyaudio
import os
from dotenv import load_dotenv

sys.path.append("../..")
from common import credential
from asr import speech_recognizer

load_dotenv(override=True)

ENGINE_MODEL_TYPE = "16k_zh"
SLICE_SIZE = 6400
CHUNK = 6400  # 每次读取的音频大小
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率16k


class MySpeechRecognitionListener(speech_recognizer.SpeechRecognitionListener):
    def __init__(self, id):
        self.id = id

    def on_recognition_start(self, response):
        print("开始识别...")

    def on_sentence_begin(self, response):
        print("检测到新的语音输入...")

    def on_recognition_result_change(self, response):
        if response.get("result"):
            print(f"实时转写: {response['result']['voice_text_str']}")

    def on_sentence_end(self, response):
        if response.get("result"):
            print(f"句子结果: {response['result']['voice_text_str']}")

    def on_recognition_complete(self, response):
        print(
            "%s|%s|OnRecognitionComplete\n"
            % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response["voice_id"])
        )

    def on_fail(self, response):
        rsp_str = json.dumps(response, ensure_ascii=False)
        print(
            "%s|%s|OnFail,message %s\n"
            % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                response["voice_id"],
                rsp_str,
            )
        )


# def process(id):
#     audio = "test.wav"
#     listener = MySpeechRecognitionListener(id)
#     credential_var = credential.Credential(SECRET_ID, SECRET_KEY)
#     recognizer = speech_recognizer.SpeechRecognizer(
#         APP_ID, credential_var, ENGINE_MODEL_TYPE, listener
#     )
#     recognizer.set_filter_modal(1)
#     recognizer.set_filter_punc(1)
#     recognizer.set_filter_dirty(1)
#     recognizer.set_need_vad(1)
#     # recognizer.set_vad_silence_time(600)
#     recognizer.set_voice_format(1)
#     recognizer.set_word_info(1)
#     # recognizer.set_nonce("12345678")
#     recognizer.set_convert_num_mode(1)
#     try:
#         recognizer.start()
#         with open(audio, "rb") as f:
#             content = f.read(SLICE_SIZE)
#             while content:
#                 recognizer.write(content)
#                 content = f.read(SLICE_SIZE)
#                 # sleep模拟实际实时语音发送间隔
#                 time.sleep(0.02)
#     except Exception as e:
#         print(e)
#     finally:
#         recognizer.stop()


# def process_multithread(number):
#     thread_list = []
#     for i in range(0, number):
#         thread = threading.Thread(target=process, args=(i,))
#         thread_list.append(thread)
#         thread.start()

#     for thread in thread_list:
#         thread.join()


def process_microphone(id):
    listener = MySpeechRecognitionListener(id)
    credential_var = credential.Credential(
        os.getenv("SECRET_ID"), os.getenv("SECRET_KEY")
    )
    recognizer = speech_recognizer.SpeechRecognizer(
        os.getenv("APP_ID"), credential_var, ENGINE_MODEL_TYPE, listener
    )
    recognizer.set_filter_modal(1)
    recognizer.set_filter_punc(1)
    recognizer.set_filter_dirty(1)
    recognizer.set_need_vad(1)
    recognizer.set_voice_format(1)
    recognizer.set_word_info(1)
    recognizer.set_convert_num_mode(1)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    recognizer = speech_recognizer.SpeechRecognizer(
        os.getenv("APP_ID"),
        credential_var,
        ENGINE_MODEL_TYPE,
        listener,
    )
    try:
        recognizer.start()
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            recognizer.write(data)
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\n停止录音")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        recognizer.stop()


if __name__ == "__main__":
    process_microphone(0)  # 使用麦克风进行识别
