import redis
import time
import random
from loguru import logger
from enum import Enum


class CallStatus(Enum):
    ORDER_PLACED_SUCCESSFULLY = "Order Placed Successfully"
    ORDER_NOT_PLACED = "Order Not Placed"
    COMPLAINT = "Complaint"
    CALL_TRANSFERRED = "Call Transferred"
    TRANSFER_TIMEOUT = "Transfer Timeout"
    HANG_UP_TIMEOUT = "Hang Up Timeout"
    HANG_UP_DUE_TO_ABUSIVE_LANGUAGE = "Hang Up Due to Abusive Language"


class CallRecordManager:
    def __init__(self, host="localhost", port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def _get_redis_client(self):
        return redis.Redis(host=self.host, port=self.port, db=self.db)

    def call_insert_random(self, from_phone: str, to_phone: str, num=10):
        phone_count_key = f"phone_count:{from_phone}:{to_phone}"
        inserted_records = []

        with self._get_redis_client() as r:
            for _ in range(num):
                current_timestamp = int(time.time()) + random.randint(0, 1000)
                status = random.choice(list(CallStatus)).value

                r.zadd(
                    f"{phone_count_key}:calls", {current_timestamp: current_timestamp}
                )
                r.hset(
                    f"{phone_count_key}:call_status:{current_timestamp}",
                    "status",
                    status,
                )
                r.hincrby(f"{phone_count_key}:status_count", status, 1)

                inserted_records.append((current_timestamp, status))

            self._log_inserted_records(inserted_records, phone_count_key)

    def call_insert(self, from_phone: str, to_phone: str, state: CallStatus):
        phone_count_key = f"phone_count:{from_phone}:{to_phone}"
        current_timestamp = int(time.time()) + random.randint(0, 1000)
        status_value = state.value

        with self._get_redis_client() as r:
            r.zadd(f"{phone_count_key}:calls", {current_timestamp: current_timestamp})
            r.hset(
                f"{phone_count_key}:call_status:{current_timestamp}",
                "status",
                status_value,
            )
            r.hincrby(f"{phone_count_key}:status_count", status_value, 1)

            self._log_inserted_records(
                [(current_timestamp, status_value)], phone_count_key
            )

    def query_status_statistics(self, from_phone: str, to_phone: str):
        phone_count_key = f"phone_count:{from_phone}:{to_phone}"
        special_statuses = {
            CallStatus.TRANSFER_TIMEOUT.value,
            CallStatus.HANG_UP_TIMEOUT.value,
            CallStatus.HANG_UP_DUE_TO_ABUSIVE_LANGUAGE.value,
        }
        special_status_count = 0

        try:
            with self._get_redis_client() as r:
                status_stats = r.hgetall(f"{phone_count_key}:status_count")

                logger.info(f"\nStatus Statistics ({from_phone} → {to_phone}):")
                if not status_stats:
                    logger.info("No statistics found.")
                else:
                    for status, count in status_stats.items():
                        decoded_status = status.decode()
                        decoded_count = int(count.decode())

                        logger.info(f"{decoded_status}: {decoded_count}")

                        if decoded_status in special_statuses:
                            special_status_count += decoded_count

                logger.info(f"\nTotal for selected statuses: {special_status_count}")
                return special_status_count

        except redis.RedisError as e:
            logger.error(f"Redis error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
        return 0

    def delete_phone_count(self, from_phone: str, to_phone: str):
        phone_count_key = f"phone_count:{from_phone}:{to_phone}"

        with self._get_redis_client() as r:
            all_calls = r.zrange(f"{phone_count_key}:calls", 0, -1)

            for call in all_calls:
                timestamp = call.decode()
                status_key = f"{phone_count_key}:call_status:{timestamp}"
                r.delete(status_key)
                logger.info(f"Deleted Call Record: Timestamp {timestamp}")

            r.delete(f"{phone_count_key}:calls")
            r.delete(f"{phone_count_key}:status_count")
            logger.info("\nAll call records and statistics deleted.")

    def _log_inserted_records(self, records, phone_count_key):
        with self._get_redis_client() as r:
            logger.info("Inserted Records:")
            for timestamp, status in records:
                logger.info(f"Timestamp: {timestamp}, Status: {status}")

            recent_calls = r.zrange(f"{phone_count_key}:calls", 0, -1)
            call_details = [
                (
                    int(call.decode()),
                    r.hget(
                        f"{phone_count_key}:call_status:{call.decode()}", "status"
                    ).decode(),
                )
                for call in recent_calls
            ]

            # logger.info("\nRecords in Redis:")
            # for call_time, status in call_details:
            #     readable_time = time.strftime(
            #         "%Y-%m-%d %H:%M:%S", time.localtime(call_time)
            #     )
            #     logger.info(f"Time: {readable_time}, Status: {status}")


if __name__ == "__main__":
    manager = CallRecordManager()

    try:
        # manager.delete_phone_count("+10000000000", "+13613488866")
        # manager.call_insert_random("+10000000000", "+13613488866")
        manager.query_status_statistics("+1000000000", "+13613488866")
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
