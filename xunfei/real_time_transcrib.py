# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa) + "&lang=cn&engLangType=4")
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    # def send(self, file_path):
    #     file_object = open(file_path, 'rb')
    #     try:
    #         index = 1
    #         while True:
    #             chunk = file_object.read(1280)
    #             if not chunk:
    #                 break
    #             self.ws.send(chunk)

    #             index += 1
    #             time.sleep(0.04)
    #     finally:
    #         file_object.close()

    #     self.ws.send(bytes(self.end_tag.encode('utf-8')))
    #     print("send end tag success")
    def send(self):
        # 设置音频流参数
        chunk = 1024  # 每次读取的音频数据块大小
        format = pyaudio.paInt16  # 音频格式
        channels = 1  # 单声道
        rate = 16000  # 采样率

        # 初始化 PyAudio
        p = pyaudio.PyAudio()

        # 打开音频流
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print("开始录音...")

        try:
            while True:
                # 从麦克风读取音频数据
                data = stream.read(chunk)
                self.ws.send(data)
                time.sleep(0.04)
        except KeyboardInterrupt:
            print("录音结束")
        finally:
            # 关闭音频流
            stream.stop_stream()
            stream.close()
            p.terminate()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        print("send end tag success")

    def recv(self): 
        
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)
                
                if result_dict["action"] == "result":
                    data =  json.loads( result_dict["data"])
                    word_type =  data["cn"]["st"]["type"]
                    word = ""
                    for rt in data["cn"]["st"]["rt"]:
                        for ws in rt["ws"]:
                            for cw in ws["cw"]:
                                word+=cw["w"]
                    if word_type == '0':
                        print(f"final:{word}")
                        
                    elif word_type == '1':
                        print(f"interim:{word}")
                    word = ""
                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")
if __name__ == '__main__':
    logging.basicConfig()

    
    file_path = r"./test_1.pcm"

    client = Client()
    client.send()
