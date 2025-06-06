# Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv
from time import sleep
import logging

from deepgram.utils import verboselogs

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from typing import List, Optional, Union
import threading
import json
import asyncio
from loguru import logger
import os

load_dotenv()

# We will collect the is_final=true messages here so we can use them when the person finishes speaking
is_finals = []

finalize_after = 0.5
timer_task = None


async def main():

    def reset_timer():
        global timer_task
        if timer_task:
            timer_task.cancel()
        timer_task = asyncio.create_task(timer_coroutine())

    async def timer_coroutine():
        await asyncio.sleep(finalize_after)
        await send_finalize()

    async def send_finalize():
        await dg_connection.send(json.dumps({"type": "Finalize"}))
        logger.info(f"Finalize sent due to {finalize_after} seconds of silence")
        logger.info(f"Finalize sent due to {finalize_after} seconds of silence")

    try:
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        # config = DeepgramClientOptions(
        #     verbose=verboselogs.DEBUG, options={"keepalive": "true"}
        # )
        # deepgram: DeepgramClient = DeepgramClient("", config)
        # otherwise, use default config
        deepgram: DeepgramClient = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

        dg_connection = deepgram.listen.websocket.v("1")

        def on_open(self, open, **kwargs):
            logger.info("Connection Open")

        def on_message(self, result, **kwargs):
            global is_finals
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            # reset_timer()
            if result.is_final:

                # logger.info(f"Message: {result.to_json()}")
                # We need to collect these and concatenate them together when we get a speech_final=true
                # See docs: https://developers.deepgram.com/docs/understand-endpointing-interim-results
                is_finals.append(sentence)

                # Speech Final means we have detected sufficent silence to consider this end of speech
                # Speech final is the lowest latency result as it triggers as soon an the endpointing value has triggered
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    logger.info(f"Speech Final: {utterance}")
                    is_finals = []
                else:
                    # These are useful if you need real time captioning and update what the Interim Results produced
                    logger.info(f"Is Final: {sentence}")
            else:
                # These are useful if you need real time captioning of what is being spoken
                logger.info(f"Interim Results: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            logger.info(f"Metadata: {metadata}")

        def on_speech_started(self, speech_started, **kwargs):
            logger.info("Speech Started")

        def on_utterance_end(self, utterance_end, **kwargs):
            logger.info("Utterance End")
            global is_finals
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                logger.info(f"Utterance End: {utterance}")
                is_finals = []

        def on_close(self, close, **kwargs):
            logger.info("Connection Closed")

        def on_error(self, error, **kwargs):
            logger.info(f"Handled Error: {error}")

        def on_unhandled(self, unhandled, **kwargs):
            logger.info(f"Unhandled Websocket Message: {unhandled}")

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)
        options: LiveOptions = LiveOptions(
            model="nova-2",
            language="zh-TW",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            # interim_results=True,
            # utterance_end_ms="1000",
            # vad_events=True,
            # endpointing=300,
            # numerals=True,
            # keywords=["order:100"],
            # replace=[
            #     "yes:No",
            #     "Tom:1",
            #     "hiccup:Pickup",
            #     "Makeup:Pickup",
            #     "backup:Pickup",
            #     "shakeup:Pickup",
            #     "back up:Pickup",
            #     "stick up:Pickup",
            #     "kick up:Pickup",
            #     "back up:Pickup",
            #     "Pick out:Pickup",
            #     "tick up:Pickup",
            #     "Ecom:Pickup",
            #     "Peacock:Pickup",
            #     "Peak up:Pickup",
            #     "Hiccup:Pickup",
            #     "Pick up:Pickup",
            # ],
        )

        addons = {
            "no_delay": "true",
        }

        logger.info("\n\nPress Enter to stop recording...\n\n")
        if dg_connection.start(options, addons=addons) is False:
            logger.info("Failed to connect to Deepgram")
            return

        microphone = Microphone(dg_connection.send)
        microphone.start()
        input("")
        microphone.finish()
        dg_connection.finish()
        logger.info("Finished")

    except Exception as e:
        logger.info(f"Could not open socket: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
