from client.client import Client
from util import logging
from util.config import CFG
from uuid import UUID
from network.protocol import Address
from typing import overload

ClientList = dict[UUID, Client]

class ClientManager:
    clients: ClientList

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
        
    @overload
    def client_exists(self, id: UUID):
        return id in self.clients
    
    @overload
    def client_exists(self, addr: Address):
        for client in self.clients.values():
            if client.addr == addr:
                return True
        return False