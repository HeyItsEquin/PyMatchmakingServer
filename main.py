import argparse
import socket
from network import server
from network.socket import *
from uuid import *
from util import logging

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type")

args = parser.parse_args()

prog_type: str = args.type
prog_type = prog_type.lower()

if prog_type == "c" or prog_type == "client":
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect(("127.0.0.1", 8001))

    id = recv_all_data(tcp)

    uuid = UUID(id)

    logging.info(f"Assigned ID <{uuid}> by server")
    logging.info("Sending ACK response")

    tcp.send("ACK".encode())

    tcp.close()

if prog_type == "s" or prog_type == "server":
    s = server.Server()
    s.start()