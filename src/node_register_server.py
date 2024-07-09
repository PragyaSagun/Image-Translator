from btpeer import BTPeer
import json
from utils import *
from config import TRANSLATION_CONFIG
import random
import os


class RegisterationServer(BTPeer):
    def __init__(self, maxpeers, serverport):
        BTPeer.__init__(self, maxpeers, serverport)
        self.requests = set()
        handlers = {
            "TRAN": self.handle_forward,
            "ACKT": self.handle_forward,
            "DISC": self.handle_forward,
            "REGS": self.handle_register,
            "REGR": self.handle_forward,
            "BINT": self.handle_forward,
            "BTCR": self.handle_forward,
            "TRSC": self.handle_forward,
            "INIT": self.handle_forward
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])
        self.nodes = {}
        if os.path.exists('interface-info.txt'):
            os.remove('interface-info.txt')

    def handle_register(self, peerconn, registration_request):
        registration_request = json.loads(registration_request)
        id = registration_request["sender"]
        req = registration_request["id"]
        name, addr = registration_request["node_info"]
        host, port = addr.split(":")
        if registration_request["ntype"] == "INTERFACE":
            file = open("interface-info.txt", "a")
            line = registration_request["extip"]+":3000"+"\n"
            file.write(line)
            file.close()
        if req in self.requests:
            cmp = json.dumps(create_duplicate_response())
            self.connectandsend(host, port, "DUPL", cmp,
                                pid=self.myid, waitreply=False)
        else:
            self.requests.add(req)
            if len(self.nodes) == 0:
                node_id = "unk"
                node = "None"
            else:
                rand = random.randint(0, len(self.nodes))
                node_id = list(self.nodes.keys())[rand]
                node = self.nodes[node_id]
            self.nodes[name] = id
            cmp = json.dumps(create_message(
                self.myid, node_id, node, req, "REGR"))
            self.connectandsend(host, port, "REGR", cmp,
                                pid=self.myid, waitreply=False)

    def handle_forward(self, peerconn, forward_request):
        rand = random.randint(0, len(self.nodes))
        msg = json.loads(forward_request)
        if msg["id"] in self.requests:
            return
        self.requests.add(msg["id"])
        node_id = list(self.nodes.keys())[rand]
        host, port = self.nodes[node_id].split(":")
        self.connectandsend(
            host, port, msg["type"], forward_request, pid=self.myid, waitreply=False)

    def main(self):
        self.mainloop()


node = RegisterationServer(1000, TRANSLATION_CONFIG["regr"])
node.main()
