import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Use 'redis_cache' if in Docker, 'localhost' if testing on Ubuntu directly
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

# decode_responses=True means you get back strings, not raw bytes
cache = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
