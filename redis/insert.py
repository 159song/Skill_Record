import redis
import time
import random

# 连接 Redis
r = redis.Redis(host="localhost", port=6379, db=0)

# 定义号码和状态
caller = "+14158887996"
receiver = "+111"
phone_count_key = f"phone_count:{caller}:{receiver}"
statuses = ["成功下单", "未下单", "投诉", "转接", "超时转接", "超时挂机", "脏话挂机"]

# 插入几条记录
inserted_records = []
for _ in range(5):  # 插入 5 条记录
    current_timestamp = int(time.time()) + random.randint(0, 1000)
    status = random.choice(statuses)

    # 写入呼叫记录到 ZSET
    r.zadd(f"{phone_count_key}:calls", {current_timestamp: current_timestamp})

    # 写入呼叫状态
    r.hset(f"{phone_count_key}:call_status:{current_timestamp}", "status", status)

    # 更新状态统计计数
    r.hincrby(f"{phone_count_key}:status_count", status, 1)

    # 保存插入信息
    inserted_records.append((current_timestamp, status))

# 获取记录以确认插入结果
recent_calls = r.zrange(f"{phone_count_key}:calls", 0, -1)
call_details = [
    (
        int(call.decode()),
        r.hget(f"{phone_count_key}:call_status:{call.decode()}", "status").decode(),
    )
    for call in recent_calls
]

# 打印插入结果
print("插入的记录:")
for record in inserted_records:
    print(f"时间戳: {record[0]}, 状态: {record[1]}")

# 打印 Redis 中的记录
print("\nRedis 中的记录:")
for detail in call_details:
    call_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(detail[0]))
    print(f"时间: {call_time}, 状态: {detail[1]}")

# 打印状态统计
print("\n状态统计:")
status_stats = r.hgetall(f"{phone_count_key}:status_count")
for status, count in status_stats.items():
    print(f"{status.decode()}: {count.decode()}")
