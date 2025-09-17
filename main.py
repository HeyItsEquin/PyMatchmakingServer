from network.protocol import *

msg = Message()
msg.header = MessageHeader()
msg.header.type = MessageType.CONNECT
msg.header.name = "Equin :3"
msg.header.id = uuid4()
msg.body = {"message": "Hello, world!"}

print(msg.encode().decode())