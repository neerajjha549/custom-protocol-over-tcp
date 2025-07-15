import socket
import struct
import sys

# Define constants for the protocol to match the server
HEADER_SIZE = 5
COMMAND_ECHO = 1
COMMAND_REVERSE = 2
COMMAND_QUIT = 3

class TCPClient:
    """
    A TCP client that communicates with the custom protocol server.
    """
    def __init__(self, host='127.0.0.1', port=65432):
        """
        Initializes the client.
        Args:
            host (str): The host IP address of the server.
            port (int): The port of the server.
        """
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """
        Connects to the server.
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to server at {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            print("Successfully connected to the server.")
            return True
        except ConnectionRefusedError:
            print("Connection failed. Is the server running?")
            return False
        except Exception as e:
            print(f"An error occurred during connection: {e}")
            return False

    def start_interactive_mode(self):
        """
        Starts a command-line loop to interact with the server.
        """
        if not self.client_socket:
            print("Client is not connected. Cannot start interactive mode.")
            return

        print("\nCommands:")
        print("  echo <message>  - Server will send the message back.")
        print("  rev <message>   - Server will reverse the message.")
        print("  quit            - Disconnect from the server.")
        print("--------------------------------------------------")

        try:
            while True:
                user_input = input("Enter command > ").strip()
                if not user_input:
                    continue

                parts = user_input.split(' ', 1)
                command_str = parts[0].lower()
                payload = parts[1] if len(parts) > 1 else ""

                if command_str == "echo":
                    command_id = COMMAND_ECHO
                elif command_str == "rev":
                    command_id = COMMAND_REVERSE
                elif command_str == "quit":
                    self._send_message(COMMAND_QUIT, "")
                    print("Sent QUIT command to server.")
                    break
                else:
                    print("Invalid command. Please use 'echo', 'rev', or 'quit'.")
                    continue
                
                # Send message and get response
                self._send_message(command_id, payload)
                response = self._receive_message()
                if response:
                    print(f"Server Response: {response}")
                else:
                    print("Did not receive a valid response from the server.")
                    break # Break if server connection seems lost

        except KeyboardInterrupt:
            print("\nExiting. Sending QUIT command...")
            self._send_message(COMMAND_QUIT, "")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            self.close()

    def _send_message(self, command, payload):
        """
        Packs and sends a message to the server.
        Args:
            command (int): The command code.
            payload (str): The string payload.
        """
        try:
            payload_bytes = payload.encode('utf-8')
            # Pack the header: '>BI' means big-endian, 1-byte unsigned int, 4-byte unsigned int
            header = struct.pack('>BI', command, len(payload_bytes))
            message = header + payload_bytes
            self.client_socket.sendall(message)
        except socket.error as e:
            print(f"Failed to send message: {e}")
            self.close()

    def _receive_message(self):
        """
        Receives and unpacks a message from the server.
        Returns:
            str: The payload of the received message, or None on error.
        """
        try:
            # 1. Read the header
            header_data = self._recv_all(HEADER_SIZE)
            if not header_data:
                print("Server closed the connection while waiting for header.")
                return None

            # 2. Unpack header
            _command, payload_len = struct.unpack('>BI', header_data)

            # 3. Read payload
            if payload_len > 0:
                payload_data = self._recv_all(payload_len)
                if not payload_data:
                    print("Server closed the connection while waiting for payload.")
                    return None
                return payload_data.decode('utf-8')
            return "" # Return empty string for zero-length payloads
        except socket.error as e:
            print(f"Failed to receive message: {e}")
            return None

    def _recv_all(self, n):
        """Helper function to receive exactly n bytes."""
        data = bytearray()
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def close(self):
        """Closes the client socket."""
        if self.client_socket:
            print("Closing connection to the server.")
            self.client_socket.close()
            self.client_socket = None

if __name__ == "__main__":
    client = TCPClient()
    if client.connect():
        client.start_interactive_mode()

