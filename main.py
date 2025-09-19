import argparse
from network import server
from network.socket import *
from network.protocol import *
from network.client import *
from uuid import *
from util.config import *

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type")
parser.add_argument("-v", "--verbose", action='store_true')

args = parser.parse_args()

prog_type: str = args.type
prog_type = prog_type.lower()
verbose: bool = args.verbose

if verbose:
    CFG["verbose"] = True


if prog_type == "c" or prog_type == "client":
    cl = Client()
    cl.connect("Equin :3")
    cl.cleanup()

if prog_type == "s" or prog_type == "server":
    s = server.Server()
    s.start()