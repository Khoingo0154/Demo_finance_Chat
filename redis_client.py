# """Redis client singleton"""
# import redis
# from config import REDIS_HOST, REDIS_PORT, REDIS_DB

# class RedisClient:
#     _instance = None
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             try:
#                 cls._instance.client = redis.Redis(
#                     host=REDIS_HOST,
#                     port=REDIS_PORT,
#                     db=REDIS_DB,
#                     decode_responses=True
#                 )
#                 cls._instance.client.ping()
#                 print("✅ Đã kết nối Redis thành công")
#             except Exception as e:
#                 print(f"⚠️  Không thể kết nối Redis: {e}")
#                 cls._instance.client = None
#         return cls._instance
    
#     def get_client(self):
#         return self.client

# redis_client = RedisClient().get_client()

#------------------------------------------------------------------------------------------------

import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
                client.ping()
                cls._instance.client = client
                print("✅ Đã kết nối Redis thành công")
            except Exception as e:
                # FIX: không raise ở đây để app vẫn có thể chạy local (fallback)
                print(f"⚠️  Không thể kết nối Redis: {e}")
                cls._instance.client = None
        return cls._instance

    def get_client(self):
        return self.client


# Export redis_client (có thể là None nếu không kết nối)
redis_client = RedisClient().get_client()