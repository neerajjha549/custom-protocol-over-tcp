# Python TCP Client-Server with Custom Protocol

This project provides a simple yet robust implementation of a multi-threaded TCP server and a corresponding client in Python. They communicate using a custom-defined binary protocol that ensures message integrity and clarity.

This example is designed to be a clear, well-documented starting point for anyone looking to understand socket programming, custom protocols, and multi-threaded servers.

---

## Features

-   **Multi-threaded Server:** The server can handle multiple client connections simultaneously, with each client managed in its own thread.
-   **Custom Binary Protocol:** A simple header-based protocol is used to frame messages, ensuring that complete messages are always processed.
-   **Clear Separation of Concerns:** The protocol, server logic, and client logic are well-defined and separated.
-   **Interactive Client:** The client provides a simple command-line interface for interacting with the server.
-   **Robust Communication:** Helper functions are used to ensure that the exact number of bytes for each part of a message (header and payload) is sent and received, preventing common streaming issues.

---

## The Custom Protocol

The protocol adds a layer of structure on top of the TCP stream. Every message consists of a **5-byte header** followed by a **variable-length payload**.

### Message Structure

| Part           | Size (bytes) | Data Type      | Description                                          |
| -------------- | ------------ | -------------- | ---------------------------------------------------- |
| **Command** | 1 byte       | Unsigned Int   | A number representing the action to perform.         |
| **Payload Len**| 4 bytes      | Unsigned Int   | The length of the upcoming payload data in bytes.    |
| **Payload** | Variable     | String (UTF-8) | The actual data for the command.                     |

### Defined Commands

| Code | Name      | Client Command | Description                                      |
| :--- | :-------- | :------------- | ------------------------------------------------ |
| `1`  | `ECHO`    | `echo <msg>`   | Server returns the `<msg>` back to the client.   |
| `2`  | `REVERSE` | `rev <msg>`    | Server returns a reversed version of `<msg>`.    |
| `3`  | `QUIT`    | `quit`         | Informs the server that the client is leaving.   |

---

## How to Run

### Prerequisites

-   Python 3.6+

### 1. Start the Server

Open a terminal and run the server script. It will bind to `127.0.0.1:65432` and wait for connections.

```
python server.py

```

You should see the output:

```
Server configured to run on 127.0.0.1:65432
Server started and listening for connections...

```

### 2. Run the Client

Open one or more new terminals and run the client script in each. Each will connect to the server.

```
python client.py

```

The client will connect and present you with a prompt:

```
Connecting to server at 127.0.0.1:65432...
Successfully connected to the server.

Commands:
  echo <message>  - Server will send the message back.
  rev <message>   - Server will reverse the message.
  quit            - Disconnect from the server.
--------------------------------------------------
Enter command >

```

### 3. Interact with the Server

You can now send commands from any client terminal.

-   **Echo a message:**
    
    ```
    Enter command > echo Hello, World!
    Server Response: Hello, World!
    
    ```
    
-   **Reverse a message:**
    
    ```
    Enter command > rev custom protocols are fun
    Server Response: nuf era slocotorp motsuc
    
    ```
    
-   **Quit the session:**
    
    ```
    Enter command > quit
    Sent QUIT command to server.
    Closing connection to the server.
    
    ```
    

While clients are interacting, the server's terminal will log all activity, showing connections, received commands, and disconnections.

## How to Extend

This project is a great foundation for more complex applications. Here are some ideas for extending it:

-   **Add More Commands:** Define new command codes in both the server and client (e.g., for simple calculations, file lookups, or returning server status).
    
-   **Implement Encryption:** Use libraries like `ssl` to wrap the client and server sockets, securing the data in transit.
    
-   **User Authentication:** Add commands for `LOGIN` and `REGISTER` and maintain a state for each client connection on the server.
    
-   **Broadcast Messages:** Implement a command that allows one client to send a message that is broadcast to all other connected clients.