import json
import random

class EndNode:
    def generate_regr(self):
        message = {}
        message_body = {}

        message['message_name'] = 'REGR'
        message_body['band'] = 125000
        message_body['cr'] = "4/5"
        message_body['dev_id'] = "ALEX"
        message_body['power'] = 14
        message_body['duty_c'] = 36000
        message_body['rssi'] = self.rssi()
        message_body['sf'] = 9
        message_body['snr'] = self.snr()
        message_body['time'] = 15752
        message_body['app_data'] = 'TE9SQUZJSVQ='
        message_body['sh_key'] = '+/////v////7////+////wIAAAA='
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        # print(json_message)

        return json_message

    def generate_rxl(self, dev_id, seq):
        message = {}
        message_body = {}

        message['message_name'] = 'RXL'
        # UNSUPPORTED, VOLATILE, MANDATORY
        message_body['ack'] = 'UNSUPPORTED'
        message_body['band'] = 125000
        message_body['conf_need'] = False
        message_body['cr'] = "4/5"
        message_body['data'] = 'TE9SQUZJSVQ='
        message_body['dev_id'] = dev_id
        message_body['duty_c'] = 36000
        # message_body['power'] = 12
        message_body['rssi'] = self.rssi()
        message_body['seq'] = seq
        message_body['sf'] = 7
        message_body['snr'] = self.snr()
        message_body['time'] = 10024
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        # print(json_message)

        return json_message

    """ Randomly generated SNR values between 6.5 and 11.75"""
    def snr(self):
        return round(random.uniform(0,1) * 5.25 + 6.5, 2)

    """ Randomly generated RSSI values between -35 and -115"""
    def rssi(self):
        return round(random.uniform(0,1) * (-80) -35, 1)