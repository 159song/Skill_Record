import pyaudio
import time
from loguru import logger


class MicAudio:
    def __init__(self):
        self.chunk = 1280  # 每次读取的音频数据块大小
        self.format = pyaudio.paInt16  # 音频格式
        self.channels = 1  # 单声道
        self.rate = 16000  # 采样率

        # 初始化 PyAudio
        self.p = pyaudio.PyAudio()
        self.start()

    def start(
        self,
    ):
        # 打开音频流
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        logger.info("开始录音...")

    def send_audio(self, send_func):

        try:
            while True:
                # 从麦克风读取音频数据
                data = self.stream.read(self.chunk)
                send_func(data)
                time.sleep(0.04)
        except KeyboardInterrupt:
            logger.info("录音中断")
        finally:
            # 关闭音频流
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        logger.info("录音结束")
