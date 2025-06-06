import asyncio
import websockets
from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable, Awaitable, Any
import json
import uuid

# ---------- 重连策略接口和实现 ----------


class ReconnectPolicy(ABC):
    """重连策略的抽象基类，定义重连等待时间的接口"""

    def get_wait_time(self, attempt: int) -> float:
        """
        获取重连等待时间
        :param attempt: 重试次数
        :return: 等待的秒数
        """
        pass


class ExponentialBackoffPolicy(ReconnectPolicy):
    """指数退避重连策略的实现，每次重试等待时间呈指数增长"""

    def __init__(self, base: float = 1.0, cap: float = 30.0):
        """
        初始化指数退避策略
        :param base: 基础等待时间（秒）
        :param cap: 最大等待时间（秒）
        """
        self.base = base
        self.cap = cap

    def get_wait_time(self, attempt: int) -> float:
        """
        计算指数退避等待时间
        :param attempt: 重试次数
        :return: 计算后的等待时间，不超过设定的上限
        """
        return min(self.cap, self.base * (2 ** (attempt - 1)))


# ---------- 消息处理器接口和实现 ----------


class MessageHandler(ABC):
    """消息处理器的抽象基类，定义消息处理接口"""

    @abstractmethod
    async def handle(self, message: str) -> None:
        """
        处理接收到的消息
        :param message: 接收到的消息内容
        """
        pass


class PrintMessageHandler(MessageHandler):
    """简单的打印消息处理器实现"""

    async def handle(self, message: str) -> None:
        """
        将接收到的消息打印到控制台
        :param message: 接收到的消息内容
        """
        print(f"[Message] {message}")


class JsonRpcMessageHandler(MessageHandler):
    """JSON-RPC消息处理器实现，支持RPC方法注册和请求响应处理"""

    def __init__(self):
        """
        初始化JSON-RPC处理器，设置方法字典和待处理请求字典
        """
        self._methods: Dict[str, Callable[[dict], Awaitable[None]]] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}

    def register_method(
        self, name: str, func: Callable[[dict], Awaitable[None]]
    ) -> None:
        """
        注册RPC方法
        :param name: 方法名
        :param func: 处理方法的异步函数
        """
        self._methods[name] = func

    async def handle(self, message: str) -> None:
        """
        处理JSON-RPC消息
        :param message: JSON格式的消息字符串
        """
        try:
            data = json.loads(message)
            if "id" in data and "result" in data:
                # This is a response
                req_id: str = data["id"]
                if req_id in self._pending_requests:
                    self._pending_requests[req_id].set_result(data["result"])
                    del self._pending_requests[req_id]
            elif "method" in data:
                method: Optional[str] = data.get("method")
                if method in self._methods:
                    await self._methods[method](data)
                else:
                    print(f"[Unhandled RPC Method] {method}")
        except Exception as e:
            print(f"[JSON-RPC Error] {e}")

    async def send_request(
        self,
        websocket: websockets.WebSocketClientProtocol,
        method: str,
        params: Any,
        timeout: float = 10.0,
    ) -> Any:
        """
        发送RPC请求
        :param websocket: WebSocket连接实例
        :param method: 调用的方法名
        :param params: 方法参数
        :param timeout: 超时时间（秒）
        :return: 响应结果
        """
        req_id = str(uuid.uuid4())
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_requests[req_id] = future

        request = json.dumps(
            {"jsonrpc": "2.0", "method": method, "params": params, "id": req_id}
        )
        await websocket.send(request)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise TimeoutError(f"Request {req_id} timed out")


# ---------- 心跳管理器接口和实现 ----------


class HeartbeatManager(ABC):
    """心跳管理器的抽象基类，用于维持WebSocket连接活跃"""

    @abstractmethod
    async def start(self, websocket: websockets.WebSocketClientProtocol) -> None:
        """
        启动心跳管理
        :param websocket: WebSocket连接实例
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        停止心跳管理
        """
        pass


