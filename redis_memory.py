"""Save and load chat messages using the notebook's Redis list pattern."""
import json
import os

from dotenv import load_dotenv
from redis import Redis
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict

load_dotenv()
redis_client = Redis.from_url(
    os.environ['REDIS_URL'], decode_responses=True,
    socket_connect_timeout=10, socket_timeout=10,
)


def save_message(user_id, message):
    key = f'hopscotch:chat:{user_id}:messages'
    redis_client.lpush(key, json.dumps(message_to_dict(message)))


def load_history(user_id):
    key = f'hopscotch:chat:{user_id}:messages'
    stored_messages = redis_client.lrange(key, 0, -1)
    # LPUSH stores newest first. The model needs oldest first.
    stored_messages.reverse()
    message_dicts = [json.loads(message) for message in stored_messages]
    history = InMemoryChatMessageHistory()
    history.add_messages(messages_from_dict(message_dicts))
    return history
