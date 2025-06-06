import redis

# 连接 Redis
r = redis.Redis(host="localhost", port=6379, db=0)

# 定义号码和键名
caller = "+14158887996"
receiver = "+111"
phone_count_key = f"phone_count:{caller}:{receiver}"

# 获取所有呼叫记录
all_calls = r.zrange(f"{phone_count_key}:calls", 0, -1)

# 删除记录及其状态
for call in all_calls:
    timestamp = call.decode()

    # 删除状态记录
    status_key = f"{phone_count_key}:call_status:{timestamp}"
    r.delete(status_key)

    print(f"删除通话记录: 时间戳 {timestamp}")

# 删除呼叫记录和状态统计
r.delete(f"{phone_count_key}:calls")
r.delete(f"{phone_count_key}:status_count")

# 确认删除成功
print("\n所有呼叫记录及状态统计已删除。")
