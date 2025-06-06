import asyncio
import json
import websockets
import time
import sys
import base64
import hmac
import hashlib
import pyaudio
from datetime import datetime
from urllib.parse import urlencode
import threading

sys.path.append("../..")
from common import credential
from asr import speech_recognizer


class TencentASR:
    # 配置参数

    ENGINE_MODEL_TYPE = "16k_zh"

    # 音频参数
    CHUNK = 6400
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    def __init__(self, use_websocket=True):
        """
        初始化ASR实例
        :param use_websocket: True使用WebSocket方式，False使用SDK方式
        """
        self.use_websocket = use_websocket
        self.ws = None
        self.recognizer = None
        self.is_running = False

    def _create_sdk_recognizer(self):
        """创建SDK方式的识别器"""

        class Listener(speech_recognizer.SpeechRecognitionListener):
            def __init__(self):
                self.parent = None

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
                print("识别完成")

            def on_fail(self, response):
                print(f"识别失败: {response.get('message', '未知错误')}")

        listener = Listener()
        credential_var = credential.Credential(self.SECRET_ID, self.SECRET_KEY)
        recognizer = speech_recognizer.SpeechRecognizer(
            self.APP_ID, credential_var, self.ENGINE_MODEL_TYPE, listener
        )

        # 设置识别参数
        recognizer.set_filter_modal(1)
        recognizer.set_filter_punc(1)
        recognizer.set_filter_dirty(1)
        recognizer.set_need_vad(1)
        recognizer.set_voice_format(1)
        recognizer.set_word_info(1)
        recognizer.set_convert_num_mode(1)

        return recognizer

    def __init__(self):
        self.ws = None
        self.audio_stream = None
        self.is_running = False

    def generate_url(self):
        """生成WebSocket连接URL"""
        # 生成请求参数
        request_param = {
            "secretid": self.SECRET_ID,
            "engine_type": self.ENGINE_MODEL_TYPE,
            "voice_format": 1,  # PCM
            "voice_id": int(time.time()),
            "hotword_id": "",
            "filter_dirty": 1,
            "filter_modal": 1,
            "filter_punc": 1,
            "convert_num_mode": 1,
            "word_info": 1,
            "needvad": 1,
        }

        # 生成签名
        query_string = urlencode(request_param)
        signature_org = f"asr.cloud.tencent.com/asr/v2/?\{query_string}"
        signature = base64.b64encode(
            hmac.new(
                SECRET_KEY.encode("utf-8"), signature_org.encode("utf-8"), hashlib.sha1
            ).digest()
        ).decode("utf-8")

        # 生成完整URL
        url = (
            f"wss://asr.cloud.tencent.com/asr/v2/?\{query_string}&signature={signature}"
        )
        return url

    async def receive_messages(self):
        try:
            while True:
                message = await self.ws.recv()
                response = json.loads(message)

                if response.get("code") == 0:  # 成功的响应
                    if response.get("final") == 1:  # 一句话结束
                        print(f"句子结果: {response.get('result', '')}")
                    else:  # 实时识别结果
                        print(f"实时转写: {response.get('result', '')}")
                elif response.get("code") == 100:  # 识别结束
                    print("识别完成")
                    break
                else:  # 错误情况
                    print(f"发生错误: {response}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        except Exception as e:
            print(f"接收消息时发生错误: {e}")

    async def send_audio_data(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            print("开始录音，按Ctrl+C停止...")
            self.is_running = True

            while self.is_running:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    # 发送音频数据
                    if self.ws and self.is_running:
                        await self.ws.send(data)
                        await asyncio.sleep(0.02)
                except KeyboardInterrupt:
                    break

        except Exception as e:
            print(f"发送音频数据时发生错误: {e}")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()
            # 发送结束标记
            if self.ws:
                await self.ws.send(json.dumps({"type": "end"}))

    async def process_microphone(self):
        url = self.generate_url()
        try:
            async with websockets.connect(url) as ws:
                self.ws = ws
                print("开始识别...")

                # 创建发送和接收任务
                receive_task = asyncio.create_task(self.receive_messages())
                send_task = asyncio.create_task(self.send_audio_data())

                # 等待任务完成
                try:
                    await asyncio.gather(receive_task, send_task)
                except KeyboardInterrupt:
                    print("\n停止录音")
                    self.is_running = False

        except Exception as e:
            print(f"连接发生错误: {e}")
        finally:
            self.is_running = False
            if self.ws:
                await self.ws.close()


def main():
    asr = TencentASRWebSocket()
    try:
        asyncio.run(asr.process_microphone())
    except KeyboardInterrupt:
        print("\n程序已停止")


if __name__ == "__main__":
    main()
