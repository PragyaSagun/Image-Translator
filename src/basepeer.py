from btpeer import BTPeer
from utils import *
import json
import random
from threading import Thread
import time


class BasePeer(BTPeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BTPeer.__init__(self, maxpeers, serverport)
        self.requests = set()
        self.name = name
        self.register_server = register_server
        self.ext_ip = None

        handlers = {
            "DISC": self.handle_discovery,
            "REGR": self.handle_register_reply,
            "DISR": self.handle_discovery_reply,
            "BINT": self.handle_forward,
            "BTCR": self.handle_forward,
            "TRSC": self.handle_forward,
            "INIT": self.handle_forward
        }
        # Add node types here
        self.node_types = {
            "translation": "TRANSLATION",
            "broker": "BROKER",
            "transcription": "TRANSCRIPTION",
            "interface": "INTERFACE"
        }
        # Add Message to node type mapping here
        self.message_node_mapping = {
            "TRAN": "TRANSLATION",
            "BTCR": "BROKER",
            "TRSC": "TRANSCRIPTION",
            "BINT": "BROKER"
        }
        self.registered = False
        self.peerType = {}
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_register_reply(self, peerconn, register_reply):
        self.registered = True
        print("I am ready to serve")
        register_reply = json.loads(register_reply)
        peerid, peeradd = register_reply["node_info"]
        if peerid == "unk":
            print("I am the first node in the P2P")
            return
        if register_reply["id"] in self.requests:
            return
        self.requests.add(register_reply["id"])
        peerhost, peerport = peeradd.split(":")
        msg = create_message(self.myid, self.name, self.myid,
                             random.randint(0, 1000000), "DISC", self.node_types[self.name])
        self.connectandsend(peerhost, peerport, "DISC", json.dumps(
            msg), pid=self.myid, waitreply=False)

    def handle_discovery(self, peerconn, discovery_message):
        """
        peerconn: PeerConnection instance.
        discovery_message: message data json encoded. Need to get json dump of message before read.
        """
        discovery_message = json.loads(discovery_message)
        # peerid = nodeid in createMessage, or self.name.
        # peeradd = nodeinfo in create message, self.myid
        # self.myid = '%s:%d' % (self.serverhost, self.serverport).
        peerid, peeradd = discovery_message["node_info"]
        peertype = discovery_message["ntype"]
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        for id in self.getpeerids():
            # Iterate though all peers and propogate discovery message of node.
            # Will forward message, not change content. So any reply goes direct to intial node.
            (host, port) = self.getpeer(id)
            self.connectandsend(host, port, "DISC", json.dumps(
                discovery_message), self.myid, waitreply=False)

        # Send reply to initial discovery message. e.g. Send DISR reply.
        reply = create_message(self.myid, self.name,
                               self.myid, random.randint(0, 1000000), "DISR", self.node_types[self.name])
        self.addpeer(peerconn, peeradd.split(":")[0], peeradd.split(":")[1])
        if peertype not in self.peerType:
            self.peerType[peertype] = set()
        self.peerType[peertype].add(peeradd)
        self.connectandsend(peeradd.split(":")[0], peeradd.split(
            ":")[1], "DISR", json.dumps(reply), self.myid, waitreply=False)

    def handle_discovery_reply(self, peerconn, discovery_reply_message):
        discovery_message = json.loads(discovery_reply_message)
        peerid, peeradd = discovery_message["node_info"]
        if discovery_message["id"] in self.requests:
            return
        self.requests.add(discovery_message["id"])
        print("Added peer {}".format(peerid))
        self.addpeer(peerconn, peeradd.split(":")[0], peeradd.split(":")[1])
        if discovery_message["ntype"] not in self.peerType:
            self.peerType[discovery_message["ntype"]] = set()
        self.peerType[discovery_message["ntype"]].add(peeradd)

    def handle_forward(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return
        self.requests.add(msg["id"])
        if self.message_node_mapping[msg["type"]] in self.peerType:
            nodelist = self.peerType[self.message_node_mapping[msg["type"]]]
            for node in nodelist:
                (host, port) = node.split(":")
                self.connectandsend(host, port, msg["type"], json.dumps(
                    msg), pid=self.myid, waitreply=False)
        else:
            for peerid in self.getpeerids():
                (host, port) = self.getpeer(peerid)
                self.connectandsend(host, port, msg["type"], json.dumps(
                    msg), pid=self.myid, waitreply=False)

    def register(self):
        while self.registered == False:
            host, port = self.register_server.split(":")
            if self.name == "broker":
                msg = create_message(self.myid, self.name, self.myid,
                                     random.randint(0, 100000), "REGS", "BROKER")
            if self.name == "interface":
                msg = create_message(self.myid, self.name, self.myid,
                                     random.randint(0, 100000), "REGS", "INTERFACE", ext_ip=self.ext_ip)
            if self.name == "transcription":
                msg = create_message(self.myid, self.name, self.myid,
                                     random.randint(0, 100000), "REGS", "TRANSCRIPTION")
            if self.name == "translation":
                msg = create_message(self.myid, self.name, self.myid,
                                     random.randint(0, 100000), "REGS", "TRANSLATION")
            cmp = json.dumps(msg)
            self.connectandsend(host, port, "REGS", cmp,
                                pid=self.myid, waitreply=False)
            time.sleep(5)

    def main(self):
        reg = Thread(target=self.register)
        reg.start()
        self.mainloop()
