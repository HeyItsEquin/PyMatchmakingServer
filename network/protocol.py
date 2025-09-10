import json
from enum import IntEnum
from typing import Any

class MessageType(IntEnum):
    PING = 0
    T1 = 1
    T2 = 3
    T3 = 4

class Message:
    message_type: MessageType
    message_contents: dict[Any, Any]

    @staticmethod
    def from_str(str: str) -> "Message":
        try:
            msg = Message
            
            parts = str.split("\r\n")
            
            r_type = int(parts[0])
            r_content = parts[1]
            
            type = MessageType(r_type)
            content = json.loads(r_content)
            
            msg.message_type = type
            msg.message_contents = content
            
            return msg
        except ValueError as e:
            print("Malformed message body. Message type is not valid")
            return None
        except Exception as e:
            print("An exception occurred while parsing message, likely malformed")
            return None        