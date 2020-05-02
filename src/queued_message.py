class QueuedMessage:
    def __init__(self, json_message, start, end):
        self.json_message = json_message
        self.start = start
        self.end = end
