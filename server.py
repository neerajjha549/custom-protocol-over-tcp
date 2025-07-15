import socket
import threading
import struct
import sys

# Define constants for the protocol
HEADER_SIZE = 5
COMMAND_ECHO = 1
COMMAND_REVERSE = 2
COMMAND_QUIT = 3

class TCPServer:
    """
    A multi-threaded TCP server that implements a custom protocol.
    """
    def __init__(self, host='127.0.0.1', port=65432):
        """
        Initializes the server.
        Args:
            host (str): The host IP address to bind to.
            port (int): The port to listen on.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        print(f"Server configured to run on {self.host}:{self.port}")

    def start(self):
        """
        Starts the server, binds the socket, and listens for connections.
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # This allows reusing the address, helpful for quick restarts
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5) # Listen for up to 5 queued connections
            print("Server started and listening for connections...")
            self._accept_connections()
        except OSError as e:
            print(f"Error starting server: {e}")
            sys.exit(1)
        finally:
            if self.server_socket:
                self.server_socket.close()
                print("Server socket closed.")

    def _accept_connections(self):
        """
        Main loop to accept new client connections.
        """
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from {addr}")
                # Create a new thread to handle the client
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, addr))
                client_thread.daemon = True # Allows main program to exit even if threads are running
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        except Exception as e:
            print(f"Error accepting connections: {e}")

    def _handle_client(self, client_socket, addr):
        """
        Handles communication with a single client according to the custom protocol.
        Args:
            client_socket (socket.socket): The socket object for the client.
            addr (tuple): The address of the client (ip, port).
        """
        try:
            while True:
                # 1. Read the fixed-size header first
                header_data = self._recv_all(client_socket, HEADER_SIZE)
                if not header_data:
                    print(f"Client {addr} disconnected abruptly.")
                    break

                # 2. Unpack the header to get command and payload length
                #    '>' for big-endian, 'B' for 1-byte unsigned int (command)
                #    'I' for 4-byte unsigned int (length)
                command, payload_len = struct.unpack('>BI', header_data)
                
                print(f"[Client {addr}] Received Header: Command={command}, Payload Length={payload_len}")

                # 3. Read the payload based on the length from the header
                payload = ""
                if payload_len > 0:
                    payload_data = self._recv_all(client_socket, payload_len)
                    if not payload_data:
                        print(f"Client {addr} disconnected before sending payload.")
                        break
                    payload = payload_data.decode('utf-8')

                print(f"[Client {addr}] Received Payload: '{payload}'")

                # 4. Process the command
                if command == COMMAND_ECHO:
                    response_payload = payload
                elif command == COMMAND_REVERSE:
                    response_payload = payload[::-1]
                elif command == COMMAND_QUIT:
                    print(f"Client {addr} sent QUIT command. Closing connection.")
                    break
                else:
                    print(f"Unknown command: {command}. Ignoring.")
                    continue

                # 5. Send the response back to the client using the same protocol
                self._send_message(client_socket, COMMAND_ECHO, response_payload)
                print(f"[Client {addr}] Sent Response: '{response_payload}'")

        except ConnectionResetError:
            print(f"Connection with {addr} was forcibly closed by the client.")
        except Exception as e:
            print(f"An error occurred with client {addr}: {e}")
        finally:
            print(f"Closing connection for {addr}")
            client_socket.close()

    def _recv_all(self, sock, n):
        """
        Helper function to ensure all n bytes are received from the socket.
        Args:
            sock (socket.socket): The socket to receive from.
            n (int): The number of bytes to receive.
        Returns:
            bytes: The received data, or None if the connection is closed.
        """
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def _send_message(self, sock, command, payload):
        """
        Packs and sends a message according to the custom protocol.
        Args:
            sock (socket.socket): The socket to send the message to.
            command (int): The command code.
            payload (str): The string payload.
        """
        payload_bytes = payload.encode('utf-8')
        header = struct.pack('>BI', command, len(payload_bytes))
        message = header + payload_bytes
        sock.sendall(message)


if __name__ == "__main__":
    server = TCPServer()
    server.start()
