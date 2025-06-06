from pydub import AudioSegment
import asyncio
from stt import Deepgram_Client

# Load your .m4a file
audio = AudioSegment.from_file("phone_test.m4a", format="m4a")

# Export as .wav file
audio.export("phone_test_48000.wav", format="wav")

import wave

# Open the .wav file
with wave.open("phone_test_48000.wav", "rb") as wav_file:
    # Get the number of channels
    channels = wav_file.getnchannels()
    # Get the sample rate
    sample_rate = wav_file.getframerate()

print(f"phone_test_48000 Channels: {channels}")
print(f"phone_test_48000 Sample Rate: {sample_rate} Hz")

from pydub import AudioSegment

# Load your .wav file
audio = AudioSegment.from_file("phone_test_48000.wav", format="wav")

# Set the frame rate to 8000 Hz
audio = audio.set_frame_rate(8000)

# Export the modified audio as a new .wav file
audio.export("phone_test_8000.wav", format="wav")

# Open the .wav file
with wave.open("phone_test_8000.wav", "rb") as wav_file:
    # Get the number of channels
    channels = wav_file.getnchannels()
    # Get the sample rate
    sample_rate = wav_file.getframerate()

print(f"phone_test_8000 Channels: {channels}")
print(f"phone_test_8000 Sample Rate: {sample_rate} Hz")


async def push_audio(file_path: str, sample_rate: int = 48000):
    print(f"{file_path}")
    num_channels = 1
    num_frames = int(sample_rate / 100) * 2
    stt_model = Deepgram_Client(sample_rate=sample_rate)
    with wave.open(file_path, "rb") as wav_file:
        # Ensure the WAV file has the expected sample rate and number of channels
        if (
            wav_file.getframerate() != sample_rate
            or wav_file.getnchannels() != num_channels
        ):
            raise ValueError(
                "WAV file sample rate or number of channels does not match expected values."
            )

        while True:
            audio_data = wav_file.readframes(num_frames)
            if len(audio_data) > 0:
                stt_model.audio_send(audio_data)
                await asyncio.sleep(0.02)
            else:
                break


asyncio.run(push_audio(file_path="phone_test_8000.wav", sample_rate=8000))
asyncio.run(push_audio(file_path="phone_test_48000.wav", sample_rate=48000))
