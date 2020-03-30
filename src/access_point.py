import json


class AccessPoint:
    def __init__(self, id):
        self.id = id

    def generate_setr(self):
        message = {}
        message_body = {}
        lora_stand = {}

        message['message_name'] = 'SETR'
        message_body['id'] = self.id
        message_body['ver'] = "1.0"
        message_body['m_chan'] = True
        message_body['channels'] = 8
        message_body['sup_freqs'] = [863000000, 100000, 870000000]
        message_body['sup_sfs'] = [7, 8, 9, 10, 11, 12]
        message_body['sup_crs'] = ["4/5", "4/6", "4/7", "4/8"]
        message_body['sup_bands'] = [500000, 250000, 125000]
        message_body['max_power'] = 14

        lora_stand['name'] = "LoRa@FIIT"
        lora_stand['version'] = "1.0"

        message_body['lora_stand'] = lora_stand
        message['message_body'] = message_body

        return json.dumps(message, separators=(',', ':'))