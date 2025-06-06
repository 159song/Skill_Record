import asyncio
from typing import List, Any

# -------- asyncio 常用方法示例 --------


async def demo_basic_operations():
    """基础操作示例"""
    # 1. 基本的异步等待
    await asyncio.sleep(1)  # 异步休眠1秒

    # 2. 创建任务
    async def background_task():
        await asyncio.sleep(2)
        return "task completed"

    task = asyncio.create_task(background_task())  # 创建一个任务
    result = await task  # 等待任务完成


async def demo_concurrent_operations():
    """并发操作示例"""

    # 1. 并发执行多个协程
    async def worker(n: int) -> int:
        await asyncio.sleep(1)
        return n * 2

    # gather 同时运行多个协程
    results = await asyncio.gather(worker(1), worker(2), worker(3))

    # 2. 使用 wait 等待多个协程（可设置超时）
    tasks = [worker(i) for i in range(3)]
    done, pending = await asyncio.wait(
        tasks, timeout=2.0, return_when=asyncio.ALL_COMPLETED
    )


async def demo_timeouts():
    """超时控制示例"""

    async def long_operation():
        await asyncio.sleep(5)
        return "完成"

    try:
        # 使用 wait_for 设置超时
        result = await asyncio.wait_for(long_operation(), timeout=2.0)
    except asyncio.TimeoutError:
        print("操作超时")


async def demo_async_primitives():
    """异步原语示例"""
    # 1. 锁
    lock = asyncio.Lock()
    async with lock:
        await asyncio.sleep(1)  # 临界区代码

    # 2. 事件
    event = asyncio.Event()

    async def waiter():
        await event.wait()
        print("事件被触发")

    task = asyncio.create_task(waiter())
    await asyncio.sleep(1)
    event.set()  # 触发事件
    await task

    # 3. 信号量
    sem = asyncio.Semaphore(2)  # 最多允许2个并发
    async with sem:
        await asyncio.sleep(1)


async def demo_queue_operations():
    """队列操作示例"""
    # 创建一个异步队列
    queue = asyncio.Queue()

    # 生产者
    async def producer():
        for i in range(3):
            await queue.put(i)
            await asyncio.sleep(1)

    # 消费者
    async def consumer():
        while True:
            item = await queue.get()
            print(f"处理项目: {item}")
            queue.task_done()

    # 启动生产者和消费者
    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    await producer_task
    await queue.join()  # 等待队列处理完成
    consumer_task.cancel()  # 取消消费者任务


async def main():
    """主函数：运行所有示例"""
    await demo_basic_operations()
    await demo_concurrent_operations()
    await demo_timeouts()
    await demo_async_primitives()
    await demo_queue_operations()


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
