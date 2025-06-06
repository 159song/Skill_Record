import redis

# 连接 Redis
r = redis.Redis(host="localhost", port=6379, db=0)


def query_status_statistics(caller, receiver):
    """查询状态统计"""
    phone_count_key = f"phone_count:{caller}:{receiver}"

    # 获取状态统计
    status_stats = r.hgetall(f"{phone_count_key}:status_count")

    print(f"\n状态统计 ({caller} → {receiver}):")
    if not status_stats:
        print("没有找到任何统计记录。")
    else:
        for status, count in status_stats.items():
            print(f"{status.decode()}: {count.decode()}")


# 示例调用
caller = "+14158887996"
receiver = "+111"
query_status_statistics(caller, receiver)
