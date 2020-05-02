import json


class Helper:
    @staticmethod
    def to_json(message):
        json_message = json.dumps(message, separators=(',', ':'), sort_keys=True)
        return json_message.encode('ascii')

    @staticmethod
    def from_json(json_message):
        return json.loads(json_message)