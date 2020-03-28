import json

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
        message_body['rssi'] = -57.0
        message_body['sf'] = 9
        message_body['snr'] = 10.75
        message_body['time'] = 15752
        message_body['app_data'] = 'TE9SQUZJSVQ='
        message_body['sh_key'] = '+/////v////7////+////wIAAAA='
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        print(json_message)

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
        message_body['rssi'] = -67.0
        message_body['seq'] = seq
        message_body['sf'] = 7
        message_body['snr'] = 12.75
        message_body['time'] = 10024
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        print(json_message)

        return json_message