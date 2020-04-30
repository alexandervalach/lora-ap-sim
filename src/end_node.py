import json
import random

from lora import BATTERY_FULL
from lora import DUTY_CYCLE
from lora import NET_CONFIG
from lora import LoRa
from lora import PRE_SHARED_KEY
from lora import REG_FREQUENCIES
from lora import MIN_HEART_RATE
from lora import MAX_HEART_RATE
from lora import MessageType
from lora import Acknowledgement


class EndNode():
    def __init__(self, dev_id, conn, register_node=True, seq=1):
        self.dev_id = dev_id
        self.seq = seq
        self.battery_level = BATTERY_FULL
        self.duty_cycle = DUTY_CYCLE
        self.is_mobile = False
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_current_time()
        self.pre_shared_key = PRE_SHARED_KEY
        self.freq = REG_FREQUENCIES[0]
        self.conn = conn
        self.last_downlink_toa = 0

        if register_node:
            self.send_message('reg')

    def get_dev_id(self):
        return self.dev_id

    def pop_last_downlink_toa(self):
        toa = self.last_downlink_toa
        self.last_downlink_toa = 0
        return toa

    def send_message(self, message_type='normal'):
        message = self.generate_message(message_type)

        if message is not None:
            reply = self.conn.send_data(message)
            if reply is not None:
                self.last_downlink_toa = self.process_reply(reply)
        else:
            print("{0}: expired duty cycle".format(self.dev_id))

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
        freq = self.net_config[config_type]['freqs'][0]

        time = LoRa.calculate_time_on_air(len(app_data), sf, band, cr, 1)

        # Check if there is remaining duty cycle, additionally perform refresh
        self.set_remaining_duty_cycle(time)
        # print(self.duty_cycle)
        if self.duty_cycle == 0:
            return None

        message_body['freq'] = freq
        message_body['band'] = band
        message_body['cr'] = cr
        message_body['dev_id'] = self.dev_id
        message_body['power'] = power
        message_body['duty_c'] = self.duty_cycle
        message_body['rssi'] = LoRa.get_rssi()
        message_body['sf'] = sf
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time
        message_body['type'] = config_type

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
        message['message_body']['ack'] = Acknowledgement.OPTIONAL.value
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
                # First '{' is doubled for unknown reason, let's remove it
                reply = reply[1:]
                message = json.loads(reply)
                message_name = message['message_name']

                if message_name == 'REGA':
                    return self.process_rega(message)
                elif message_name == 'TXL':
                    return self.process_txl(message)
                else:
                    print("Unknown message type")
                    return 0
        except ValueError:
            print("Could not deserialize JSON object")
            return 0
        except TypeError:
            print("TypeError")
            return 0

    def process_rega(self, message):
        print('Processing REGA message for node {0}...'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            # No support for app_data
            # if body['app_data']:
            # app_data = body['app_data']

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
                        print('FREQS {0} set for node {1}'.format(data['freqs'], self.dev_id))
        else:
            print("Different DEV_IDs:")
            print(dev_id, self.dev_id)

        try:
            return body['time']
        except KeyError:
            return 0

    def process_txl(self, message):
        print('Processing TXL message for node {0}...'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            # NO support for downlink app_data
            # if body['app_data']:
            # app_data = body['app_data']

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

        try:
            return body['time']
        except KeyError:
            return 0

    def set_remaining_duty_cycle(self, time):
        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            print('Duty cycle refresh for node {0}'.format(self.dev_id))
            self.duty_cycle = DUTY_CYCLE

        if self.duty_cycle - time > 0:
            self.duty_cycle -= time
        else:
            self.seq += 1
