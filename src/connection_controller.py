import socket
import ssl
import time


class ConnectionController:
    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)

        self.conn = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
        self.host = host
        self.port = port

    def connect(self):
        try:
            self.conn.connect((self.host, self.port))
        except InterruptedError as e:
            print("An error occurred during a connection attempt")
            print(e)
        # finally:
        # self.conn.close()

    def send_data(self, data):
        self.conn.send(data)

        try:
            reply = self.recv()
            if reply is not None:
                print("Reply:\n" + reply)
                return reply
            else:
                return None
        except ssl.SSLError as s:
            print("No reply from network server")
            return None

    def close(self):
        self.conn.close()

    def recv(self):
        try:
            text = ''
            chunk = ''
            while True:
                chunk += self.conn.recv()
                if not chunk:
                    # Unreliable
                    break
                else:
                    text += chunk
        except Exception:
            if text:
                return text
            else:
                return None
