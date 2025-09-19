import socket
import threading
import time
from client.client import Client
from client.manager import ClientManager
from network.socket import recv_all_data, recv_all_data_udp
from network.protocol import Message, MessageType
from uuid import UUID, uuid4
from util import logging
from concurrent.futures import ThreadPoolExecutor

class Server:
    tcp: socket.socket
    udp: socket.socket

    listening: bool

    tcp_thread: threading.Thread
    udp_thread: threading.Thread

    tcp_thread_pool: ThreadPoolExecutor
    udp_thread_poll: ThreadPoolExecutor

    manager: ClientManager

    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_thread = threading.Thread(target=self.handle_tcp_listen)
        self.udp_thread = threading.Thread(target=self.handle_udp_connection)
        self.tcp_thread_pool = ThreadPoolExecutor()
        self.udp_thread_poll = ThreadPoolExecutor()
        self.manager = ClientManager()

    def __stall(self):
        while self.listening:
            try:
                time.sleep(0.025)
            except KeyboardInterrupt:
                break

    def __cleanup(self):
        try:
            logging.info("Closing server sockets")
            self.tcp.close()
            self.udp.close()
        except Exception as e:
            logging.error(f"Error during server cleanup: {e}")

    def handle_message_identity(self, msg: Message, client: Client):
        pass

    def init_tcp_handshake(self, sock):
        logging.info("Received <CONNECT> request from client", True)
        cl_id = uuid4()
        logging.info(f"Authenticating client with UUID <{cl_id}>")
        logging.info("Sending <SYN> response with ID", True)
        res = Message()
        res.header.type = MessageType.SYN
        res.header.name = "<SERVER>"
                    
        res.body["assigned"] = cl_id.__str__()
            
        res.send(sock)

        logging.info("Awaiting <ACK> response from client", True)
            
        buf = recv_all_data(sock)
        msg = Message.from_string(buf)
            
        if msg.header.type != MessageType.ACK:
            logging.error("Did not receive message type <ACK> from client")
            sock.close()
            return None
            
        if msg.header.id != cl_id:
            logging.error("ID mismatch in <ACK> response from client")
            logging.error(f"Expected UUID <{cl_id}>; received <{msg.header.id}>")
            res = Message()
            res.header.type = MessageType.REJECTED
            res.header.name = "<SERVER>"
                
            res.send(sock)
            sock.close()
            return None
            
        logging.info("Received <ACK> response from client; Authentication success", True)
            
        res = Message()
        res.header.type = MessageType.VERIFIED
        res.header.name = "<SERVER>"
            
        res.send(sock)
        
        logging.info("Informed client of verification")
        
        return cl_id

    def handle_tcp_connection(self, sock, addr):
        try:
            v_success: UUID | None = self.init_tcp_handshake(sock)
        except Exception as e:
            logging.error(f"TCP handshake failed: {e}")
            v_success = None
        if not v_success:
            logging.error(f"TCP handshake failed")
            return
        
        cl = Client()
        cl.id = v_success
        cl.addr = addr
        self.manager.add_client(cl)
        
    def handle_tcp_listen(self):
        try:
            logging.info("Server TCP socket bound and listening at 127.0.0.1:8001")
            while self.listening:
                self.tcp.listen()
                try:
                    cl_sock, cl_addr = self.tcp.accept()
                except OSError as e:
                    if e.errno == 10038:
                        break
                    else:
                        logging.error("Error accepting new incoming connecton on TCP socket")
                logging.info(f"Accepting new incoming connection ({cl_addr[0]}:{cl_addr[1]})")

                buf = recv_all_data(cl_sock)
                msg = Message.from_string(buf)
                
                if msg.header.type != MessageType.CONNECT and msg.header.type != MessageType.ACK:
                    logging.error("Did not receive message type <CONNECT> from client on TCP socket")
                    cl_sock.close()
                    continue
                
                if msg.header.type == MessageType.ACK:
                    logging.error("Received message type <ACK> but no handshake was initialized")
                    cl_sock.close()
                    continue

                self.tcp_thread_pool.submit(self.handle_tcp_connection, cl_sock, cl_addr)
        except ConnectionError as e:
            logging.error(f"Connection error occurred: {e}")
        except OSError as e:
            if e.errno == 98:
                logging.error("TCP socket address is already in use, please try again later")
            if e.errno == 10038:
                return
            else:
                logging.error(f"Something went wrong with the TCP socket: {e}")
        except KeyboardInterrupt:
            self.listening = False
        except Exception as e:
            logging.error(f"Error in TCP listening thread: {e}")

    def handle_udp_request(self, data):
        try:
            msg = Message.from_string(data)
            if not msg.header.id or msg.header.id == -1:
                logging.warn("Received UDP message without valid UUID, discarding")
                return
            if msg.header.id not in self.clients:
                logging.warn(f"Received UDP message from unknown client, discarding")
                return
            client = self.clients[msg.header.id]
            if msg.header.type == MessageType.IDENTITY:
                self.handle_message_identity(msg, client)
        except Exception as e:
            logging.error(f"Something went wrong parsing UDP request: {e}")

    def handle_udp_connection(self):
        try:
            while True:
                dat, addr = recv_all_data_udp(self.udp)
                if not dat:
                    continue
                self.udp_thread_poll.submit(self.handle_udp_request, dat, addr)
        except Exception as e:
            logging.error(f"Something went wrong trying to parse UDP request: {e}")

    def start(self):
        try:
            self.tcp.bind(("127.0.0.1", 8001))
            self.listening = True
            self.tcp_thread.start()
            self.udp_thread.start()

            self.__stall()
            self.__cleanup()
        except Exception as e:
            logging.error(f"Something went wrong starting the server: {e}")
            self.__cleanup()