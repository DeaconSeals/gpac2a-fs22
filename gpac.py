import random
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.path as mpath

GHOST_ACTIONS = {'up':(0,1), 'right':(1,0), 'down':(0,-1), 'left':(-1,0)}
PAC_ACTIONS = {'hold':(0,0)}
PAC_ACTIONS.update(GHOST_ACTIONS)

# pac-man icon creation
pac_vertices = deepcopy(mpath.Path.unit_circle().vertices)
pac_codes = deepcopy(mpath.Path.unit_circle().codes)
pac_vertices[5] = [0,0]
pac_vertices[6] = [0,0]
pac_vertices[7] = [0,0]
PAC_ICON = mpath.Path(vertices=pac_vertices,codes=pac_codes)
# ghost icon creation
fin_depth = 0.5
ghost_vertices = deepcopy(mpath.Path.unit_circle().vertices)
ghost_codes = deepcopy(mpath.Path.unit_circle().codes)
ghost_vertices[1] = [0.25,-fin_depth]
ghost_vertices[2] = [0.5, -1]
ghost_vertices[3] = [0.75, -fin_depth]
ghost_vertices[4] = [1, -1]
ghost_vertices[5] = [1, 0]
ghost_vertices[19] = [-1, -1]
ghost_vertices[20] = [-0.75, -fin_depth]
ghost_vertices[21] = [-0.5, -1]
ghost_vertices[22] = [-0.25, -fin_depth]
ghost_vertices[23] = [0, -1]
ghost_codes[1] = 2
ghost_codes[2] = 2
ghost_codes[3] = 2
ghost_codes[4] = 2
ghost_codes[5] = 2
ghost_codes[6] = 2
ghost_codes[19] = 2
ghost_codes[20] = 2
ghost_codes[21] = 2
ghost_codes[22] = 2
ghost_codes[23] = 2
GHOST_ICON = mpath.Path(vertices=ghost_vertices,codes=ghost_codes)