class PingHeartbeatManager(HeartbeatManager):
    """基于ping的心跳管理器实现"""

    def __init__(self, interval: int = 10):
        """
        初始化心跳管理器
        :param interval: 心跳间隔时间（秒）
        """
        self.interval = interval
        self._task: Optional[asyncio.Task] = None

    async def _ping_loop(self, websocket: websockets.WebSocketClientProtocol) -> None:
        """
        心跳维持循环
        :param websocket: WebSocket连接实例
        """
        while True:
            try:
                await websocket.ping()
                await asyncio.sleep(self.interval)
            except Exception:
                break

    async def start(self, websocket: websockets.WebSocketClientProtocol) -> None:
        """
        启动心跳任务
        :param websocket: WebSocket连接实例
        """
        self._task = asyncio.create_task(self._ping_loop(websocket))

    async def stop(self) -> None:
        """
        停止心跳任务
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


# ---------- 可插拔式WebSocket服务 ----------


class PluggableWebSocketService:
    """
    可插拔式WebSocket服务的主类，支持：
    - 可配置的重连策略
    - 可配置的消息处理器
    - 可配置的心跳机制
    """

    def __init__(self, uri: str):
        """
        初始化WebSocket服务
        :param uri: WebSocket服务器地址
        """
        self._uri = uri
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._running: bool = False
        self._reconnect_policy: ReconnectPolicy = ExponentialBackoffPolicy()
        self._message_handler: MessageHandler = PrintMessageHandler()
        self._heartbeat: Optional[HeartbeatManager] = None

    def set_reconnect_policy(self, policy: ReconnectPolicy) -> None:
        """
        设置重连策略
        :param policy: 重连策略实例
        """
        self._reconnect_policy = policy

    def set_message_handler(self, handler: MessageHandler) -> None:
        """
        设置消息处理器
        :param handler: 消息处理器实例
        """
        self._message_handler = handler

    def set_heartbeat(self, manager: HeartbeatManager) -> None:
        """
        设置心跳管理器
        :param manager: 心跳管理器实例
        """
        self._heartbeat = manager

    async def connect(self) -> None:
        """
        建立WebSocket连接
        """
        self._websocket = await websockets.connect(self._uri)
        if self._heartbeat:
            await self._heartbeat.start(self._websocket)

    async def disconnect(self) -> None:
        """
        断开WebSocket连接
        """
        if self._websocket:
            await self._websocket.close()
        if self._heartbeat:
            await self._heartbeat.stop()

    async def run_forever(self) -> None:
        """
        永久运行WebSocket服务，包含自动重连机制
        """
        self._running = True
        attempt = 0

        while self._running:
            try:
                await self.connect()
                async for msg in self._websocket:
                    await self._message_handler.handle(msg)
                attempt = 0
            except Exception as e:
                attempt += 1
                wait_time: float = self._reconnect_policy.get_wait_time(attempt)
                print(f"[Reconnect] Waiting {wait_time}s after error: {e}")
                await asyncio.sleep(wait_time)

    async def stop(self) -> None:
        """
        停止WebSocket服务
        """
        self._running = False
        await self.disconnect()


# ---------- 示例用法 ----------


async def handle_echo(data: dict) -> None:
    """Echo请求的处理函数"""
    print(f"[RPC Request] {data}")


async def handle_custom_event(data: dict) -> None:
    """自定义事件处理"""
    print(f"[Custom Event] Received data: {data}")


async def demo_different_configs():
    """
    演示不同配置组合的使用方法
    """
    # 1. 基础配置 - 只打印消息
    basic_ws = PluggableWebSocketService("wss://echo.websocket.events")

    # 2. 自定义重连策略的配置
    custom_reconnect_ws = PluggableWebSocketService("wss://echo.websocket.events")
    custom_reconnect_ws.set_reconnect_policy(ExponentialBackoffPolicy(base=1.5, cap=15))

    # 3. 自定义消息处理器
    class CustomMessageHandler(MessageHandler):
        async def handle(self, message: str) -> None:
            print(f"[Custom Handler] Received: {message}")
            # 进行自定义处理...

    custom_handler_ws = PluggableWebSocketService("wss://echo.websocket.events")
    custom_handler_ws.set_message_handler(CustomMessageHandler())

    # 4. 完整配置示例
    full_config_ws = PluggableWebSocketService("wss://echo.websocket.events")
    rpc_handler = JsonRpcMessageHandler()
    rpc_handler.register_method("custom_event", handle_custom_event)

    full_config_ws.set_reconnect_policy(ExponentialBackoffPolicy(base=2, cap=20))
    full_config_ws.set_message_handler(rpc_handler)
    full_config_ws.set_heartbeat(PingHeartbeatManager(interval=30))

    # 启动服务示例
    try:
        await full_config_ws.run_forever()
    except KeyboardInterrupt:
        await full_config_ws.stop()


# 修改main函数使用新的示例
async def main() -> None:
    """
    主函数，展示WebSocket服务的不同配置和使用方式
    """
    await demo_different_configs()


if __name__ == "__main__":
    asyncio.run(main())
