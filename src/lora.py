import random
import base64
import datetime

from enum import Enum

DUTY_CYCLE = 36000
GW_DUTY_CYCLE = 36000
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
        return base64.b64encode(message_bytes).decode('ascii')

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
        time_per_symbol = pow(2, sf) / (bw / 1000)

        lora_fiit_overhead = 12

        if sf > SpreadingFactors.SF10.value:
            optimization = 1
        else:
            optimization = 0

        message_symbols = 8 + ((8 * (lora_fiit_overhead + data_len) - 4 * sf + 28 + 16) / (4 * (sf - 2 * optimization))) * (cr + 4)

        return round(time_per_symbol * message_symbols)

    @staticmethod
    def get_current_time():
        """
        Returns current minutes and seconds within an hour
        :return:
        """
        return datetime.datetime.now().replace(microsecond=0)

    @staticmethod
    def get_future_time():
        """
        Returns current minutes and seconds within an hour
        :return:
        """
        return datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=1)

    @staticmethod
    def should_refresh_duty_cycle(next_refresh_time):
        """
        Returns whether a duty cycle should be refreshed
        :param next_refresh_time:
        :return:
        """
        return datetime.datetime.now().replace(microsecond=0) >= next_refresh_time

    @staticmethod
    def get_coding_rate_value(cr):
        if cr == CodingRates.CR45.value:
            return 1.0
        elif cr == CodingRates.CR46.value:
            return 2.0
        elif cr == CodingRates.CR47.value:
            return 3.0
        elif cr == CodingRates.CR48.value:
            return 4.0


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

    # normal
    F8661 = 866100000
    F8663 = 866300000
    F8665 = 866500000
    # emergency
    F8669 = 866900000
    # register
    F8667 = 866700000


class Bandwidth(Enum):
    def __int__(self):
        return int(self.value)

    BW125 = 125000
    BW250 = 250000
    BW500 = 500000


class Power(Enum):
    def __int__(self):
        return int(self)

    PW15 = 15
    PW14 = 14
    PW13 = 13
    PW12 = 12


# From lora AP concentrator
SUP_FREQUENCIES = [863000000, 100000, 870000000]

REG_FREQUENCIES = [Frequencies.F8667.value]
EMER_FREQUENCIES = [Frequencies.F8669.value]

NORMAL_FREQUENCIES = [
    Frequencies.F8661.value,
    Frequencies.F8663.value,
    Frequencies.F8665.value
]

NET_CONFIG = {
    'normal': {
        'freqs': NORMAL_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF7.value,
        'power': Power.PW13.value
    },
    'reg': {
        'freqs': REG_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF12.value,
        'power': Power.PW15.value
    },
    'emer': {
        'freqs': EMER_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF12.value,
        'power': Power.PW15.value
    }
}

BANDIT_ARMS = [
    {'sf': 7, 'pw': 10, 'reward': 70},
    {'sf': 7, 'pw': 11, 'reward': 70},
    {'sf': 7, 'pw': 12, 'reward': 70},
    {'sf': 7, 'pw': 13, 'reward': 70},
    {'sf': 7, 'pw': 14, 'reward': 70},
    {'sf': 7, 'pw': 15, 'reward': 70},
    {'sf': 8, 'pw': 10, 'reward': 75},
    {'sf': 8, 'pw': 11, 'reward': 75},
    {'sf': 8, 'pw': 12, 'reward': 75},
    {'sf': 8, 'pw': 13, 'reward': 75},
    {'sf': 8, 'pw': 14, 'reward': 75},
    {'sf': 8, 'pw': 15, 'reward': 75},
    {'sf': 9, 'pw': 10, 'reward': 80},
    {'sf': 9, 'pw': 11, 'reward': 80},
    {'sf': 9, 'pw': 12, 'reward': 80},
    {'sf': 9, 'pw': 13, 'reward': 80},
    {'sf': 9, 'pw': 14, 'reward': 80},
    {'sf': 10, 'pw': 10, 'reward': 85},
    {'sf': 10, 'pw': 11, 'reward': 85},
    {'sf': 10, 'pw': 12, 'reward': 85},
    {'sf': 10, 'pw': 13, 'reward': 85},
    {'sf': 10, 'pw': 14, 'reward': 85},
    {'sf': 10, 'pw': 15, 'reward': 85},
    {'sf': 11, 'pw': 10, 'reward': 90},
    {'sf': 11, 'pw': 11, 'reward': 90},
    {'sf': 11, 'pw': 12, 'reward': 90},
    {'sf': 11, 'pw': 13, 'reward': 90},
    {'sf': 11, 'pw': 14, 'reward': 90},
    {'sf': 11, 'pw': 15, 'reward': 90},
    {'sf': 12, 'pw': 10, 'reward': 95},
    {'sf': 12, 'pw': 11, 'reward': 95},
    {'sf': 12, 'pw': 12, 'reward': 95},
    {'sf': 12, 'pw': 13, 'reward': 95},
    {'sf': 12, 'pw': 14, 'reward': 95},
    {'sf': 12, 'pw': 15, 'reward': 100},
]

MAX_POWER = Power.PW14.value

FREQUENCIES = [
    Frequencies.F8667.value,
    Frequencies.F8661.value,
    Frequencies.F8663.value,
    Frequencies.F8669.value
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