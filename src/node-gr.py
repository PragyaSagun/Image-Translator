from utils import *
import os
import requests
import uuid
import json
from config import TRANSLATION_CONFIG
from threading import Thread
import random
import smtplib
import ssl
from basepeer import BasePeer


class TranslatorNode(BasePeer):
    def __init__(self, maxpeers, serverport, name, register_server):
        BasePeer.__init__(self, maxpeers, serverport, name, register_server)
        self.region = "GR"
        handlers = {
            "TRAN": self.handle_translate
        }
        self.registered = False
        for m_type in handlers.keys():
            self.addhandler(m_type, handlers[m_type])

    def handle_translate(self, peerconn, translation_request):
        translation_request = json.loads(translation_request)
        if translation_request["id"] in self.requests:
            return
        if self.region != translation_request["region"]:
            # for peerid in self.getpeerids():
            #     (host, port) = self.getpeer(peerid)
            #     self.connectandsend(host, port, "TRAN", json.dumps(
            #         translation_request), pid=self.myid, waitreply=False)
            # return
            self.handle_forward(peerconn, json.dumps(translation_request))
            return
        self.requests.add(translation_request["id"])
        host, port, text = translation_request['requester'].split(
            ":")[0], translation_request['requester'].split(":")[1], translation_request['message']
        translated_text = self.translate(text)
        self.send_email(translated_text, json.dumps(
            translation_request["email"]))

    def translate(self, text):
        subscription_key = 'bfcfe92f1fa842e6a5cf95f622345b2c'
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        path = '/translate?api-version=3.0'
        params = '&from=en&to=de'
        constructed_url = endpoint + path + params
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': 'eastus',
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{
            'text': text
        }]
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        print(response)
        return response[0]['translations'][0]['text']

    def send_email(self, translated_text, email):
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "imagetranslator214@gmail.com"
        password = "translateImage"
        receiver_email = email
        context = ssl.create_default_context()
        message = """\
    Subject: Request Ready

    Your translated text is : """ + translated_text
        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email,
                            message.encode('utf-8'))
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()


node = TranslatorNode(
    100, TRANSLATION_CONFIG["gr"], "translation", 'localhost:'+str(TRANSLATION_CONFIG["regr"]))
node.main()
