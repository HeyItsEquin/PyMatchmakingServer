from client.client import Client
from util import logging
from util.config import CFG
from uuid import UUID
from network.protocol import Address

class ClientManager:
    clients: dict[UUID, Client]

    def __init__(self):
        self.clients = {}

    def add_client(self, client: Client):
        if client.id in self.clients:
            return False
        self.clients[client.id] = client
        return True

    def remove_client(self, client: Client):
        if client.id not in self.clients:
            return False
        del self.clients[client.id]
        return True
    
    def get_client_by_addr(self, addr: Address):
        for client in self.clients.values():
            if client.addr == addr:
                return client
        return None