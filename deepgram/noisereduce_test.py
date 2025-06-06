import pyaudio
import numpy as np
import sounddevice as sd
import noisereduce as nr
from vad_analyzer import VADParams, VADState
from silero import SileroVADAnalyzer
from loguru import logger

# 配置参数
CHUNK = 256  # 每次处理的音频块大小
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 8000  # 采样率

# 初始化 PyAudio
p = pyaudio.PyAudio()

# 打开麦克风输入流
input_stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

# 创建 sounddevice 输出流
output_stream = sd.OutputStream(samplerate=RATE, channels=CHANNELS, dtype="int16")
output_stream.start()

# 初始化 Silero VAD
vad_params = VADParams(confidence=0.7, start_secs=0.1, stop_secs=0.4, min_volume=0.7)
silero_vad = SileroVADAnalyzer(sample_rate=RATE, params=vad_params)

print("开始实时降噪音频处理 (Ctrl+C 退出)...")

try:
    while True:
        # 从麦克风读取数据
        audio_data = input_stream.read(CHUNK, exception_on_overflow=False)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # 语音活动检测
        vad_state = silero_vad.analyze_audio(audio_data)

        if vad_state in [VADState.STARTING, VADState.SPEAKING]:
            # 检测到语音活动，进行降噪处理
            logger.info("检测到语音活动")
            reduced_noise = nr.reduce_noise(y=audio_array, sr=RATE, prop_decrease=2)
        else:
            logger.info("---------------")
            # 没有语音活动，直接输出原始音频
            reduced_noise = audio_array

        # 将处理后的音频播放
        output_stream.write(reduced_noise.astype(np.int16))
except KeyboardInterrupt:
    print("停止音频处理...")
finally:
    # 关闭音频流
    input_stream.stop_stream()
    input_stream.close()
    output_stream.close()
    p.terminate()
