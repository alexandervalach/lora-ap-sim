import json

from lora import *


class EndNode:
    def __init__(self, dev_id, seq=1):
        self.dev_id = dev_id
        self.seq = seq
        self.battery_level = BATTERY_FULL
        self.duty_cycle = DUTY_CYCLE
        self.is_mobile = False
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_current_time()

    def get_dev_id(self):
        return self.dev_id

    def generate_regr(self):
        message = {}
        message_body = {}

        app_data = LoRa.get_data()
        time = LoRa.get_time(len(app_data))

        if self.calculate_duty_cycle(time) is None:
            return None

        message_body['band'] = self.net_config['reg']['band']
        message_body['cr'] = self.net_config['reg']['cr']
        message_body['dev_id'] = self.dev_id
        message_body['power'] = self.net_config['reg']['power']
        message_body['duty_c'] = self.duty_cycle
        message_body['rssi'] = LoRa.get_rssi()
        message_body['sf'] = self.net_config['reg']['sf']
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time
        message_body['app_data'] = app_data
        message_body['sh_key'] = PRE_SHARED_KEY

        message['message_name'] = MessageType.REGR.value
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'))
        return json_message

    def generate_rxl(self):
        message = {}
        message_body = {}
        heart_rate = random.randint(MIN_HEART_RATE, MAX_HEART_RATE)

        if heart_rate < 60 or heart_rate > 145:
            return self.generate_emer(heart_rate)

        data = LoRa.get_data(heart_rate, self.battery_level)
        time = LoRa.get_time(len(data))

        if self.calculate_duty_cycle(time) is None:
            return None

        message_body['ack'] = Acknowledgement.NO_ACK.value
        message_body['band'] = self.net_config['normal']['band']
        message_body['conf_need'] = False
        message_body['cr'] = self.net_config['normal']['cr']
        message_body['data'] = data
        message_body['dev_id'] = self.dev_id
        message_body['duty_c'] = self.duty_cycle
        message_body['power'] = self.net_config['normal']['power']
        message_body['rssi'] = LoRa.get_rssi()
        message_body['seq'] = self.seq
        message_body['sf'] = self.net_config['normal']['sf']
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time

        message['message_name'] = MessageType.RXL.value
        message['message_body'] = message_body

        self.seq += 1

        json_message = json.dumps(message, separators=(',', ':'))
        return json_message

    def generate_emer(self, heart_rate):
        message = {}
        message_body = {}

        data = LoRa.get_data(heart_rate, self.battery_level)
        time = LoRa.get_time(len(data))

        if self.calculate_duty_cycle(time) is None:
            return None

        message_body['ack'] = Acknowledgement.MANDATORY.value
        message_body['band'] = self.net_config['emer']['band']
        message_body['conf_need'] = False
        message_body['cr'] = self.net_config['emer']['cr']
        message_body['data'] = data
        message_body['dev_id'] = self.dev_id
        message_body['duty_c'] = self.duty_cycle
        message_body['power'] = self.net_config['emer']['power']
        message_body['rssi'] = LoRa.get_rssi()
        message_body['seq'] = self.seq
        message_body['sf'] = self.net_config['emer']['sf']
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time

        message['message_name'] = MessageType.RXL.value
        message['message_body'] = message_body

        self.seq += 1

        json_message = json.dumps(message, separators=(',', ':'))
        return json_message

    def process_reply(self, reply):
        try:
            if reply is not None:
                # First { is doubled for unknown reason, remove it
                reply = reply[1:]
                message = json.loads(reply)
                message_name = message['message_name']

                if message_name == 'REGA':
                    self.process_rega(message)
                elif message_name == 'TXL':
                    self.process_txl(message)
                else:
                    print("Unknown message type")
        except ValueError:
            print("Could not deserialize JSON object")
        except TypeError:
            print("TypeError")

    def process_rega(self, message):
        print('Processing REGA message for node {0}...'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            if body['app_data']:
                app_data = body['app_data']

            if body['net_data']:
                net_data = body['net_data']

                for data in net_data:
                    net_config_type = data['type'].lower()

                    print('Network Data Type: {0}'.format(data['type']))

                    if data['sf']:
                        self.net_config[net_config_type]['sf'] = data['sf']
                        print('SF set to {0} for node {1}'.format(data['sf'], self.dev_id))

                    if data['power']:
                        self.net_config[net_config_type]['power'] = data['power']
                        print('PWR set to {0} for node {1}'.format(data['power'], self.dev_id))

                    if data['cr']:
                        self.net_config[net_config_type]['cr'] = data['cr']
                        print('CR set to {0} for node {1}'.format(data['cr'], self.dev_id))

                    if data['band']:
                        self.net_config[net_config_type]['band'] = data['band']
                        print('BW set to {0} for node {1}'.format(data['band'], self.dev_id))

                    if data['freqs']:
                        self.net_config[net_config_type]['freqs'] = data['freqs']
                        print('FREQS set for node {1}'.format(data['freqs'], self.dev_id))
        else:
            print("Different DEV_IDs:")
            print(dev_id, self.dev_id)

    def process_txl(self, message):
        print('Processing TXL message for node {0}...'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            if body['app_data']:
                app_data = body['app_data']

            if body['net_data']:
                net_data = body['net_data']

                for data in net_data:
                    net_config_type = data['type'].lower()

                    if data['sf']:
                        self.net_config[net_config_type]['sf'] = data['sf']
                        print('SF updated to {0} for node {1}'.format(data['sf'], self.dev_id))

                    if data['power']:
                        self.net_config[net_config_type]['power'] = data['power']
                        print('PWR updated to {0} for node {1}'.format(data['power'], self.dev_id))
        else:
            print("Different DEV_IDs:")
            print(dev_id, self.dev_id)

    def calculate_duty_cycle(self, time):
        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            print('Duty cycle refresh for node {0}'.format(self.dev_id))
            self.duty_cycle = DUTY_CYCLE

        if self.duty_cycle - time > 0:
            self.duty_cycle -= time
            return 0
        else:
            self.seq += 1
            return None
