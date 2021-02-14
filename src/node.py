import random
import time

from multiprocessing import Queue
from lora import BATTERY_FULL
from lora import DUTY_CYCLE
from lora import GW_DUTY_CYCLE
from lora import NET_CONFIG
from lora import PROC_COEFF
from lora import SLEEP_TIME
from lora import LoRa
from lora import PRE_SHARED_KEY
from lora import REG_FREQUENCIES
from lora import MIN_HEART_RATE
from lora import MAX_HEART_RATE
from lora import MAX_X_POSITION
from lora import MAX_Y_POSITION
from lora import MessageType
from lora import Acknowledgement
from helper import Helper
from queued_message import QueuedMessage


class Node:
    def __init__(self, dev_id, register_node=True, seq=1, sleep_time=SLEEP_TIME):
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
        self.x = 0
        self.y = 0
        self.x_direction = 1
        self.y_direction = 1
        self.sleep_time = sleep_time
        self.set_initial_position(round(random.uniform(0, 1) * MAX_X_POSITION, 1), round(random.uniform(0, 1) * MAX_Y_POSITION, 1))

    def device_routine(self, normal_queue, emer_queue):
        """
        Main end node process putting message to queue
        :param normal_queue: Queue, queue for all messages
        :param emer_queue: Queue, priority queue for emergency messages
        :return
        """
        self.uptime = time.time()

        try:
            if self.register_node:
                while not self.node_registered:
                    start_time = time.time()
                    message = self.generate_message('reg')
                    self._send_routine(message, normal_queue, is_register=True)
                    self.active_time += (time.time() - start_time)
                    time.sleep(SLEEP_TIME)

            while True:
                start_time = time.time()

                # If there is a message waiting in queue, send it first
                if not self.awaiting_reply.empty():
                    queued_message = self.awaiting_reply.get(timeout=1)
                    queued_message.retries += 1

                    msg_dict = Helper.from_json(queued_message.json_message)

                    if msg_dict['message_body']['type'] == 'emer':
                        self._send_routine(msg_dict, emer_queue)
                    else:
                        self._send_routine(msg_dict, normal_queue)

                    if queued_message.retries < 3:
                        self.awaiting_reply.put(queued_message)
                # Otherwise generate new message
                else:
                    message = self.generate_message('normal')

                    if message['message_body']['type'] == 'emer':
                        self._send_routine(message, emer_queue)
                    else:
                        self._send_routine(message, normal_queue)

                    self.active_time += time.time() - start_time
                self.move_node(SLEEP_TIME)
        except KeyboardInterrupt:
            self.uptime = (time.time() - self.uptime) / 1000
            print("{0},{1},{2},{3}".format(self.dev_id, round(self.active_time * PROC_COEFF, 2),
                                           round(self.uptime * PROC_COEFF, 2), self.collision_counter))

    def get_dev_id(self):
        """
        Return a new dev_id
        :return string
        """
        return self.dev_id

    def pop_last_downlink_toa(self):
        """
        Pop last downlink airtime message
        :return int, airtime
        """
        toa = self.last_downlink_toa
        self.last_downlink_toa = 0
        return toa

    @staticmethod
    def _calculate_heart_rate(config_type='normal'):
        """
        Heart rate calculation
        :param config_type: string, config type
        :return tuple, heart-rate value and new config type
        """
        heart_rate = random.randint(MIN_HEART_RATE, MAX_HEART_RATE)
        # If critical heart rate values are present change message type
        if heart_rate < 56 or heart_rate > 145:
            config_type = 'emer'

        return heart_rate, config_type

    def _select_net_data(self, config_type='normal'):
        """
        Selects config parameters from net config
        :param config_type: string
        :return tuple, SF, BW, CR, PWR, FREQ
        """
        sf = self.net_config[config_type]['sf']
        band = self.net_config[config_type]['band']
        cr = self.net_config[config_type]['cr']
        power = self.net_config[config_type]['power']
        freq = self.net_config[config_type]['freqs'][0]
        return sf, band, cr, power, freq

    def generate_message(self, config_type='normal'):
        """
        Generate new message
        :param config_type: string, normal, emer, reg
        :return dict, STIoT message as a dictionary
        """
        message = {}
        message_body = {}

        heart_rate, config_type = self._calculate_heart_rate(config_type)
        sf, band, cr, power, freq = self._select_net_data(config_type)

        app_data = LoRa.get_data(heart_rate, self.battery_level)
        time_on_air = LoRa.calculate_time_on_air(len(app_data), sf, band, cr, 1)

        # Check if there is remaining duty cycle, additionally perform refresh
        self.set_remaining_duty_cycle(time_on_air)
        # print(self.duty_cycle)
        if self.duty_cycle == 0:
            print("{0}: Could not send message due to low duty cycle".format(self.dev_id))
            return None

        message_body['freq'] = freq
        message_body['band'] = band
        message_body['cr'] = cr
        message_body['dev_id'] = self.dev_id
        message_body['power'] = power
        message_body['duty_c'] = self.ap_duty_cycle
        message_body['rssi'] = LoRa.get_rssi()
        message_body['sf'] = sf
        message_body['snr'] = LoRa.get_snr()
        message_body['time'] = time_on_air
        message_body['type'] = config_type

        message['message_body'] = message_body

        if config_type == 'normal':
            return self._generate_rxl(message, app_data)
        elif config_type == 'emer':
            return self._generate_emer(message, app_data)
        elif config_type == 'reg':
            return self._generate_regr(message, app_data)

    def _generate_regr(self, message, app_data):
        """
        Generate new regr message
        :param message: dict, message
        :param app_data: base64, base64 encoded application data
        :return dict, STIoT message REGR
        """
        message['message_name'] = MessageType.REGR.value
        message['message_body']['app_data'] = app_data
        message['message_body']['sh_key'] = self.pre_shared_key
        return message

    def _generate_rxl(self, message, data):
        """
        Generate new regr message
        :param message: dict, message
        :param app_data: base64, base64 encoded application data
        :return dict, STIoT message RXL, type normal
        """
        message['message_name'] = MessageType.RXL.value
        message['message_body']['ack'] = Acknowledgement.OPTIONAL.value
        message['message_body']['conf_need'] = False
        message['message_body']['data'] = data
        message['message_body']['seq'] = self.seq
        self.seq += 1
        return message

    def _generate_emer(self, message, data):
        """
        Generate new regr message
        :param message: dict, message
        :param app_data: base64, base64 encoded application data
        :return dict, STIoT message RXL, type emer
        """
        message['message_name'] = MessageType.RXL.value
        message['message_body']['ack'] = Acknowledgement.MANDATORY.value
        message['message_body']['conf_need'] = False
        message['message_body']['data'] = data
        message['message_body']['seq'] = self.seq
        self.seq += 1
        return message

    def process_reply(self, reply, ap_duty_cycle):
        """
        Returns time on air of message
        :param ap_duty_cycle: AP duty cycle
        :param reply: dict, message reply
        :return int or None, time on air of message
        """
        start_time = time.time()
        messages_awaiting_reply = []
        self.update_ap_duty_cycle(ap_duty_cycle)

        while not self.awaiting_reply.empty():
            msg = self.awaiting_reply.get(timeout=1)
            messages_awaiting_reply.append(msg)
            if msg.id == reply.id:
                print("{0}: Message {1} acknowledged".format(self.dev_id, reply.id))
                messages_awaiting_reply.remove(msg)
                break

        for item in messages_awaiting_reply:
            self.awaiting_reply.put(item)

        try:
            message_name = reply.message['message_name']

            if message_name == 'REGA':
                return self._process_rega(reply.message)
            elif message_name == 'TXL':
                return self._process_txl(reply.message)
            else:
                print("Unknown message type")
                return 0
        except ValueError:
            print("Could not deserialize JSON object")
            return 0
        except TypeError:
            print("TypeError")
            return 0
        finally:
            self.active_time += (time.time() - start_time)

    def _process_rega(self, message):
        """
        Process registration acknowledgement
        :param message: STIoT Message as a dictionary
        :return
        """
        print('{0}: Received REGA message'.format(self.dev_id))
        try:
            return message['message_body']['time']
        except KeyError:
            return 0

    def _process_txl(self, message):
        """
        Process TX message
        :param message: STIoT message as a dictionary
        :return
        """
        print('{0}: Received TXL message'.format(self.dev_id))
        try:
            return message['message_body']['time']
        except KeyError:
            return 0

    def set_remaining_duty_cycle(self, time_on_air):
        """
        Checks AP duty cycle and refresh it if duty cycle refresh
        Returns 0 if available and substracts duty cycle
        :param time_on_air: int, time on air of message
        :return int, 0 if available, 1 if not available
        """
        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            print('{0}: Duty cycle refresh'.format(self.dev_id))
            self.duty_cycle = DUTY_CYCLE
            self.duty_cycle_na = 0
            self.duty_cycle_refresh = LoRa.get_future_time()

        if self.duty_cycle - time_on_air > 0:
            self.duty_cycle -= time_on_air
            print('{0}: Remaining duty cycle is {1}.'.format(self.dev_id, self.duty_cycle))
            return 0

        self.duty_cycle_na = 1
        self.seq += 1
        return self.duty_cycle_na

    def _schedule_message(self, message, queue):
        """
        Helper function to add a message to multiprocessor queue
        :param message: dict, message to schedule
        :param queue: Queue, normal queue
        :return boolean, True if message scheduled, False if collision
        """
        message_body = message['message_body']
        send_time, receive_time = LoRa.get_frame_time(message_body['time'])
        queued_message = QueuedMessage(Helper.to_json(message), send_time, receive_time)
        is_collision = False

        queue_items = []

        while not queue.empty():
            msg = queue.get(timeout=1)
            queue_items.append(msg)
            is_collision = LoRa.is_collision(queued_message, msg)
            if is_collision:
                break

        for item in queue_items:
            queue.put(item)

        if not is_collision:
            queue.put(queued_message)

            if message_body['type'] == 'emer' or message_body['type'] == 'reg':
                self.awaiting_reply.put(queued_message)
                print("{0}: {1} message scheduled. Awaiting reply for {2}.".format(
                    self.dev_id, message_body['type'], queued_message.id))
            else:
                print("{0}: {1} message scheduled".format(self.dev_id, message_body['type']))
            return True
        print("{0}: A collision occurred on SF{1}".format(self.dev_id, message_body['sf']))
        return False

    def _send_routine(self, message, queue, is_register=False):
        """
        Try to send a message three times
        :param message: dict, send message
        :param queue: Queue, normal queue
        :param is_register: boolean, check if registration
        :return
        """
        if message is None:
            print("{0}: Message could not be sent due to low duty cycle".format(self.dev_id))
            return

        retries = 0
        message_scheduled = False

        while not message_scheduled:
            message_scheduled = self._schedule_message(message, queue)
            if not message_scheduled:
                retries += 1
                self.collision_counter += 1
                if retries >= 3:
                    print("{0}: {1} unsuccessful attempts. Entering sleep mode".format(self.dev_id, retries))
                    break
                time.sleep(random.randrange(1) + 1)

            if is_register and message_scheduled:
                self.node_registered = True

    def update_ap_duty_cycle(self, duty_cycle):
        """
        Updates AP duty cycle
        :param duty_cycle: int, duty cycle values
        :return void
        """
        self.ap_duty_cycle = duty_cycle

    def set_initial_position(self, x, y):
        """
        Sets the position of each node
        :param x: position on x-axis
        :param y: position on y-axis
        :return: void
        """
        self.x = x
        self.y = y
        print(f'Node {self.dev_id} position set to [{self.x}, {self.y}]')

    def move_node(self, sleep_time=SLEEP_TIME):
        for i in range(sleep_time):
            x = round(random.uniform(0, 1) * 1.45, 1)
            y = round(random.uniform(0, 1) * 1.45, 1)
            self._check_x_direction(x)
            self._check_y_direction(y)
            self.x = self.x + (self.x_direction * x)
            self.y = self.y + (self.y_direction * y)
            print(f'Node {self.dev_id} moved to [{self.x:.1f}, {self.y:.1f}]')
            time.sleep(1)

    def _check_x_direction(self, x):
        if self.x_direction > 0:
            # Right step
            if self.x + x >= MAX_X_POSITION:
                self.x_direction = -1
        else:
            # Left step
            if self.x - x <= 0:
                self.x_direction = 1

    def _check_y_direction(self, y):
        if self.y_direction > 0:
            if self.y + y >= MAX_Y_POSITION:
                self.y_direction = -1
        else:
            if self.y - y <= 0:
                self.y_direction = 1
