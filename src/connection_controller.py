import socket
import ssl
import time


class ConnectionController:
    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        self.conn = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
        self.host = host
        self.port = port

    def connect(self):
        try:
            self.conn.connect((self.host, self.port))
        except Exception as e:
            print("An error occurred during a connection attempt")
            print(e)
        # finally:
        # self.conn.close()

    def send_data(self, data):
        self.conn.sendall(data)

        try:
            reply = self.recv(1024)
            if reply is not None:
                print("Reply:")
                print(str(reply, 'ascii'))
                return reply
            else:
                return None
        except ssl.SSLError as s:
            print("No reply from network server")
            return None

    def close(self):
        self.conn.close()

    def recv(self, buffer_size):
        print("Waiting for reply...")
        try:
            text = bytes()
            chunk = bytes()
            while True:
                chunk += self.conn.recv(buffer_size)
                if not chunk:
                    break
                else:
                    text += chunk
        except Exception as e:
            if text:
                return text
            else:
                return None
