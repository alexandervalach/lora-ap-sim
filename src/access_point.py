import json

from lora import *


class AccessPoint:
    def __init__(self, id):
        self.id = id
        self.net_config = NET_CONFIG

    def generate_setr(self):
        message = {}
        message_body = {}
        lora_stand = {}

        message['message_name'] = MessageType.SETR.value
        message_body['id'] = self.id
        message_body['ver'] = LORA_VERSION
        message_body['m_chan'] = True
        message_body['channels'] = 8
        message_body['sup_freqs'] = FREQUENCIES
        message_body['sup_sfs'] = SPREADING_FACTORS
        message_body['sup_crs'] = CODING_RATES
        message_body['sup_bands'] = BANDS
        message_body['max_power'] = MAX_POWER

        lora_stand['name'] = "LoRa@FIIT"
        lora_stand['version'] = "1.0"

        message_body['lora_stand'] = lora_stand
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))

        return json_message

    def process_seta(self, message):
        print("Processing SETA message...\n")
        body = message['message_body']
        print("Body:")
        print(body)

    def process_reply(self, reply):
        try:
            message = json.loads(reply)
            message_name = message['message_name']

            if message_name == 'SETA':
                self.process_seta(message)
            else:
                print("Unknown message type")
        except ValueError:
            print("Could not deserialize JSON object")
