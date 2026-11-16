
import os
import json
import redis
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

def check_redis():
    return redis_client.ping()


def get_history(session_id: str):

    key = f"chat:{session_id}"

    messages = redis_client.lrange(key, 0, -1)

    return [json.loads(message) for message in messages]


def save_message(session_id: str, role: str, content: str):

    key = f"chat:{session_id}"

    message = {
        "role": role,
        "content": content
    }

    redis_client.rpush(key, json.dumps(message))

    redis_client.expire(key, 86400)


def clear_history(session_id: str):

    redis_client.delete(f"chat:{session_id}")
