from multiprocessing import Queue
from lora import BATTERY_FULL
from lora import GW_DUTY_CYCLE
from lora import DUTY_CYCLE
from lora import BANDIT_ARMS
from lora import LoRa
from lora import PRE_SHARED_KEY
from lora import Bandwidth
from lora import CodingRates
from lora import Frequencies
from node import Node
from upper_confidence_bound import UpperConfidenceBound
from thompson_sampling import ThompsonSampling


class BanditNode(Node):
    def __init__(self, dev_id, algorithm="ucb", register_node=True, seq=1):
        self.dev_id = dev_id
        self.seq = seq
        self.battery_level = BATTERY_FULL
        self.duty_cycle = DUTY_CYCLE
        self.is_mobile = False
        self.net_config = BANDIT_ARMS
        self.duty_cycle_refresh = LoRa.get_future_time()
        self.duty_cycle_na = 0
        self.pre_shared_key = PRE_SHARED_KEY
        self.freq = Frequencies.F8661.value
        self.last_downlink_toa = 0
        self.register_node = register_node
        self.node_registered = not register_node
        self.active_time = 0
        self.uptime = 0
        self.collision_counter = 0
        self.awaiting_reply = Queue()
        self.ap_duty_cycle = GW_DUTY_CYCLE

        if algorithm == "ucb":
            self.algorithm = UpperConfidenceBound(self.net_config)
        elif algorithm == "ts":
            self.algorithm = ThompsonSampling()

    def _select_net_data(self, config_type="normal"):
        net_data = self.algorithm.choose_arm()
        sf = net_data['sf']
        power = net_data['pw']
        band = Bandwidth.BW125.value
        cr = CodingRates.CR45.value
        freq = self.freq
        return sf, band, cr, power, freq

    def _process_rega(self, message):
        print('{0}: Received REGA message'.format(self.dev_id))
        body = message['message_body']
        dev_id = body['dev_id']

        if dev_id == self.dev_id:
            if body['net_data']:
                print(body['net_data'])
                net_data = body['net_data']
                self.net_config = net_data
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
                print(net_data)
        try:
            return body['time']
        except KeyError:
            return 0
