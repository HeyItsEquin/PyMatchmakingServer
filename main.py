import argparse
from network import server
from network.socket import *
from network.protocol import *
from client.client import *
from uuid import *
from util.config import *
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type")
parser.add_argument("-v", "--verbose", action='store_true')
parser.add_argument("-n", "--name", required=False)

args = parser.parse_args()

prog_type: str = args.type
prog_type = prog_type.lower()
verbose: bool = args.verbose
name: str = args.name

if not name:
    name = "Equin :3"

if verbose:
    CFG["verbose"] = True

def __stall():
    try:
        while True:
            sleep(0.025)
    except KeyboardInterrupt:
        return

if prog_type == "c" or prog_type == "client":
    cl = Client()
    cl.connect()
    __stall()
    cl.cleanup()

if prog_type == "s" or prog_type == "server":
    s = server.Server()
    s.start()