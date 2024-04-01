import socket

# Configure camera settings under Device Settings > Network Settings > Network
HOST = "192.168.1.200"
# Configure control port under Device Settings > Network Settings > TCP/IP Settings
CONTROL_PORT = 107
# Configure results port under Device Settings > Network Settings > TCP/IP Settings
RESULTS_PORT = 25250

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, CONTROL_PORT))
    # Default string to trigger camera
    # Configure trigger string under Device Settings > Network Settings > TCP/IP Settings > Control
    message = "TRIGGER\r\n"
    s.sendall(message.encode())
    print(f"Message sent: {message}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, RESULTS_PORT))
    response = s.recv(1024).decode()
    print(f"Message received: {response}")
