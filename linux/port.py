import asyncio
import websockets
import sounddevice as sd
import numpy as np


async def play_audio():
    uri = "ws://localhost:<local_port>"
    async with websockets.connect(uri) as websocket:
        async for audio_data in websocket:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio_array, samplerate=24000)


if __name__ == "__main__":
    asyncio.run(play_audio())
