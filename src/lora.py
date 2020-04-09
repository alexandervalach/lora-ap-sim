import random
import base64
import math

from enum import Enum

DUTY_CYCLE = 3600
BATTERY_FULL = 100
MIN_HEART_RATE = 50
MAX_HEART_RATE = 150
LORA_VERSION = "1.0"
CHANNELS = 8
PRE_SHARED_KEY = '+/////v////7////+////wIAAAA='


class LoRa:
    """ Randomly generated SNR values between 6.5 and 11.75"""

    @staticmethod
    def get_snr():
        return round(random.uniform(0, 1) * 5.25 + 6.5, 2)

    """ Randomly generated RSSI values between -35 and -115"""

    @staticmethod
    def get_rssi():
        return round(random.uniform(0, 1) * (-80) - 35, 1)

    """ Generate time according to data_length and basic parameters """

    @staticmethod
    def get_time(data_length, sf=7, cr=1.0, bw=125):
        bit_rate = sf * ((4 / (4 + cr)) / (pow(2, sf) / bw))
        return math.ceil(data_length * 8 * bit_rate)

    """ Generate base64 string from input data"""

    @staticmethod
    def get_data(heart_rate=78, battery_level=90):
        message = str(heart_rate) + "," + str(battery_level)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        return base64_bytes


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
