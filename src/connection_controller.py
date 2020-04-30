import socket
import ssl


class ConnectionController:
    def __init__(self, s=None):
        if s is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5)
        else:
            self.s = s

        self.conn = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_TLSv1)

    def connect(self, host, port):
        try:
            self.conn.connect((host, port))
        except Exception as e:
            print("An error occurred during a connection attempt")
            print(e)

    def get_connection(self):
        return self.conn

    def send_data(self, data):
        self.conn.sendall(data)

        try:
            reply = self.recv(1024)
            if reply is not None:
                # print("Reply:")
                # print(str(reply, 'ascii'))
                return reply
            else:
                return None
        except ssl.SSLError as s:
            print("No reply from network server")
            return None

    def close(self):
        self.s.close()
        self.conn.close()

    def recv(self, buffer_size):
        # print("Waiting for reply...")
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
