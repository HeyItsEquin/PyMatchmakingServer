from enum import IntEnum
from uuid import *
import json

class MessageType(IntEnum):
    PING = 0,
    CONNECT = 1,
    ACK = 2

class MessageHeader:
    type: MessageType
    name: str
    id: UUID

class Message:
    header: MessageHeader
    body: any

    def __init__(self):
        self.header = MessageHeader()
        self.body = {}

    def __str__(self):
        str = f"Type: {MessageType(self.header.type).name}\nName: {self.header.name}\nUUID: {self.header.id}\n"
        json_str = json.dumps(self.body, indent=4)
        return str + json_str

    @staticmethod
    def from_string(msg: str) -> "Message":
        message = Message()

        parts = msg.split("\r\n")

        r_header = parts[0]
        r_body = parts[1]

        json_header = json.loads(r_header)
        json_body = json.loads(r_body)

        header = MessageHeader()
        header.type = json_header["type"]
        header.name = json_header["name"]
        if "id" in json_header: header.id = json_header["id"] 

        message.body = json_body
        message.header = header

        return message
        
    def encode(self, encoding = "utf-8"):
        header_dict = {
            "type": self.header.type,
            "name": self.header.name,
            "id": self.header.id.__str__()
        }

        json_header = json.dumps(header_dict)
        json_body = json.dumps(self.body)

        str = f"{json_header}\r\n{json_body}"

        return str.encode(encoding)
