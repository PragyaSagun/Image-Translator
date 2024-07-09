from basepeer import BasePeer
import requests
import json
from config import TRANSLATION_CONFIG, IOT_GATEWAY_CONFIG
from datetime import datetime
import random
from utils import *


b_interface_topic = IOT_GATEWAY_CONFIG["b_interface_topic"]
b_transcriptor_topic = IOT_GATEWAY_CONFIG["b_transcriptor_topic"]


class BrokerNode(BasePeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)
        self.iot_gateway_url = IOT_GATEWAY_CONFIG["url"]

        # Handlers defined for listining to messages.
        handlers = {
            "BINT": self.__handle_interface_broker_request,
            "BTCR": self.__handle_transcription_broker_request,
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def __handle_interface_broker_request(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.__update_iot(b_interface_topic, msg["id"])
        new_msg = create_transcription_request_message(random.randint(
            0, 1000000), msg["sender"], msg["region"], msg["requester"], msg["email"], msg["image"])
        # for peerid in self.getpeerids():
        #     (host, port) = self.getpeer(peerid)
        #     # Update message type, as going to transcription node.
        #     self.connectandsend(host, port, "TRSC",
        #                         json.dumps(new_msg), pid=self.myid, waitreply=False)
        self.handle_forward(peerconn, json.dumps(new_msg))

    def __handle_transcription_broker_request(self, peerconn, translation_request):
        msg = json.loads(translation_request)
        if msg["id"] in self.requests:
            return

        self.__update_iot(b_transcriptor_topic, msg["id"])
        new_msg = create_translation_request_message(random.randint(
            0, 1000000), msg["sender"], msg["region"], msg["requester"], msg["message"], msg["email"])
        # for peerid in self.getpeerids():
        #     (host, port) = self.getpeer(peerid)
        #     # Update message type, as going to transcription node.
        #     self.connectandsend(host, port, "TRAN",
        #                         json.dumps(new_msg), pid=self.myid, waitreply=False)
        self.handle_forward(peerconn, json.dumps(new_msg))

    def __update_iot(self, topic, newMessageId):
        """
        Will be called when a a broker node receives a message.
        Will publish message to differnet topics depending on if broker or transcription message.
        """
        constructed_url = self.iot_gateway_url + topic
        headers = {
            'Content-type': 'application/json',
        }
        body = [
            {
                "nodeid": self.myid,
                "queue": len(self.requests),
                "newMessageId": newMessageId,
                "datetime": datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
            }
        ]

        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        print(response)


node = BrokerNode(
    100, TRANSLATION_CONFIG["broker"], "broker", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()
