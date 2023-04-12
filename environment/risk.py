import math
import numpy as np
from enum import Enum, auto
from maps import default_map

ATTACK_WON = 1
ATTACK_UNDECIDED = 0
ATTACK_FAILED = -1

ARMIES = 0
OWNER = 1

class Phase(Enum):
    RECRUITMENT = auto()
    CHOOSE_FIRST_ATTACK = auto()
    CHOOSE_SUBS_ATTACK = auto()
    CONTINUE_ATTACK = auto()
    FORTIFY = auto()


# Taken from https://github.com/civrev/RLRisk/blob/master/rlrisk/environment/risk.py
class Risk:
    def __init__(self, n_players, random_setup = True, max_turns = math.inf):
        """
        n_players - the players to play this game
        random_setup - should the territories be assigned randomly, and armies placed randomly
        max_turns - maximum number of turns for this game
        """
        if n_players < 2 or n_players > 6:
            raise ValueError("2 <= len(players) <= 6")
        self.n_players = n_players

        self.random_setup = random_setup
        self.max_turns = max_turns

        self.turn = 0
        self.current_player = 0
        self.phase = Phase.RECRUITMENT
        self.finished = False

        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.territories = self.make_state()

    def get_state(self):
        return self.territories

    def get_territory_count(self):
        return self.territories.shape[0]
    def get_player_territories(self, player_id):
        return np.where(self.territories[:, 1] == player_id)[0]
    def is_border(self, terr):
        return not np.all(self.territories[self.graph[terr]][OWNER] == self.territories[terr, OWNER])
    def get_border_territories(self, player_id):
        return self.get_player_territories
    def get_player_army_count(self, player_id):
        """Gets total number of armies owned by a player"""
        return self.territories[ self.territories[:, 1] == player_id ][:, 0].sum()
    
    def print_update(self):
        x = [ len(self.get_player_territories(p.id)) for p in self.players ]
        print(self.turn, x)

    def play(self):
        # setup
        self.claim_territories()
        self.setup_armies()
        while not self.finished:
            player_id = self.get_next_player()
            self.print_update()
            self.turn += 1
            self.recruitment_phase(player_id)
            self.attack_phase(player_id)
            if self.winner():
                self.finished = True
                self.print_update()
                print(f'Player {player_id} won!')
                break
            self.fortify_phase(player_id)
            if self.turn > self.max_turns:
                self.finished = True
                break
    def is_player_alive(self, player_id):
        return player_id in self.territories[:, OWNER]
    def winner(self):
        return np.array_equal(self.territories[:, OWNER], np.repeat(self.territories[0, OWNER], self.get_territory_count()))
        self.get_next_player(self)
    def get_next_player(self):
        """
        NOTE: possibility for an infinite loop here maybe
        in future we should do this differently
        """
        self.next_player = (self.next_player + 1) % self.n_players
        if self.is_player_alive(self.next_player):
            return self.next_player
    def setup(self):
        self.claim_territories()
        self.setup_armies()
        self.phase = 0
    def step(self, move = None):
        """
        Executes move, and moves one game step forward
        If move is none, then it doesn't execute a move, just return info
        Returns the next move to be made
        formate (player_id, state, valid_moves)
        """
        if move is not None:
            if self.phase == Phase.RECRUITMENT:
                if self.is_valid_recruitment(self.current_player, move):
                    self.recruitment_step(move)
        if self.phase == Phase.RECRUITMENT:
            return ( self.current_player, self.territories, Phase.RECRUITMENT, self.get_recruitment_moves(self.current_player) )

    def get_recruitment_moves(self, player_id):
        return ( self.get_new_armies(player_id), self.get_player_territories(player_id) )
    def is_valid_recruitment(self, player_id, placement):
        total_armies = sum(placement[:, ARMIES])
        return total_armies <= self.get_new_armies(player_id) and len(set(placement[:, OWNER])) == 1
    def recruitment_step(self, move):
        for _, (territory, armies) in move:
            self.territories[territory, ARMIES] += armies

    def get_new_armies(self, player_id):
        """
        Returns the number of armies a player can recruit on their turn
        """
        my_territories = self.get_player_territories(player_id)
        new_armies = my_territories.shape[0] // 3
        if new_armies < 3:
            new_armies = 3
        for c in self.continents:
            owned = True
            for t in self.continents[c]:
                if t not in my_territories:
                    owned = False
            if owned:
                new_armies += self.continent_rewards[c]
        return new_armies
    def place_armies(self, player_id, n_armies):
        """
        Asks the player to place n_armies
        """
        player = self.players[player_id]
        legal_placements = self.get_player_territories(player_id)
        assert len(legal_placements) > 0
        for _ in range(n_armies):
            t = player.choose_recruitment_territory(self.get_state(), legal_placements)
            if t:
                self.territories[t][ARMIES] += 1
    def recruitment_phase(self, player_id):
        """
        Simulates the recruitment phase
        """
        new_armies = self.get_new_armies(player_id)
        self.place_armies(player_id, new_armies)

    def get_legal_attacks(self, player_id, frm=None):
        """
        Returns an array of pairs of provinces where attacks can be made: (terr_frm, terr_to)
        Will return an empty array if frm has less than 2 units
        To be legal an attack must:
        -originate from a territory owned by the player
        -That territory must have at least 2 armies
        -It must go to an adjacent territory owned by another player
        """
        owned = self.get_player_territories(player_id)
        if frm is None:
            valid_from = owned[np.where(self.territories[owned, ARMIES] > 1)[0]]
        else:
            assert self.territories[frm, OWNER] == player_id
            if self.territories[frm, ARMIES] < 2:
                return []
            valid_from = [ frm ] 
        legal_attacks = []
        for vf_terr in valid_from:
            edges = set(self.graph[vf_terr])
            valid_to = edges - set(owned)
            for vt_terr in valid_to:
                legal_attacks.append((vf_terr, vt_terr))
        return legal_attacks
    def do_attack(self, frm, to):
        # sanity checks
        assert self.territories[frm, OWNER] != self.territories[to, OWNER]
        assert self.territories[frm, ARMIES] >= 2
        assert self.territories[to, ARMIES] > 0
        assert to in self.graph[frm]

        attacker_armies = min(3, self.territories[frm, ARMIES] - 1)
        attacker_id = self.territories[frm, OWNER]
        max_attacker_armies = self.territories[frm, ARMIES]
        max_defender_armies = self.territories[to, ARMIES]
        defender_armies = min(2, max_defender_armies)

        # generate random list of rolls in descending order
        a_rolls = np.random.randint(1, 7, attacker_armies)
        d_rolls = np.random.randint(1, 7, defender_armies)
        a_rolls.sort()
        d_rolls.sort()

        for i in reversed(range(min(a_rolls.shape[0], d_rolls.shape[0]))):
            if a_rolls[i] > d_rolls[i]:
                max_defender_armies -= 1
            else:
                attacker_armies -= 1
                max_attacker_armies -= 1

        if max_defender_armies == 0:
            self.territories[frm, ARMIES] = max_attacker_armies - attacker_armies
            self.territories[to, ARMIES] = attacker_armies
            self.territories[to, OWNER] = attacker_id
            result = ATTACK_WON 
        elif max_attacker_armies == 1:
            self.territories[frm, ARMIES] = max_attacker_armies
            result = ATTACK_FAILED
        else:
            self.territories[frm, ARMIES] = max_attacker_armies
            self.territories[to, ARMIES] = max_defender_armies
            result = ATTACK_UNDECIDED

        return result
    def attack_phase(self, player_id):
        player = self.players[player_id]
        valid_attacks = self.get_legal_attacks(player_id)
        attack = player.choose_attack(self.get_state(), valid_attacks) 
        while attack != False:
            frm = attack[0]
            to = attack[1]
            result = self.do_attack(frm, to)
            if result == ATTACK_FAILED:
                break
            elif result == ATTACK_UNDECIDED:
                if self.territories[frm, ARMIES] < 2:
                    break
                if not player.keep_attacking(self.get_state()):
                    break
            elif result == ATTACK_WON:
                self.reinforce_after_attack(player_id, frm, to)
                attack = player.choose_attack(self.get_state(), self.get_legal_attacks(player_id, to))
    def reinforce_after_attack(self, player_id, from_terr, to_terr):
        player = self.players[player_id]
        movable_armies = self.territories[from_terr, ARMIES] - 1
        self.territories[to_terr, ARMIES] = 1
        for _ in range(movable_armies):
            choice = player.choose_reinforce(self.get_state(), (from_terr, to_terr))
            if choice:
                self.territories[to_terr, ARMIES] += 1
                self.territories[from_terr, ARMIES] -= 1

    # TODO: optimize fortification code, it is the main bottleneck
    def get_valid_fortifications(self, territory):
        if self.territories[territory, ARMIES] < 2:
            return []
        player_id = self.territories[territory][OWNER]
        edges = self.graph[territory]
        return [(territory, t) for t in edges if self.territories[t, OWNER] == player_id ]
    def fortify_phase(self, player_id):
        player = self.players[player_id]
        owned = self.get_player_territories(player_id)
        possible_moves = {}
        for t in owned:
            possible_moves[t] = self.territories[t, ARMIES] - 1
        for t in owned:
            valid_forts = self.get_valid_fortifications(t)
            for _ in range(self.territories[t, ARMIES] - 1):
                f = player.choose_fortify(self.get_state(), valid_forts)
                if f:
                    frm = f[0]
                    to = f[1]
                    self.territories[frm, ARMIES] -= 1
                    possible_moves[frm] -= 1
                    self.territories[to, ARMIES] += 1

    # Setup Stuff
    def make_state(self):
        graph_size = len(self.graph.keys())
        territory = np.array([0, -1])
        territories = np.array([territory] * graph_size)
        return territories
    def claim_territories(self):
        n_players = len(self.players)
        if self.random_setup:
            order = np.resize(np.arange(n_players), self.get_territory_count())
            np.random.shuffle(order)
            self.territories[:, 0] = np.ones(self.get_territory_count())
            self.territories[:, 1] = order
        else:
            raise NotImplementedError("We haven't implemented player choice yet...")
    def setup_armies(self):
        n_players = len(self.players)
        players_to_initial_armies = { 2: 40, 3: 35, 4: 30, 5: 25, 6: 20 }
        armies_to_place_base = players_to_initial_armies[n_players]
        if self.random_setup:
            for p in self.players:
                armies_to_place = armies_to_place_base - len(self.get_player_territories(p.id))
                my_territories = np.isin(element=self.territories[:, 1], test_elements=p.id)
                army_placement = np.ones(my_territories.sum())
                for _ in range(armies_to_place):
                    army_placement[np.random.randint(army_placement.shape[0])] += 1
                self.territories[my_territories, 0] = army_placement
        else:
            raise NotImplementedError("We haven't implemented player choice yet...")