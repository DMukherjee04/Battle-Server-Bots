import random
import time

MAP_START = 10
MAP_END = 690
MOVE_CAPPED_AT = 20
SPEED = 5
HIT_RADII = 15
DAMAGE = 20
SHOOT_CD = 5

projectile_count = 1

actions = {}

def random_coor_generator():
    num = random.randint(MAP_START, MAP_END)
    return num

def reset():
    return {
        'agent_1' : {
            'x' : random_coor_generator(),
            'y' : random_coor_generator(),
            'hp' : 100,
            'shoot_cd' : 0
        },
        'agent_2' : {
            'x' : random_coor_generator(),
            'y' : random_coor_generator(),
            'hp' : 100,
            'shoot_cd' : 0
        },
        'projectiles' : {}
    }

def step(state, actions):

    reward = {'agent_1' : 0, 'agent_2' : 0}

    global projectile_count 
    global time_now_1
    global time_now_2

    done = False

    for key, action in actions.items():

        if state[key]['shoot_cd'] > 0 :
            state[key]['shoot_cd'] -= 1

        dx = max(-MOVE_CAPPED_AT, min(MOVE_CAPPED_AT, action['dx']))
        dy = max(-MOVE_CAPPED_AT, min(MOVE_CAPPED_AT, action['dy']))

        state[key]['x'] += dx
        state[key]['y'] += dy

        state[key]['x'] = min(max(MAP_START, state[key]['x']), MAP_END)
        state[key]['y'] = min(max(MAP_START, state[key]['y']), MAP_END)

        if action['shoot'] == 1 and state[key]['shoot_cd'] <= 0 :
            state['projectiles'][projectile_count] = {
                'owner' : key,
                'x' : state[key]['x'],
                'y' : state[key]['y'],
                'vx' : action['shoot_dx'],
                'vy' : action['shoot_dy'],
            }
            projectile_count += 1
            state[key]['shoot_cd'] = SHOOT_CD

    projectiles_to_dispose = []

    for key, proj in state['projectiles'].items():
        proj['x'] += SPEED * proj['vx']
        proj['y'] += SPEED * proj['vy']

        if proj['x'] > MAP_END or proj['y'] > MAP_END or proj['x'] < MAP_START or proj['y'] < MAP_START:
            projectiles_to_dispose.append(key)
            continue

        if proj['owner'] == 'agent_1':
            target = 'agent_2'
        else:
            target = 'agent_1'

        if abs(proj['x'] - state[target]['x']) < HIT_RADII and abs(proj['y'] - state[target]['y']) < HIT_RADII and state[target]['hp'] > 0:
            state[target]['hp'] -= DAMAGE
            reward[proj['owner']] += 10

            projectiles_to_dispose.append(key)

            if state[target]['hp'] <= 0:

                reward[proj['owner']] += 100
                reward[target] -= 100
                done = True
                break

    for proj_key in projectiles_to_dispose:
        state['projectiles'].pop(proj_key, None)

    return state, reward, done

state = reset()

for _ in range(1000):
    actions = {
        'agent_1':
        {   
            "dx": random.randint(-5, 5),
            "dy": random.randint(-5, 5),
            "shoot": random.choice([0, 1]),
            "shoot_dx": random.choice([-1, 1]),
            "shoot_dy": random.choice([-1, 1])
        },

        'agent_2':
        {
            "dx": random.randint(-5, 5),
            "dy": random.randint(-5, 5),
            "shoot": random.choice([0, 1]),
            "shoot_dx": random.choice([-1, 1]),
            "shoot_dy": random.choice([-1, 1])
        }
    }

    state, reward, done = step(state, actions)
    print(state)
    if done:
        break
