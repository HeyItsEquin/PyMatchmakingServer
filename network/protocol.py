import json
from enum import IntEnum
from typing import Any

class MessageType(IntEnum):
    PING = 0

class Message:
    message_type: MessageType
    message_contents: dict[Any, Any]

