from btpeer import *
from utils import *
import json
import base64


class TranslatorNode(BTPeer):
    def __init__(self, maxpeers, serverport, neighbourport, id, nid):
        BTPeer.__init__(self, maxpeers, serverport)
        self.region = "EU"
        self.requests = {}
        handlers = {
            "TRAN": self.translate,
            "ACKN": self.ack
        }
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

        # self.addpeer(nid,'localhost',neighbourport)

    def translate(self, peer, data):
        print("I am translating")

    def ack(self, peer, data):
        print(data["message"])

    def main(self):
        # TODO: When creating a translation  request should also give user email.
        # Only user interface will ever create a translation request.
        # data = create_translation_request_message(
        #    16, self.myid, "ES", self.myid, "I walk a lonely road and only one that I have ever known, dont know where it goes but its the only one I have ever known", "shiveshganju@gmail.com")
        image = open('pic3.gif', 'rb')  # open binary file in read mode
        image_read = image.read()
        image_64_encode = base64.encodebytes(image_read).decode("utf-8")
        data = create_transcription_request_message(
            23, self.myid, "IT", self.myid, "shiveshganju@gmail.com", image_64_encode)
        data = json.dumps(data)
        self.connectandsend('localhost', 1111, "TRSC",
                            data, pid=self.myid, waitreply=False)


a = TranslatorNode(100, 8888, 3333, "A", "D")
a.main()
# import json
# a = {
#     "x":"y",
#     "a":"B"
# }
# x=json.dumps(a)
# print(json.loads(x)['x'])
