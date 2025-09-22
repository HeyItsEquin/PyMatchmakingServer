from enum import IntEnum
from uuid import UUID
import socket
import json

Address = type[tuple[str, int]]

class MessageType(IntEnum):
    CONNECT = 0,
    ACK = 1,
    SYN = 2,
    VERIFIED = 3,
    REJECTED = 4,

    IDENTITY = 5,
    DISCONNECT = 6,

    ANONTEST = 7,
    CLIENTLIST = 8

UnverifiedOkMessageType = [
    MessageType.ANONTEST,
    MessageType.CLIENTLIST
]

class MessageHeader:
    type: MessageType
    name: str
    id: UUID | int
    
    def __init__(self):
        self.id = -1

class Message:
    header: MessageHeader
    body: any

    def __init__(self):
        self.header = MessageHeader()
        self.body = {}
        self.header.name = ""
        self.header.id = -1

    def __str__(self):
        str = f"Type: {MessageType(self.header.type).name}\nName: {self.header.name}\nUUID: {self.header.id}\n"
        json_str = json.dumps(self.body, indent=4)
        return str + json_str

    def __bytes__(self):
        return self.encode()

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
        if "id" in json_header: header.id = UUID(json_header["id"])
        else: header.id = -1

        message.body = json_body
        message.header = header

        return message
        
    def encode(self, encoding = "utf-8"):
        header_dict = {
            "type": self.header.type,
            "name": self.header.name
        }
        
        if self.header.id != -1:
            header_dict["id"] = self.header.id.__str__()

        json_header = json.dumps(header_dict)
        json_body = json.dumps(self.body)

        str = f"{json_header}\r\n{json_body}\0"

        return str.encode(encoding)

    def send(self, sock):
        sock.sendall(self.encode())

    def sendto(self, sock: socket.socket, addr: Address):
        if sock.fileno == -1:
            e = OSError("Socket is closed")
            e.errno = 10038
            raise e
        sock.sendto(self.encode(), addr)