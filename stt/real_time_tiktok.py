import asyncio
import datetime
import gzip
import json
import uuid
import websockets
import pyaudio
from loguru import logger


class RealTimeTiktokASR:
    def __init__(self, **kwargs):
        # 音频参数设置
        self.chunk = 512  # 每次读取的音频数据块大小
        self.format = pyaudio.paInt16  # 音频格式
        self.channels = 1  # 单声道
        self.rate = 8000  # 采样率

        # WebSocket参数设置
        self.ws_url = kwargs.get(
            "ws_url", "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel"
        )
        self.uid = kwargs.get("uid", "test")

        # 初始化PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.ws = None
        self.is_running = False

        self.last_text = ""  # 添加上一次识别结果的缓存

    async def init_websocket(self):
        """初始化WebSocket连接并发送初始请求"""
        reqid = str(uuid.uuid4())
        request_params = {
            "user": {
                "uid": self.uid,
            },
            "audio": {
                "format": "pcm",
                "sample_rate": self.rate,
                "bits": 16,
                "channel": self.channels,
                "codec": "raw",
            },
            "request": {
                "model_name": "bigmodel",
                "enable_punc": True,
            },
        }

        header = {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Access-Key": "DDFAiCUS0XZ5qUzBEsmC4lvihyIKcO10",
            "X-Api-App-Key": "4227051015",
            "X-Api-Request-Id": reqid,
        }

        # 压缩并准备初始请求数据
        payload_bytes = gzip.compress(str.encode(json.dumps(request_params)))

        # 构造请求头部
        full_client_request = bytearray(
            [
                0x11,  # 版本号和头部大小
                0x11,  # 消息类型和标志
                0x11,  # 序列化方法和压缩方式
                0x00,  # 保留字段
            ]
        )

        # 添加序列号(1)和payload大小
        full_client_request.extend((1).to_bytes(4, "big", signed=True))
        full_client_request.extend(len(payload_bytes).to_bytes(4, "big"))
        full_client_request.extend(payload_bytes)

        self.ws = await websockets.connect(
            self.ws_url, additional_headers=header, max_size=1000000000
        )
        await self.ws.send(full_client_request)
        response = await self.ws.recv()
        logger.info(f"WebSocket连接已建立: {response}")

    def start_mic(self):
        """启动麦克风"""
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        logger.info("麦克风已启动...")

    async def process_audio(self):
        """处理音频数据"""
        seq = 2  # 从2开始，因为1已经用于初始请求
        try:
            while self.is_running:
                # 读取音频数据
                data = self.stream.read(self.chunk, exception_on_overflow=False)

                # 压缩音频数据
                payload_bytes = gzip.compress(data)

                # 构造音频数据请求
                audio_request = bytearray(
                    [
                        0x11,  # 版本号和头部大小
                        0x21,  # 音频数据消息类型和标志
                        0x11,  # 序列化方法和压缩方式
                        0x00,  # 保留字段
                    ]
                )

                # 添加序列号和payload大小
                audio_request.extend(seq.to_bytes(4, "big", signed=True))
                audio_request.extend(len(payload_bytes).to_bytes(4, "big"))
                audio_request.extend(payload_bytes)

                # 发送音频数据
                await self.ws.send(audio_request)

                # 接收识别结果
                response = await self.ws.recv()
                try:
                    # 解析响应
                    if len(response) > 8:  # 确保响应包含足够的数据
                        # 跳过头部，直接读取payload
                        payload_start = 8  # 跳过基本头部和序列号
                        payload_size = int.from_bytes(
                            response[payload_start : payload_start + 4], "big"
                        )
                        payload_data = response[
                            payload_start + 4 : payload_start + 4 + payload_size
                        ]

                        if payload_data:  # 如果有payload数据
                            try:
                                # 尝试判断是否为gzip压缩数据
                                if payload_data.startswith(
                                    b"\x1f\x8b"
                                ):  # gzip magic number
                                    decoded_data = gzip.decompress(payload_data)
                                    result = json.loads(decoded_data)
                                else:
                                    # 如果不是gzip压缩的，直接当作JSON字符串处理
                                    result = json.loads(payload_data)

                                # 处理识别结果
                                if "result" in result:
                                    result_dict = (
                                        result["result"]
                                        if isinstance(result["result"], dict)
                                        else json.loads(result["result"])
                                    )
                                    if "utterances" in result_dict:
                                        current_text = ""
                                        for utterance in result_dict["utterances"]:
                                            if utterance.get("text"):
                                                current_text = utterance["text"]

                                        # 只有当文本内容发生变化时才打印
                                        if (
                                            current_text
                                            and current_text != self.last_text
                                        ):
                                            self.last_text = current_text
                                            logger.info(current_text)

                            except json.JSONDecodeError as e:
                                logger.error(
                                    f"JSON解析错误: {e}, 原始数据: {payload_data[:100]}"
                                )
                            except Exception as e:
                                logger.error(f"处理响应数据错误: {e}")

                except Exception as e:
                    logger.error(f"处理响应错误: {e}")

                seq += 1

        except KeyboardInterrupt:
            logger.info("\n识别已停止")
        except Exception as e:
            logger.error(f"处理音频时发生错误: {e}")

    async def cleanup(self):
        """清理资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()
        if self.ws:
            await self.ws.close()
        logger.info("已清理所有资源")

    async def run(self):
        """运行实时语音识别"""
        try:
            await self.init_websocket()
            self.start_mic()
            self.is_running = True
            logger.info("开始实时语音识别...")
            await self.process_audio()
        except Exception as e:
            logger.error(f"运行时发生错误: {e}")
        finally:
            await self.cleanup()


async def main():
    asr = RealTimeTiktokASR()
    await asr.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
