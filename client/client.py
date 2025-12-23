import socket
import json

HOST = "127.0.0.1"
PORT = 5000  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    join_obj = {
        'id' : 'xyz',
        'type' : 'JOIN'
    }
    s.sendall((json.dumps(join_obj) + '\n').encode())
    data1 = s.recv(1024)
    print(f"Received '{data1.decode()}'")
    bullet_obj = {
        'id' : 'xyz',
        'type' : 'ATTACK',
        'directionX' : 1,
        'directionY' : 0
    }
    s.sendall((json.dumps(bullet_obj) + '\n').encode())
    data3 = s.recv(1024)
    print(f"Received '{data3.decode()}'")
    while True:
        send_obj = {
            'id' : 'xyz',
            'type': 'MOVE',
            'dx' : 0,
            'dy' : 1
        }
        s.sendall((json.dumps(send_obj) + '\n').encode())
        data2 = s.recv(1024)
        print(f"Received '{data2.decode()}'")
