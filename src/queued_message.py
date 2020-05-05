import string
import random


class QueuedMessage:
    def __init__(self, json_message, start, end):
        self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.json_message = json_message
        self.start = start
        self.retries = 0
        self.end = end


class QueuedReply:
    def __init__(self, id, message):
        self.id = id
        self.message = message
