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
        self.pre_shared_key = PRE_SHARED_KEY

    def get_dev_id(self):
        return self.dev_id

    def generate_message(self, config_type):
        message = {}
        message_body = {}

        heart_rate = random.randint(MIN_HEART_RATE, MAX_HEART_RATE)

        # If critical heart rate values are present change message type
        if heart_rate < 60 or heart_rate > 145:
            config_type = 'emer'

        app_data = LoRa.get_data(heart_rate, self.battery_level)

        sf = self.net_config[config_type]['sf']
        band = self.net_config[config_type]['band']
        cr = self.net_config[config_type]['cr']
        power = self.net_config[config_type]['power']

        time = LoRa.calculate_time_on_air(len(app_data), sf, band, cr, 1)

        # Check if there is remaining duty cycle, additionally perform refresh
        self.set_remaining_duty_cycle(time)
        print(self.duty_cycle)
        if self.duty_cycle == 0:
            return None

        message_body['band'] = band
        message_body['cr'] = cr
        message_body['dev_id'] = self.dev_id
        message_body['power'] = power
        message_body['duty_c'] = self.duty_cycle
        message_body['rssi'] = LoRa.get_rssi()
        message_body['sf'] = sf
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time

        message['message_body'] = message_body

        if config_type == 'normal':
            message = self.generate_rxl(message, app_data)
        elif config_type == 'emer':
            message = self.generate_emer(message, app_data)
        elif config_type == 'reg':
            message = self.generate_regr(message, app_data)

        json_message = json.dumps(message, separators=(',', ':'), sort_keys=True)
        return json_message.encode('ascii')

    def generate_regr(self, message, app_data):
        message['message_name'] = MessageType.REGR.value
        message['message_body']['app_data'] = app_data
        message['message_body']['sh_key'] = self.pre_shared_key
        return message

    def generate_rxl(self, message, data):
        message['message_name'] = MessageType.RXL.value
        message['message_body']['ack'] = Acknowledgement.NO_ACK.value
        message['message_body']['conf_need'] = False
        message['message_body']['data'] = data
        message['message_body']['seq'] = self.seq
        self.seq += 1
        return message

    def generate_emer(self, message, data):
        message['message_name'] = MessageType.RXL.value
        message['message_body']['ack'] = Acknowledgement.MANDATORY.value
        message['message_body']['conf_need'] = False
        message['message_body']['data'] = data
        message['message_body']['seq'] = self.seq
        self.seq += 1
        return message

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
                    config_type = data['type'].lower()

                    print('Network Data Type: {0}'.format(data['type']))

                    if data['sf']:
                        self.net_config[config_type]['sf'] = data['sf']
                        print('SF set to {0} for node {1}'.format(data['sf'], self.dev_id))

                    if data['power']:
                        self.net_config[config_type]['power'] = data['power']
                        print('PWR set to {0} for node {1}'.format(data['power'], self.dev_id))

                    if data['cr']:
                        self.net_config[config_type]['cr'] = data['cr']
                        print('CR set to {0} for node {1}'.format(data['cr'], self.dev_id))

                    if data['band']:
                        self.net_config[config_type]['band'] = data['band']
                        print('BW set to {0} for node {1}'.format(data['band'], self.dev_id))

                    if data['freqs']:
                        self.net_config[config_type]['freqs'] = data['freqs']
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
                    config_type = data['type'].lower()

                    if data['sf']:
                        self.net_config[config_type]['sf'] = data['sf']
                        print('SF updated to {0} for node {1}'.format(data['sf'], self.dev_id))

                    if data['power']:
                        self.net_config[config_type]['power'] = data['power']
                        print('PWR updated to {0} for node {1}'.format(data['power'], self.dev_id))
        else:
            print("Different DEV_IDs:")
            print(dev_id, self.dev_id)

    def set_remaining_duty_cycle(self, time):
        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            print('Duty cycle refresh for node {0}'.format(self.dev_id))
            self.duty_cycle = DUTY_CYCLE

        if self.duty_cycle - time > 0:
            self.duty_cycle -= time
        else:
            self.seq += 1
