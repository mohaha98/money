"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/8/14 17:31
文件名： redis_pub
功能作用： 
=================不积小流无以成江海=================="""
from redis import Redis
from datetime import datetime, timedelta

class RedisVerificationCodeManager:
    def __init__(self, host='192.168.26.124', port=6379, db=6):
        self.redis_client = Redis(host=host, port=port, db=db)

    def add_code(self, code, timestamp):
        self.redis_client.zadd('verification_codes', {code: timestamp})

    def get_codes_by_timestamp(self, min_timestamp, max_timestamp):
        codes = self.redis_client.zrangebyscore('verification_codes', min_timestamp, max_timestamp)
        return [code.decode('utf-8') for code in codes]


def get_timestamp(time):
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 将日期转换为时间戳（以秒为单位）
    timestamp = int(time.timestamp()* 1000)
    return timestamp

def get_now_time():
    return datetime.now()

def get_past_time(D,H,M,S):
    # 获取当前时间
    current_time = datetime.now()
    # 构造时间间隔
    time_delta = timedelta(days=D, hours=H, minutes=M, seconds=S)
    # 计算过去一天三小时10分10秒的时间
    past_time = current_time - time_delta
    return past_time


if __name__ == "__main__":
    time=get_past_time(1,12,23,12)
    print(get_timestamp(get_now_time()))

