import json

from lora import *


class EndNode:
    def __init__(self, dev_id, seq=1, sf=SpreadingFactors.SF7.value, power=Power.PW14.value):
        self.dev_id = dev_id
        self.seq = seq
        self.sf = sf
        self.power = power

    def generate_regr(self):
        message = {}
        message_body = {}

        app_data = LoRa.get_data()

        message['message_name'] = MessageType.REGR.value
        message_body['band'] = Bandwidth.BW125.value
        message_body['cr'] = CodingRates.CR45.value
        message_body['dev_id'] = self.dev_id
        message_body['power'] = self.power
        message_body['duty_c'] = DUTY_CYCLE
        message_body['rssi'] = LoRa.get_rssi()
        message_body['sf'] = self.sf
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = LoRa.get_time(len(app_data))
        message_body['app_data'] = app_data
        message_body['sh_key'] = PRE_SHARED_KEY
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        print(json_message)
        return json_message

    def generate_rxl(self):
        message = {}
        message_body = {}

        data = LoRa.get_data()

        message['message_name'] = MessageType.RXL.value
        message_body['ack'] = Acknowledgement.NO_ACK.value
        message_body['band'] = Bandwidth.BW125.value
        message_body['conf_need'] = False
        message_body['cr'] = CodingRates.CR45.value
        message_body['data'] = data
        message_body['dev_id'] = self.dev_id
        message_body['duty_c'] = DUTY_CYCLE
        message_body['power'] = self.power
        message_body['rssi'] = LoRa.get_rssi()
        message_body['seq'] = self.seq
        message_body['sf'] = self.sf
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = LoRa.get_time(len(data))
        message['message_body'] = message_body

        self.seq += 1

        json_message = json.dumps(message, separators=(',', ':'))
        print(json_message)
        return json_message
