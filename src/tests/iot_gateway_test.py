import requests
from datetime import datetime

iot_gateway_url = "https://rlt6g70pul.execute-api.eu-central-1.amazonaws.com/prod/message/"


def gatewayTes(topic, newMessageId):
    constructed_url = iot_gateway_url + topic
    headers = {
        'Content-type': 'application/json',
    }
    body = [
        {
            "nodeid": "localhost:114",
            "queue": 1,
            "newMessageId": newMessageId,
            "datetime": datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
        }
    ]

    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    print(response)


def main():
    gatewayTes("broker_interface", 1)
    gatewayTes("broker_transcriptor", 2)


main()