class GPacGame():
    def __init__(self, game_map, pill_density=0.1, fruit_prob=0.2, fruit_score=10, time_multiplier=2, num_ghosts=3, num_pacs=1, pill_spawn = 'stochastic', **kwargs):
        assert len(game_map) > 0 and min([len(col) for col in game_map]) > 0, "ERROR: MAP MUST BE 2 DIMENSIONAL"
        self.map = game_map[:][:]
        self.width = len(self.map)
        self.height = max([len(col) for col in self.map])
        self.players = {'m': ()}
        for pac in range(num_pacs-1):
            self.players[f'm{pac}'] =  ()
        for ghost in range(num_ghosts):
            self.players[f'{ghost}'] = ()
        self.pill_density = pill_density
        self.fruit_prob = fruit_prob
        self.fruit_score = fruit_score
        self.time_multiplier = time_multiplier
        self.pill_spawn = pill_spawn
        self.reset()

    def reset(self):
        # spawn players
        for player in self.players:
            if 'm' in player:
                self.players[player] = (0, len(self.map[0])-1)
            else:
                self.players[player] = (len(self.map)-1,0)
        self.pills_consumed = 0
        self.pills = set()

        placement_strategies = {'stochastic', 'linear', 'manhattan'}
        assert self.pill_spawn in placement_strategies, f"ERROR: UNRECOGNIZED PILL SPAWN STRATEGY {self.pill_spawn} BUT EXPECTED {placement_strategies}"
        # generate pill placement
        if self.pill_spawn.casefold() == 'stochastic':
            for x in range(len(self.map)):
                for y in range(len(self.map[x])):
                    # skip spawning location of pac-man and ghosts
                    if (x,y) in self.players.values():
                        continue
                    if self.map[x][y] == 0 and random.random() <= self.pill_density:
                        self.pills.add((x,y))
            if len(self.pills) == 0: # failsafe logic to guarantee pill placement
                forbidden_locations = {self.players[player] for player in self.players}
                available_locations = list()
                for x in range(len(self.map)):
                    for y in range(len(self.map[x])):
                        if self.map[x][y] == 0 and (x, y) not in forbidden_locations:
                            available_locations.append((x, y))
                assert len(available_locations) > 0, "ERROR: NO VALID PILL LOCATIONS"
                self.pills.add(random.choice(available_locations))
        elif self.pill_spawn.casefold() == 'linear' or self.pill_spawn.casefold() == 'manhattan':
            forbidden_locations = {self.players[player] for player in self.players}
            available_locations = list()
            for x in range(len(self.map)):
                for y in range(len(self.map[x])):
                    if self.map[x][y] == 0 and (x, y) not in forbidden_locations:
                        available_locations.append((x, y))
            assert len(available_locations) > 0, "ERROR: NO VALID PILL LOCATIONS"
            pill_freq = max(1,int(round(1/self.pill_density)))
            if self.pill_spawn.casefold() == 'manhattan':
                available_locations = sorted(available_locations, key=lambda location: location[0]+location[1])
            for i in range(len(available_locations)):
                if i%pill_freq==0:
                    self.pills.add(available_locations[i])

        self.fruit_consumed = 0
        self.fruit_location = None
        self.time = int(self.width*self.height*self.time_multiplier)
        self.score = 0
        self.bonus = 0
        self.gameover = False
        self.graveyard = set()
        self.registered_actions = dict()
        self.possible_actions = dict()

        # initialize new world file log
        self.log = [f'{self.width}', f'{self.height}']
        for player, location in self.players.items():
            self.log.append(f'{player} {location[0]} {location[1]}')
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] == 1:
                    self.log.append(f'w {x} {y}')
        for x, y in self.pills:
            self.log.append(f'p {x} {y}')
        self.log.append(f't {self.time} {self.score}')

    def update_score(self):
        self.score = int(100*self.pills_consumed/(self.pills_consumed+len(self.pills))) + self.bonus

    def manage_fruit(self):
        # check if fruit already exists and whether or not one should spawn this turn
        if self.fruit_location == None and random.random() <= self.fruit_prob:
            forbidden_locations = self.pills | {self.players[player] for player in self.players if 'm' in player}
            available_locations = list()
            for x in range(len(self.map)):
                for y in range(len(self.map[x])):
                    if self.map[x][y] == 0 and (x, y) not in forbidden_locations:
                        available_locations.append((x, y))

            if len(available_locations) == 0:
                self.fruit_location = None
            else:
                self.fruit_location = random.choice(available_locations)
                # log spawn of fruit
                self.log.append(f'f {self.fruit_location[0]} {self.fruit_location[1]}')

    def get_actions(self, player='m'):
        if player not in self.possible_actions:
            available_actions = list()
            if 'm' in player:
                candidate_actions = PAC_ACTIONS
            else:
                candidate_actions = GHOST_ACTIONS
            current_location = self.players[player]
            for action in candidate_actions:
                x, y = current_location
                x_shift, y_shift = PAC_ACTIONS[action]
                if  0 <= x+x_shift < len(self.map) and 0 <= y+y_shift < len(self.map[x]) and self.map[x+x_shift][y+y_shift] == 0:
                    available_actions.append(action)
            self.possible_actions[player] = available_actions

        return self.possible_actions[player]

    def get_observations(self, actions, player='m'):
        observations = list()
        current_location = self.players[player]
        fruit_copy = self.fruit_location
        for action in actions:
            x, y = current_location
            x_shift, y_shift = PAC_ACTIONS[action]
            x, y = x+x_shift, y+y_shift
            state = {'walls': self.map[:][:], 'pills':list(self.pills), 'fruit':fruit_copy, 'players':self.players.copy()}
            state['players'][player] = (x, y)
            observations.append(state)
        return observations 

    def register_action(self, action, player='m'):
        self.registered_actions[player] = action

    def step(self):
        self.time -= 1
        old_locations = self.players.copy()
        touched_pills = set()
        touched_fruit = False
        
        # update player locations from registered actions
        for player, action in self.registered_actions.items():
            if player in self.graveyard:
                continue # skip deceased pacs
            assert action in self.get_actions(player=player), f'ERROR: INVALID ACTION ({action}) FOR PLAYER {player}'
            x, y = self.players[player]
            if 'm' in player:
                x_shift, y_shift = PAC_ACTIONS[action]
                self.players[player] = pac = (x+x_shift, y+y_shift)
                if pac in self.pills:
                    touched_pills.add(pac)
                touched_fruit = pac == self.fruit_location
            else:
                x_shift, y_shift = GHOST_ACTIONS[action]
                self.players[player] = (x+x_shift, y+y_shift)
        self.registered_actions.clear()
        self.possible_actions.clear()

        # detect collsions between pacs and ghosts
        pacs = {player for player in self.players if 'm' in player}
        ghosts = [player for player in self.players if player not in pacs]
        for pac in pacs:
            if pac in self.graveyard:
                continue
            # detect direct collision
            if self.players[pac] in {self.players[ghost] for ghost in ghosts}:
                self.graveyard.add(pac)
                continue
            # detect collsion via trading locations
            for ghost in ghosts:
                if self.players[pac] == old_locations[ghost] and old_locations[pac] == self.players[ghost]:
                    self.graveyard.add(pac)
        
        if self.graveyard == pacs:
            self.gameover = True
        else:
            if touched_pills:
                for pill in touched_pills:
                    self.pills_consumed += 1
                    self.pills.remove(pill)
                self.update_score()
            if touched_fruit:
                self.fruit_consumed += 1
                self.fruit_location = None
                self.bonus += self.fruit_score
                self.update_score()
            if len(self.pills) == 0:
                self.gameover = True
                self.bonus += int(100*self.time/int(self.width*self.height*self.time_multiplier))
                self.update_score()
            elif self.time <= 0:
                self.gameover = True
            
        # update log
        for player, location in self.players.items():
            self.log.append(f'{player} {location[0]} {location[1]}')
        self.manage_fruit() # do things with fruit
        self.log.append(f't {self.time} {self.score}')

