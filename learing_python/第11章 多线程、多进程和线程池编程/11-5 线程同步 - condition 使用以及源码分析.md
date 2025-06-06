```
"""第一版本"""
import threading
class XiaoAi(threading.Thread):
    def __init__(self,lock):
        super().__init__(name="小爱")
        self.lock = lock
    def run(self):
        self.lock.acquire()
        print("{}: 在".format(self.name))
        self.lock.release()
        self.lock.acquire()
        print("{}: 好啊".format(self.name))
        self.lock.release()
        
class TianMao(threading.Thread):
    def __init__(self,lock):
        super().__init__(name="天猫精灵")
        self.lock = lock
    def run(self):
        self.lock.acquire()
        print("{}:小爱同学 ".format(self.name))
        self.lock.release()
        self.lock.acquire()
        print("{}:我们来对古诗吧 ".format(self.name))
        self.lock.release()
if __name__ =="__main___":
    lock = threading.Lock()
    xiaoai =XiaoAi()
    tianmao =TianMao()
    tianmao.start()
    xiaoai.start()
    
"""通过condition方法"""
from threading import condition
class XiaoAi(threading.Thread):
    def __init__(self,cond):
        super().__init__(name="小爱")
        self.cond = cond
    def run(self):
        with self.cond:
            self.cond.wait()
            print("{}: 在".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:好啊 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:君住长江尾 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:共饮长江水 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:此恨何时已 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:定不负相思意 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
    
class TianMao(threading.Thread):
    def __init__(self,cond):
        super().__init__(name="天猫精灵")
        self.cond = cond
    def run(self):
        with self.cond:
            print("{}:小爱同学 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            print("{}:我们来对古诗吧 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:我住长江头 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:日日思君不见君 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:此水几时休 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            
            print("{}:只愿君心似我心 ".format(self.name))
            self.cond.notify()
            self.cond.wait()
            

if __name__ =="__main___":
    cond = threading.Condition()
    xiaoai =XiaoAi(cond)
    tianmao =TianMao(cond)
    xiaoai.start()
    tianmao.start()

1. with self.cond 实现原理
with语句使用了上下文管理器协议，Condition对象实现了__enter__和__exit__方法：
# Condition内部实现大致如下
class Condition:
    def __enter__(self):
        # 获取底层锁
        self._lock.acquire()
        return self
        
    def __exit__(self, *args):
        # 释放底层锁
        self._lock.release()

2. notify()和wait()实现机制
wait()工作原理：
创建一个新的锁（waiter）用于等待
将waiter加入等待队列
释放condition的底层锁
等待通知（阻塞在waiter上）
重新获取condition的底层锁

def wait(self, timeout=None):
    waiter = _allocate_lock()  # 创建等待锁
    waiter.acquire()  # 锁住waiter
    self._waiters.append(waiter)  # 加入等待队列
    
    # 释放condition的锁，允许其他线程执行
    self._lock.release()
    
    try:
        # 在waiter上等待
        waiter.acquire()
    finally:
        # 重新获取condition的锁
        self._lock.acquire()

GitHub Copilot
Python Condition实现原理解析
1. with self.cond 实现原理
with语句使用了上下文管理器协议，Condition对象实现了__enter__和__exit__方法：

2. notify()和wait()实现机制
wait()工作原理：
创建一个新的锁（waiter）用于等待
将waiter加入等待队列
释放condition的底层锁
等待通知（阻塞在waiter上）
重新获取condition的底层锁
notify()工作原理：
从等待队列中获取一个waiter
释放该waiter的锁，唤醒等待的线程

def notify(self, n=1):
    if not self._lock._is_owned():
        raise RuntimeError("cannot notify on un-acquired lock")
        
    waiters = self._waiters
    if not waiters:
        return
        
    waiter = waiters.pop()  # 获取一个waiter
    waiter.release()  # 释放waiter锁，唤醒等待的线程


3. 整体工作流程
以代码中的对话为例：

天猫精灵线程：
with self.cond:  # 获取锁
    print("小爱同学")  
    self.cond.notify()  # 唤醒小爱
    self.cond.wait()  # 等待小爱回应

小爱线程：
with self.cond:  # 获取锁
    self.cond.wait()  # 等待天猫呼叫
    print("在")
    self.cond.notify()  # 唤醒天猫
    self.cond.wait()  # 等待下一个对话

4. 关键特点
Condition内部维护了一个锁和一个等待队列
wait()会释放锁并阻塞当前线程
notify()会唤醒等待队列中的一个线程
使用with语句自动管理锁的获取和释放
整个机制保证了线程间的有序通信