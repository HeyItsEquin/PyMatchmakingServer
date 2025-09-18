import argparse
from network import server
from network.socket import *
from network.protocol import *
from network.client import *
from uuid import *

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type")

args = parser.parse_args()

prog_type: str = args.type
prog_type = prog_type.lower()

if prog_type == "c" or prog_type == "client":
    cl = Client()
    cl.connect()

if prog_type == "s" or prog_type == "server":
    s = server.Server()
    s.start()