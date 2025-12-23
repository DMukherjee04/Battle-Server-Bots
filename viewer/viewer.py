import socket
import json

HOST = "127.0.0.1"
PORT = 5000  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    buffer = ''
    while True:
        data = s.recv(1024)

        if not data:
            break

        buffer += data.decode()

        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if not line.strip():
                continue

            recv_obj = json.loads(line)

            if recv_obj['type'] == 'JOINED':

                print(f"id : {recv_obj['id']} joined...\n")

            elif recv_obj['type'] == 'STATE':

                print(f"PLAYERS : {recv_obj['players']}")
                print(f"PROJECTILES : {recv_obj['projectiles']}\n")

            elif recv_obj['type'] == 'DEAD':

                print(f"id : {recv_obj['id']} died...\n")

            elif recv_obj['type'] == 'LEFT':

                print(f"id : {recv_obj['id']} left...\n")
      