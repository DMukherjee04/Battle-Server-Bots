import socket
import asyncio
import json

HOST = "127.0.0.1"
PORT = 5000

players = {}
inputs = {}
projectiles = {}
connections = set()

projectile_count = 1

async def broadcast(data, exclude = None):
    loop = asyncio.get_running_loop()
    for connection_soc in connections:
        if connection_soc is not exclude:
            await loop.sock_sendall(connection_soc,((json.dumps(data)) + '\n').encode())

def all_players(exclude = None):              
    all_players = {}
    for key in players.keys():
        if key != exclude:
            all_players[f"{key}"] = players[f"{key}"]
    return all_players

def projectile_handling(): 

    HIT_RADII = 10
    DAMAGE = 20
    MAP_START = 0
    MAP_END = 800

    proj_to_pop = []
    for key_proj, proj in list(projectiles.items()):

        proj['x'] += proj['vx'] 
        proj['y'] += proj['vy']

        if proj['x'] > MAP_END or proj['y'] > MAP_END or proj['x'] < MAP_START or proj['y'] < MAP_START:
                proj_to_pop.append(key_proj)
                continue
 
        player_to_pop = None
        for key_player, player in list(players.items()): 
            if abs(player['x'] - proj['x']) < HIT_RADII and abs(player['y'] - proj['y']) < HIT_RADII and key_player != proj['owner'] and player['hp'] > 0: ## hitbox
                player['hp'] = max(0, player['hp'] - DAMAGE) ## later i would add variable dmg
                if player['hp'] <= 0:
                    player_to_pop = key_player
                proj_to_pop.append(key_proj)
                break
        
        players.pop(player_to_pop, None)

    for key_proj_to_pop in proj_to_pop:
        projectiles.pop(key_proj_to_pop, None)

def update_world_state(): ## to update world state
    
    global projectile_count

    for key, cmd in list(inputs.items()):

        if cmd['type'] == 'MOVE': ## handling MOVE

            players[key]['x'] += cmd['dx']
            players[key]['y'] += cmd['dy']

        elif cmd['type'] == 'ATTACK': ## handling ATTACK

            speed = 5 ## will change acc to projectile type

            projectiles[projectile_count] = {
                'owner' : key,
                'x' : players[key]['x'],
                'y' : players[key]['y'],
                'vx' : speed * cmd['direction'][0], ## think of it like vector, dx -> units in i cap, speed * dx -> velocity
                'vy' : speed * cmd['direction'][1]
            }
            projectile_count += 1

    projectile_handling()

    world_state = {
        'type' : 'STATE',
        'players' : players,
        'projectiles' : projectiles
    }
    
    inputs.clear()
    asyncio.create_task(broadcast(world_state)) 

async def server_tick_loop(): ## tick loop fnc
    
    while True:
        update_world_state()
        await asyncio.sleep(0.033)

async def client_handling(conn):

    conn.setblocking(False)

    loop = asyncio.get_running_loop()
    buffer = ''
    player_id = None

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

                player_id = recv_obj['id']

                sent_obj_to_joinee = { ## to the player who joined
                    'type': 'WELCOME',
                    'id': recv_obj['id'],
                    'x' : 0,
                    'y' : 0,
                    'hp' : 100,
                    'players' : all_players(recv_obj['id'])
                }

                players[f"{recv_obj['id']}"] = { ## updating players obj
                    'x' : 0,
                    'y' : 0,
                    'hp' : 100
                }

                joined_player_info = { ## to all the other players, letting them know who joined 
                    'type': 'JOINED',                    
                    'id' : recv_obj['id'],
                    'x' : 0,
                    'y' : 0,
                    'hp' : 100
                }

                asyncio.create_task(broadcast(joined_player_info, conn)) ## broadcast who joined
                await loop.sock_sendall(conn,((json.dumps(sent_obj_to_joinee)) + '\n').encode())

            elif recv_obj['type'] == 'ATTACK' : 

                inputs[player_id] = {
                    'type' : 'ATTACK',
                    'direction' : (recv_obj['directionX'], recv_obj['directionY']),
                }

            elif recv_obj['type'] == 'MOVE' : 

                inputs[player_id] = {
                    'type' : 'MOVE',
                    'dx' : recv_obj['dx'],
                    'dy' : recv_obj['dy']
                }

    players.pop(player_id, None)
    leave_obj = {
        'id' : player_id,
        'type' : 'LEFT'
    }
    asyncio.create_task(broadcast(leave_obj, conn)) ## broadcast leave to all players other than that player
    connections.discard(conn)
    conn.close()

async def main(s):

    s.setblocking(False)
    s.listen()
    loop = asyncio.get_running_loop()

    asyncio.create_task(server_tick_loop()) ## loop will go on

    while True:

        conn, addr = await loop.sock_accept(s)
        print(f"Connected by {addr}")
        connections.add(conn)
        asyncio.create_task(client_handling(conn))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
    
    server_soc.bind((HOST, PORT))
    asyncio.run(main(server_soc))
