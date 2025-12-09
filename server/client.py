import socket
import json

HOST = "127.0.0.1"
PORT = 5000  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    join_obj = {
        'id' : 'foxy',
        'type' : 'MOVE'
    }
    s.sendall((json.dumps(join_obj) + '\n').encode())
    data = s.recv(1024)

print(f"Received '{data.decode()}'")