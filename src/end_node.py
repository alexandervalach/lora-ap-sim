from multiprocessing import Queue
from lora import BATTERY_FULL
from lora import DUTY_CYCLE
from lora import NET_CONFIG
from lora import LoRa
from lora import PRE_SHARED_KEY
from lora import REG_FREQUENCIES
from lora import GW_DUTY_CYCLE
from node import Node

class EndNode(Node):
    def __init__(self, dev_id, register_node=True, seq=1):
        """
        Constructor
        :param dev_id: string, end node id
        :param register_node: boolean, set if node should itself register first
        :param seq: int, default sequence number
        """
        self.dev_id = dev_id
        self.seq = seq
        self.battery_level = BATTERY_FULL
        self.duty_cycle = DUTY_CYCLE
        self.is_mobile = False
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_future_time()
        self.duty_cycle_na = 0
        self.pre_shared_key = PRE_SHARED_KEY
        self.freq = REG_FREQUENCIES[0]
        self.last_downlink_toa = 0
        self.register_node = register_node
        self.node_registered = not register_node
        self.active_time = 0
        self.uptime = 0
        self.collision_counter = 0
        self.awaiting_reply = Queue()
        self.ap_duty_cycle = GW_DUTY_CYCLE

    def _select_net_data(self, config_type='normal'):
        sf = self.net_config[config_type]['sf']
        band = self.net_config[config_type]['band']
        cr = self.net_config[config_type]['cr']
        power = self.net_config[config_type]['power']
        freq = self.net_config[config_type]['freqs'][0]
        return sf, band, cr, power, freq

    def _process_rega(self, message):
        print('{0}: Received REGA message'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            if body['net_data']:
                net_data = body['net_data']

                for data in net_data:
                    config_type = data['type'].lower()

                    # print('Network Data Type: {0}'.format(data['type']))

                    if data['sf']:
                        self.net_config[config_type]['sf'] = data['sf']
                        # print('SF set to {0} for node {1}'.format(data['sf'], self.dev_id))

                    if data['power']:
                        self.net_config[config_type]['power'] = data['power']
                        # print('PWR set to {0} for node {1}'.format(data['power'], self.dev_id))

                    if data['cr']:
                        self.net_config[config_type]['cr'] = data['cr']
                        # print('CR set to {0} for node {1}'.format(data['cr'], self.dev_id))

                    if data['band']:
                        self.net_config[config_type]['band'] = data['band']
                        # print('BW set to {0} for node {1}'.format(data['band'], self.dev_id))

                    if data['freqs']:
                        self.net_config[config_type]['freqs'] = data['freqs']
                        #  print('FREQS {0} set for node {1}'.format(data['freqs'], self.dev_id))

        try:
            return body['time']
        except KeyError:
            return 0

    def _process_txl(self, message):
        print('{0}: Received TXL message'.format(self.dev_id))
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
                        print('{0}: SF updated to {1}'.format(self.dev_id, data['sf']))

                    if data['power']:
                        self.net_config[config_type]['power'] = data['power']
                        print('{0}: PWR updated to {1}'.format(self.dev_id, data['power']))

        try:
            return body['time']
        except KeyError:
            return 0
