import socket
import ssl


class ConnectionController:
    def __init__(self, s=None):
        """
        Initializes a new ConnectionController instance.

        Args:
            s (socket.socket, optional): An existing SSL socket instance. If None, a new socket is created.
        """
        if s is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5)
        else:
            self.s = s

        self.conn = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_TLSv1_2)

    def connect(self, host: str, port: int) -> None:
        """
        Connects to a remote server.

        Args:
            host (str): IP address or domain name of the remote server.
            port (int): Port number on which to connect.
        
        Raises:
            Exception: If an error occurs during the connection attempt.
        """
        try:
            self.conn.connect((host, port))
        except Exception as e:
            print("An error occurred during a connection attempt")
            print(e)

    def get_connection(self) -> ssl.SSLSocket:
        """
        Returns the SSL socket wrapper used for the connection.

        Returns:
            ssl.SSLSocket: The SSL socket wrapper.
        """
        return self.conn

    def send_data(self, data: bytes) -> bytes:
        """
        Sends data using the SSL socket and receives a reply.

        Args:
            data (bytes): Data to be sent over the connection.

        Returns:
            bytes: Reply received from the server, or None if no reply is received.
        """
        self.conn.sendall(data)

        try:
            reply = self.recv(1024)
            if reply is not None:
                return reply
            else:
                return None
        except ssl.SSLError as s:
            print("No reply from network server")
            return None

    def close(self) -> None:
        """
        Closes the socket connections properly.
        """
        self.s.close()
        self.conn.close()

    def recv(self, buffer_size: int = 1024) -> bytes:
        """
        Receives data from the SSL socket.

        Args:
            buffer_size (int, optional): Size of the buffer to receive data. Defaults to 1024.

        Returns:
            bytes: Data received from the server.
        """
        try:
            text = bytes()
            while True:
                chunk = self.conn.recv(buffer_size)
                if not chunk:
                    break
                text += chunk
            return text
        except Exception as e:
            return None
