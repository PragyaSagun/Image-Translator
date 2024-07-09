from utils import *
import os
import json
from config import TRANSCRIPTION_PORT, TRANSLATION_CONFIG
import random
from basepeer import BasePeer
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import base64


class TranscriptionNode(BasePeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)
        self.img_number = 0
        handlers = {
            "TRSC": self.handle_transript
        }
        self.registered = False
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_transript(self, peerconn, transcription_request):
        transcription_request = json.loads(transcription_request)
        if transcription_request["id"] in self.requests:
            return

        self.requests.add(transcription_request["id"])
        encoded_img = transcription_request["image"]
        extracted_text = str(self.transcript(encoded_img))
        translation_request = create_translation_request_message(random.randint(
            0, 100000), self.myid, transcription_request["region"], transcription_request["requester"], extracted_text, transcription_request["email"], m_type="BTCR")

        # for peerid in self.getpeerids():
        #     (host, port) = self.getpeer(peerid)
        #     self.connectandsend(host, port, "TRAN", json.dumps(
        #         translation_request), pid=self.myid, waitreply=False)
        self.handle_forward(peerconn, json.dumps(translation_request))

    def transcript(self, encoded_img):
        subscription_key = "cd154ff8fedd40cf8cb02bada9cdce69"
        endpoint = "https://cloudprojectcv.cognitiveservices.azure.com/"
        computervision_client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(subscription_key))
        image_64_decode = base64.decodebytes(encoded_img.encode("utf-8"))
        img_name = 'image_'+str(self.img_number)+".png"
        self.img_number += 1
        image_result = open(img_name, 'wb')
        image_result.write(image_64_decode)
        local_image_printed_text_path = img_name
        local_image_printed_text = open(local_image_printed_text_path, "rb")
        ocr_result_local = computervision_client.recognize_printed_text_in_stream(
            local_image_printed_text)
        sentence = ""
        for region in ocr_result_local.regions:
            for line in region.lines:
                for word in line.words:
                    sentence += word.text + " "
                sentence += "  "
        if os.path.exists(img_name):
            os.remove(img_name)
        return sentence


node = TranscriptionNode(
    100, TRANSCRIPTION_PORT, "transcription", 'localhost:'+str(TRANSLATION_CONFIG["regr"]))
node.main()
