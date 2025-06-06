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

    def _generate_websocket_url(self):
        """生成WebSocket连接URL"""
        request_param = {
            "secretid": self.SECRET_ID,
            "engine_type": self.ENGINE_MODEL_TYPE,
            "voice_format": 1,
            "voice_id": int(time.time()),
            "hotword_id": "",
            "filter_dirty": 1,
            "filter_modal": 1,
            "filter_punc": 1,
            "convert_num_mode": 1,
            "word_info": 1,
            "needvad": 1,
        }

        query_string = urlencode(request_param)
        signature_org = f"asr.cloud.tencent.com/asr/v2/?\{query_string}"
        signature = base64.b64encode(
            hmac.new(
                self.SECRET_KEY.encode("utf-8"),
                signature_org.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        return (
            f"wss://asr.cloud.tencent.com/asr/v2/?\{query_string}&signature={signature}"
        )

    async def _receive_websocket_messages(self):
        """接收WebSocket消息"""
        try:
            while True:
                message = await self.ws.recv()
                response = json.loads(message)

                if response.get("code") == 0:
                    if response.get("final") == 1:
                        print(f"句子结果: {response.get('result', '')}")
                    else:
                        print(f"实时转写: {response.get('result', '')}")
                elif response.get("code") == 100:
                    print("识别完成")
                    break
                else:
                    print(f"发生错误: {response}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        except Exception as e:
            print(f"接收消息时发生错误: {e}")

    async def process_audio_websocket(self):
        """使用WebSocket方式处理音频"""
        url = self._generate_websocket_url()
        try:
            async with websockets.connect(url) as ws:
                self.ws = ws
                print("开始识别...")

                # 创建音频捕获和处理任务
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK,
                )

                print("开始录音，按Ctrl+C停止...")
                self.is_running = True

                # 创建接收消息的任务
                receive_task = asyncio.create_task(self._receive_websocket_messages())

                try:
                    while self.is_running:
                        data = stream.read(self.CHUNK, exception_on_overflow=False)
                        await self.ws.send(data)
                        await asyncio.sleep(0.02)
                except KeyboardInterrupt:
                    print("\n停止录音")
                except Exception as e:
                    print(f"发送音频数据时发生错误: {e}")
                finally:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    await self.ws.send(json.dumps({"type": "end"}))
                    await receive_task

        except Exception as e:
            print(f"连接发生错误: {e}")
        finally:
            self.is_running = False

    def process_audio_sdk(self):
        """使用SDK方式处理音频"""
        self.recognizer = self._create_sdk_recognizer()

        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        print("开始录音，按Ctrl+C停止...")
        try:
            self.recognizer.start()
            self.is_running = True
            while self.is_running:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.recognizer.write(data)
                time.sleep(0.02)
        except KeyboardInterrupt:
            print("\n停止录音")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            if self.recognizer:
                self.recognizer.stop()

    def start(self):
        """开始音频处理"""
        try:
            if self.use_websocket:
                asyncio.run(self.process_audio_websocket())
            else:
                self.process_audio_sdk()
        except KeyboardInterrupt:
            print("\n程序已停止")
        finally:
            self.is_running = False


def main():
    # 使用WebSocket方式
    asr_ws = TencentASR(use_websocket=True)
    asr_ws.start()

    # 使用SDK方式
    # asr_sdk = TencentASR(use_websocket=False)
    # asr_sdk.start()


if __name__ == "__main__":
    main()
