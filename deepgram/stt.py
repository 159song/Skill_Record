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


finalize_after = 0.5
timer_task = None


class Deepgram_Client:
    def __init__(self, sample_rate):
        self.sample_rate: int = sample_rate
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient(
            api_key=os.getenv("DEEPGRAM_API_KEY"), config=config
        )
        # deepgram: DeepgramClient = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))
        self.dg_connection = deepgram.listen.websocket.v("1")
        self.connect()
        self.text = ""

    def reset_timer(self):
        global timer_task
        if timer_task:
            timer_task.cancel()
        timer_task = asyncio.create_task(self.timer_coroutine())

    async def timer_coroutine(self):
        await asyncio.sleep(finalize_after)
        await self.send_finalize()

    async def send_finalize(self):
        await self.dg_connection.send(json.dumps({"type": "Finalize"}))
        logger.info(f"Finalize sent due to {finalize_after} seconds of silence")
        logger.info(f"Finalize sent due to {finalize_after} seconds of silence")

    def connect(self):

        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        # config = DeepgramClientOptions(
        #     verbose=verboselogs.DEBUG, options={"keepalive": "true"}
        # )
        # deepgram: DeepgramClient = DeepgramClient("", config)
        # otherwise, use default config
        connect_stt(self.dg_connection, self)
        options: LiveOptions = LiveOptions(
            encoding="linear16",
            language="en-US",
            model="nova-2-general",
            channels=1,
            interim_results=True,
            smart_format=True,
            punctuate=True,
            profanity_filter=False,
            vad_events=False,
            numerals=True,
            sample_rate=self.sample_rate,
        )

        if self.dg_connection.start(options, addons=None) is False:
            logger.info("Failed to connect to Deepgram")
            return
        logger.info("Starting Deepgram connection...")

    def audio_send(self, audio):
        self.dg_connection.send(audio)


def connect_stt(dg_connection, client):
    def on_open(self, open, **kwargs):
        logger.info("Connection Open")

    def on_message(self, result, **kwargs):

        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        # reset_timer()
        if result.is_final:
            client.text = sentence
            logger.info(f"Is Final: {sentence}")
            logger.info(
                "------------------------------------------------------------------------------------------------"
            )
        else:
            # These are useful if you need real time captioning of what is being spoken
            logger.info(f"Interim Results: {sentence}")

    def on_metadata(self, metadata, **kwargs):
        logger.info(f"Metadata: {metadata}")

    def on_speech_started(self, speech_started, **kwargs):
        logger.info("Speech Started")

    def on_utterance_end(self, utterance_end, **kwargs):
        logger.info("Utterance End")

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
