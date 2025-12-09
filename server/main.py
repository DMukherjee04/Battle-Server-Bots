import socket
import asyncio
import json

HOST = "127.0.0.1"
PORT = 5000

players = {}
connections = set()

async def broadcast(data, exclude = None):
    loop = asyncio.get_running_loop()
    for connection_soc in connections:
        if connection_soc is not exclude:
            await loop.sock_sendall(connection_soc,((json.dumps(data)) + '\n').encode())

async def handle_client(conn):

    conn.setblocking(False)

    loop = asyncio.get_running_loop()
    buffer = ''
    conn_id = None

    while True:

        data = await loop.sock_recv(conn, 1024)
        if not data:
            break
        buffer += data.decode()

        while '\n' in buffer:

            line, buffer = buffer.split('\n', 1)
            if not line.strip():
                continue
            recv_obj = json.loads(line)

            if recv_obj['type'] == 'JOIN' :

                sent_obj = {
                    'type': 'WELCOME',
                    'id': recv_obj['id']
                }

                players[f"{recv_obj['id']}"] = {
                    'x' : 0,
                    'y' : 0,
                    'hp' : 100
                }

                conn_id = recv_obj['id']
                await loop.sock_sendall(conn,((json.dumps(sent_obj)) + '\n').encode())

            elif recv_obj['type'] == 'ATTACK' : # hp related calc

                sent_obj = {
                    'type': 'ATTACKED',
                    'id': recv_obj['id']
                }

                await loop.sock_sendall(conn,((json.dumps(sent_obj)) + '\n').encode())

            elif recv_obj['type'] == 'MOVE' : 

                sent_obj = {
                    'type': 'MOVED',
                    'id': recv_obj['id'],
                    'x' : players[recv_obj['id']]['x'] + recv_obj['dx'],
                    'y' : players[recv_obj['id']]['y'] + recv_obj['dy']
                }

                asyncio.create_task(broadcast(sent_obj, conn))
                players[f"{recv_obj['id']}"]['x'] = sent_obj['x']
                players[f"{recv_obj['id']}"]['y'] = sent_obj['y']
                await loop.sock_sendall(conn,((json.dumps(sent_obj)) + '\n').encode())

    players.pop(conn_id, None)
    connections.discard(conn)
    conn.close()

async def main(s):

    s.setblocking(False)
    s.listen()
    loop = asyncio.get_running_loop()

    while True:

        conn, addr = await loop.sock_accept(s)
        print(f"Connected by {addr}")
        connections.add(conn)
        asyncio.create_task(handle_client(conn))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
    
    server_soc.bind((HOST, PORT))
    asyncio.run(main(server_soc))
