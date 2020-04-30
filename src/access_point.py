import json

from lora import NET_CONFIG
from lora import GW_DUTY_CYCLE
from lora import LORA_VERSION
from lora import SUP_FREQUENCIES
from lora import SPREADING_FACTORS
from lora import CODING_RATES
from lora import BANDS
from lora import MAX_POWER
from lora import LoRa
from lora import MessageType


class AccessPoint:
    def __init__(self, hw_id, conn):
        self.hw_id = hw_id
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_current_time()
        self.duty_cycle = GW_DUTY_CYCLE
        self.conn = conn

    def generate_setr(self):
        message = {}
        message_body = {}
        lora_stand = {}

        message['message_name'] = MessageType.SETR.value
        message_body['id'] = self.hw_id
        message_body['ver'] = LORA_VERSION
        message_body['m_chan'] = True
        message_body['channels'] = 8
        message_body['sup_freqs'] = SUP_FREQUENCIES
        message_body['sup_sfs'] = SPREADING_FACTORS
        message_body['sup_crs'] = CODING_RATES
        message_body['sup_bands'] = BANDS
        message_body['max_power'] = MAX_POWER

        lora_stand['name'] = "LoRa@FIIT"
        lora_stand['version'] = "1.0"

        message_body['lora_stand'] = lora_stand
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'), sort_keys=True)
        return json_message.encode('ascii')

    def send_setr(self):
        setr_message = self.generate_setr()
        reply = self.conn.send_data(setr_message)
        self.process_reply(reply)

    def process_reply(self, reply):
        if reply is not None:
            try:
                message = json.loads(str(reply, 'ascii'))
                message_name = message['message_name']

                if message_name == 'SETA':
                    print("Received SETA message")
                    # self.process_seta(message)
                else:
                    print("Unknown message type")
            except ValueError:
                print("Could not deserialize JSON object")
        else:
            print("No reply")

    def set_remaining_duty_cycle(self, time):
        print("Access point duty cycle is {0} ms".format(self.duty_cycle))

        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            print('Duty cycle refresh for access point {0}'.format(self.hw_id))
            self.duty_cycle = GW_DUTY_CYCLE
            return 0

        if self.duty_cycle - time > 0:
            self.duty_cycle -= time
            return 0
        else:
            return 1
