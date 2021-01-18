import redis
import argparse
import json
import hashlib
import os
import xmlrpc.client
import algorithm
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recover Redis with the help of the car locator')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    parser.add_argument('-n', '--nonce', type=int, help='Redis recovery nonce')
    args = parser.parse_args()
    
    path = os.path.split(__file__)[0]
    if len(path) > 0:
        path += '/'
    config = json.load(open(f'{path}config.json', 'r'))
    locator_recover_script = open(f'{path}locator_recover.lua', 'r').read().encode('utf8')
    locator_recover_script_sha = hashlib.sha1(locator_recover_script).hexdigest()
    
    if args.debug:
        proxy = xmlrpc.client.ServerProxy(f"http://{config['locator_addr']['host']}:{config['locator_addr']['port']}")
        car_map = [[tuple(pos) for pos in poss] for poss in proxy.locate_cars()]
    else:
        proxy = xmlrpc.client.ServerProxy(f"http://{config['camera_addr']['host']}:{config['camera_addr']['port']}")
        image = np.array(proxy.take_photo(), dtype=np.uint8)
        car_map = algorithm.locate_cars(image, config['car_num'], config['row_num'], config['col_num'])

    def is_valid(pos):
        return pos[0] >= 0 and pos[0] < config['row_num'] and pos[1] >= 0 and pos[0] < config['col_num']

    r = redis.Redis(config['redis_addr']['host'], config['redis_addr']['port'])
    for car_id, poss in enumerate(car_map, 1):
        car_id = -car_id
        if len(poss) == 1:
            pos = poss[0]
            poss = [(pos[0] + offset[0], pos[1] + offset[1]) for offset in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]]
            poss = list(filter(is_valid, poss))
        r.evalsha(locator_recover_script_sha, 0, car_id, args.nonce, config['car_num'],
                  *[f'({pos[0]},{pos[1]})' for pos in poss])
