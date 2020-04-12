import random
import base64
from datetime import datetime

from enum import Enum

DUTY_CYCLE = 36000
BATTERY_FULL = 100
MIN_HEART_RATE = 50
MAX_HEART_RATE = 150
LORA_VERSION = "1.0"
CHANNELS = 8
PRE_SHARED_KEY = '+/////v////7////+////wIAAAA='


class LoRa:

    @staticmethod
    def get_snr():
        """
        Randomly generated SNR values between 6.5 and 11.75
        :return:
        """
        return round(random.uniform(0, 1) * 5.25 + 6.5, 2)

    @staticmethod
    def get_rssi():
        """
        Randomly generated RSSI values between -35 and -115
        :return:
        """
        return round(random.uniform(0, 1) * (-80) - 35, 1)

    """
    @staticmethod
    def get_time(data_length, sf=7, cr=1.0, bw=125):
        bit_rate = sf * ((4 / (4 + cr)) / (pow(2, sf) / bw))
        return math.ceil(data_length * 8 * bit_rate)
    """

    @staticmethod
    def get_data(heart_rate, battery_level):
        """
        Generate base64 string from input data
        :param heart_rate:
        :param battery_level:
        :return:
        """
        message = str(heart_rate) + "," + str(battery_level)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        return base64_bytes

    @staticmethod
    def calculate_time_on_air(data_len, sf, bw, cr, percentage):
        """
        Message time on air calculation based on LoRa@FIIT library
        :param data_len: data length in Bytes
        :param sf: spreading factor
        :param bw: bandwidth in Hz
        :param cr: coding rate
        :param percentage: duty cycle percentage
        :return: 
        """""
        cr = LoRa.get_coding_rate_value(cr)
        time_per_symbol = 1000 * pow(2, sf) / bw

        if sf > SpreadingFactors.SF10.value:
            optimization = 1
        else:
            optimization = 0

        time_per_preamble = (8 + 4.25) * time_per_symbol
        payload_symb_nb = 8 * data_len - 4 * sf + 28 + 16
        payload_symb_nb /= (4 * (sf - 2 * optimization))

        temp = round(payload_symb_nb)

        if temp < payload_symb_nb:
            payload_symb_nb = temp + 1
        else:
            payload_symb_nb = temp

        payload = (8 + max(payload_symb_nb * cr, 0)) * time_per_symbol

        if percentage == 0:
            return (payload + time_per_preamble) / 0.001
        elif percentage == 1:
            return (payload + time_per_preamble) / 0.01
        elif percentage == 10:
            return (payload + time_per_preamble) / 0.1

    @staticmethod
    def get_current_time():
        """
        Returns current minutes and seconds within an hour
        :return:
        """
        now = datetime.now().time()
        return now.strftime("%M:%S")

    @staticmethod
    def duty_cycle_difference(time1, time2):
        """
        Calculates difference between two timestamps and returns value in minutes
        :param time1:
        :param time2:
        :return:
        """
        fmt = '%M:%S'
        time_stamp1 = datetime.strptime(time1, fmt)
        time_stamp2 = datetime.strptime(time2, fmt)

        if time_stamp1 > time_stamp2:
            td = time_stamp1 - time_stamp2
        else:
            td = time_stamp2 - time_stamp1

        return int(round(td.total_seconds() / 60))

    @staticmethod
    def should_refresh_duty_cycle(refresh_time):
        """
        Returns whether a duty cycle should be refreshed
        :param refresh_time:
        :return:
        """
        diff = LoRa.duty_cycle_difference(refresh_time, LoRa.get_current_time())
        # print(diff)
        if diff >= 59:
            return True
        else:
            return False

    @staticmethod
    def get_coding_rate_value(cr):
        if cr == CodingRates.CR45.value:
            return 5.0
        elif cr == CodingRates.CR46.value:
            return 6.0
        elif cr == CodingRates.CR47.value:
            return 7.0
        elif cr == CodingRates.CR48.value:
            return 8.0


class Acknowledgement(Enum):
    def __str__(self):
        return str(self.value)

    NO_ACK = "UNSUPPORTED"
    OPTIONAL = "VOLATILE"
    MANDATORY = "MANDATORY"


class MessageType(Enum):
    def __str__(self):
        return str(self.value)

    REGR = "REGR"
    REGA = "REGA"
    SETR = "SETR"
    SETA = "SETA"
    RXL = "RXL"
    TXL = "TXL"
    KEYS = "KEYS"
    KEYR = "KEYR"
    KEYA = "KEYA"


class CodingRates(Enum):
    def __str__(self):
        return str(self.value)

    CR45 = "4/5"
    CR46 = "4/6"
    CR47 = "4/7"
    CR48 = "4/8"


class SpreadingFactors(Enum):
    def __int__(self):
        return int(self.value)

    SF6 = 6
    SF7 = 7
    SF8 = 8
    SF9 = 9
    SF10 = 10
    SF11 = 11
    SF12 = 12


class Frequencies(Enum):
    def __int__(self):
        return int(self.value)

    F1 = 100000
    F863 = 863000000
    F870 = 870000000
    F8661 = 866100000
    F8665 = 866500000
    F8667 = 866700000
    F8669 = 866900000
    F8638 = 863800000


class Bandwidth(Enum):
    def __int__(self):
        return int(self.value)

    BW125 = 125000
    BW250 = 250000
    BW500 = 500000


class Power(Enum):
    def __int__(self):
        return int(self)

    PW14 = 14
    PW13 = 13
    PW12 = 12


NET_CONFIG = {
    'normal': {
        'freqs': [],
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF7.value,
        'power': Power.PW13.value
    },
    'reg': {
        'freqs': [],
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF7.value,
        'power': Power.PW14.value
    },
    'emer': {
        'freqs': [],
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF7.value,
        'power': Power.PW14.value
    }
}

MAX_POWER = Power.PW14.value

FREQUENCIES = [
    Frequencies.F863.value,
    Frequencies.F1.value,
    Frequencies.F870.value
]

SPREADING_FACTORS = [
    SpreadingFactors.SF7.value,
    SpreadingFactors.SF8.value,
    SpreadingFactors.SF9.value,
    SpreadingFactors.SF10.value,
    SpreadingFactors.SF11.value,
    SpreadingFactors.SF12.value
]

CODING_RATES = [
    CodingRates.CR45.value,
    CodingRates.CR46.value,
    CodingRates.CR47.value,
    CodingRates.CR48.value
]

BANDS = [
    Bandwidth.BW125.value,
    Bandwidth.BW250.value,
    Bandwidth.BW500.value
]
