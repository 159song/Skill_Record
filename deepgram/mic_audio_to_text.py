import pyaudio
import numpy as np
import matplotlib.pyplot as plt

from silero import SileroVADAnalyzer
from vad_analyzer import VADParams, VADState
import asyncio
import json
import threading
from dotenv import load_dotenv
import os
from loguru import logger
from stt import Deepgram_Client

# 加载环境变量
load_dotenv()

# 配置 Deepgram API 密钥
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# 配置音频参数
CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000

# 初始化 PyAudio
p = pyaudio.PyAudio()
input_stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

# 初始化 Silero VAD
vad_params = VADParams(confidence=0.5, start_secs=0.1, stop_secs=0.4, min_volume=0.4)
silero_vad = SileroVADAnalyzer(sample_rate=RATE, params=vad_params)

# 初始化 Deepgram Client
stt_client = Deepgram_Client()


# 初始化绘图窗口
plt.ion()
fig, ax = plt.subplots()
x = np.arange(0, CHUNK)
(line,) = ax.plot(x, np.random.rand(CHUNK))
ax.set_ylim([-32768, 32768])
text = "Transcribed:"


async def main():

    # 实时音频处理循环
    while True:
        audio_data = input_stream.read(CHUNK, exception_on_overflow=False)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # reduced_noise = nr.reduce_noise(y=audio_array, sr=RATE).tobytes()
        reduced_noise = audio_array.tobytes()

        # 检测语音活动
        vad_state = silero_vad.analyze_audio(reduced_noise)

        stt_client.audio_send(reduced_noise)

        ax.set_title(text + stt_client.text)
        if vad_state in [VADState.STARTING, VADState.SPEAKING]:
            # 实时波形更新
            line.set_ydata(audio_array)

        else:
            line.set_ydata(np.zeros(CHUNK))
        fig.canvas.draw()
        fig.canvas.flush_events()


if __name__ == "__main__":
    asyncio.run(main())