def render_start(log, speed=1):
    '''A so-so visualization function that renders the first frame of GPac'''
    width = int(log[0])
    height = int(log[1])
    pltmaze = [[1 for __ in range(width)] for _ in range(height)]
    players = dict()
    log_idx = 2
    while log[log_idx][0] != 'w':
        elements = log[log_idx].split(' ')
        coords = (int(elements[1]), int(elements[2]))
        players[elements[0]] = coords
        log_idx += 1

    while log[log_idx][0] == 'w':
        elements = log[log_idx].split(' ')
        x, y = int(elements[1]), int(elements[2])
        pltmaze[y][x] = 0
        log_idx += 1
    pills = set()
    while log[log_idx][0] == 'p':
        elements = log[log_idx].split(' ')
        coords = (int(elements[1]), int(elements[2]))
        pills.add(coords)
        log_idx += 1
    fruit = None

    fig, ax = plt.subplots()
    ax.matshow(pltmaze, origin='lower')

    temp = list(pills)
    ax.scatter([i[0] for i in temp], [i[1] for i in temp])
    
    temp = [players[player] for player in players if 'm' in player]
    ax.scatter([i[0] for i in temp], [i[1] for i in temp], 300, marker=PAC_ICON)

    temp = [players[player] for player in players if 'm' not in player]
    ax.scatter([i[0] for i in temp], [i[1] for i in temp], 300, marker=GHOST_ICON)

    plt.xticks(range(len(pltmaze[0])))
    plt.yticks(range(len(pltmaze)))
    plt.gca().set_xticks([x - 0.5 for x in plt.gca().get_xticks()][1:], minor='true')
    plt.gca().set_yticks([y - 0.5 for y in plt.gca().get_yticks()][1:], minor='true')
    plt.grid(which='minor')
    plt.show()

# test game with random agents if you run this file
if __name__ == "__main__":
    size = 21
    game_map = [[1 for __ in range(size)] for _ in range(size)]
    for i in range(size):
        game_map[0][i] = game_map[i][0] = game_map[size//2][i] = game_map[i][size//2] = game_map[size-1][i] = game_map[i][size-1] = 0
    game = GPacGame(game_map)
    while not game.gameover:
        [game.register_action(random.choice(game.get_actions(player = player)), player = player) for player in game.players]
        game.step()
    [print(line) for line in game.log]
