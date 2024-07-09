from basepeer import BasePeer
import requests
import json
from config import TRANSLATION_CONFIG
from utils import create_translation_request_message, create_transcription_request_message
import urllib.request
import json


class InterfaceNode(BasePeer):
    """
    Needs to handle following incoming requests:

    Incoming request:
    * Handle incoming request made from interface web server. Then create meassage and send to broker node.
    """

    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)

        # Handlers defined for listining to messages.
        handlers = {
            "INIT": self.__handle_interface_initial_request,
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])
        data = json.loads(urllib.request.urlopen(
            "http://ip.jsontest.com/").read())
        self.ext_ip = data["ip"]

    def __handle_interface_initial_request(self, peerconn, init_request):
        msg = json.loads(init_request)
        if msg["id"] in self.requests:
            return

        new_message = create_transcription_request_message(
            msg["id"], self.myid, msg["region"], self.myid, msg["email"], msg["encodedImage"], m_type="BINT")

        # for peerid in self.getpeerids():
        #     (host, port) = self.getpeer(peerid)
        #     self.connectandsend(host, port, "BINT", json.dumps(
        #         new_message), pid=self.myid, waitreply=False)
        self.handle_forward(peerconn, json.dumps(new_message))


node = InterfaceNode(
    100, TRANSLATION_CONFIG["interface"], "interface", 'localhost:' + str(TRANSLATION_CONFIG["regr"]))
node.main()
