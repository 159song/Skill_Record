```
# semaphore 是用于控制进入数量的锁
#文件。读写，写一般只是用于一个协程写，读可以允许有多个
#做爬虫，
import threading
import time

class HtmlSpider(threading.Thread):
    def __init__(self,url,sem):
        super().__init__()
        self.url = url
        self.sem = sem
    def run(self):
        time.sleep(2)
        print("got html text success")
        self.sem.release()


class UrlProducer(threading.Thread):
    def __init__(self,sem):
        super().__init__()
        self.sem = sem
    def run(self):
        for i in range(20):
            self.sem.acquire()
            html_thread = HtmlSpider("https://baidu.com/{}".format(i),self.sem)
            html_thread.start()


if __name__=='__main__':
    sem = threading.Semaphore(3)
    url_producer = UrlProducer(sem)
    url_producer.start()
    #查看queue中的condition
    ```
Python threading.Semaphore 内部实现原理
1. 基本结构
Semaphore 在内部主要由以下组件构成：

一个 Condition 对象
一个计数器(_value)
2. 核心实现代码


class Semaphore:
    def __init__(self, value=1):
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._cond = threading.Condition(threading.Lock())
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        
        rc = False
        with self._cond:
            while self._value == 0:
                if not blocking:
                    break
                if timeout is None:
                    self._cond.wait()
                else:
                    if not self._cond.wait(timeout):
                        break
            else:
                self._value -= 1
                rc = True
        return rc

    def release(self):
        with self._cond:
            self._value += 1
            self._cond.notify()

# Semaphore的实现原理详解

class Semaphore:
    """Semaphore的核心实现流程：
    
    1. 初始化：
       - 创建一个Condition对象作为同步原语
       - 设置初始计数器值
    
    2. acquire方法实现：
       - 获取条件锁
       - 当计数器为0时等待
       - 成功获取时计数器减1
    
    3. release方法实现：
       - 获取条件锁
       - 增加计数器值
       - 通知等待的线程
    """
    def __init__(self, value=1):
        """初始化信号量
        
        Args:
            value: 信号量初始值，默认为1
            
        实现要点：
        1. 参数检查
        2. 创建条件变量
        3. 初始化计数器
        """
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._cond = threading.Condition(threading.Lock())
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        """获取信号量
        
        Args:
            blocking: 是否阻塞等待
            timeout: 超时时间
            
        实现要点：
        1. 参数验证
        2. 使用with语句管理条件锁
        3. 等待直到资源可用
        4. 更新计数器
        """
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        
        rc = False
        with self._cond:  # 自动获取和释放条件锁
            while self._value == 0:  # 当没有资源时循环等待
                if not blocking:  # 非阻塞模式直接返回
                    break
                if timeout is None:  # 无限期等待
                    self._cond.wait()
                else:  # 带超时的等待
                    if not self._cond.wait(timeout):
                        break
            else:  # 资源可用时
                self._value -= 1  # 减少计数器
                rc = True  # 标记获取成功
        return rc

    def release(self):
        """释放信号量
        
        实现要点：
        1. 使用with语句管理条件锁
        2. 增加计数器值
        3. 通知等待的线程
        """
        with self._cond:
            self._value += 1  # 增加计数器
            self._cond.notify()  # 通知等待的线程

核心特点：
1. 原子操作保证
   - 所有对计数器的操作都在条件锁的保护下进行
   - 确保线程安全

2. 灵活的等待机制
   - 支持阻塞和非阻塞模式
   - 支持超时机制
   - 基于FIFO的等待队列

3. 异常安全
   - 使用with语句确保锁的正确释放
   - 避免死锁情况

4. 使用场景
   - 限制并发访问数
   - 资源池管理
   - 生产者消费者模式
````