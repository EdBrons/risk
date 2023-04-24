import numpy as np 
from enum import Enum, auto
from maps import default_map, default_graph

ARMIES = 0
OWNER = 1 
NO_OWNER = -1 
MAX_ARMIES = 30                 #Just for the observation_space not in the logic of the game 

class AttackRes(Enum):
    WON = 0
    UNDECIDED = auto()
    FAILED = auto()

class Move(Enum):
    INVALID = 0
    VALID = auto()

def new_game(n_players): 
    n_territories = len(default_graph.keys())
    initial_territories = np.array([np.array([0,-1])] * n_territories)
    return RiskState(0, [ _ for _ in range(n_players) ], initial_territories )

class RiskState:
    def __init__(self, current_player, active_players, territories):
        self.current_player = current_player
        self.active_players = active_players
        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.territories = territories 
        self.done = False 

        #Initialize the board (distribute territories randomly with one army in each)
        self.setup()



    #PHASES OF A TURN 
    #---------------------------------------------------

   

    def recruit(self, territory):
        """
        First thing players can do at the beginning of a turn (place armies in a territory)
        """
        if self.is_valid_recruit(territory):
            self.territories[territory, ARMIES] += 1
            return True

        else:
            print("INVALID RECRUIT")
            return False 
            

    def attack(self, frm, to):
        #TODO: Remember that move will have three thngs (from, to, quantity)
        if self.is_valid_attack(frm, to):
            res = self.do_attack(frm, to)
            #Check if game is over 
            defender = self.territories[to, OWNER]
            if len(self.get_player_territories(defender)) == 0:
                self.active_players.remove(defender)
                if len(self.active_players) == 1:
                    self.done = True
            return res

        else:
            print("INVALID ATTACK")
            return False 

    def reinforce(self, frm, to, n_armies):
        #move is the same as in first_attack 
        if self.is_valid_reinforce(frm, to, n_armies):
            self.territories[frm, ARMIES] += n_armies
            self.territories[to, ARMIES] -= n_armies
        else: 
            #TODO: smth to give a negative reward 
            print("INVALID REINFORCE")
            pass
    

    #---------------------------------------------------
   
    def armies_in_territory(self, territory):
        return self.territories[territory, OWNER]

    def max_borders(self):
        c_max = float('-inf')
        for country in self.graph:
            c_max = max(c_max, len(self.graph[country]))
        return c_max

    def get_next_player(self):
        n_players = self.n_players()
        for i in range(n_players):
            if self.active_players[i] == self.current_player:
                return self.active_players[(i + 1) % n_players]
            
            
    def n_recruits(self, player):
        """
        Returns the number of armies a player can recruit on their turn
        """
        my_territories = np.where(self.territories[:, 1] == player)[0]
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

    def is_valid_attack(self, frm, to):
        return (
            self.territories[frm, ARMIES] > 1
            and self.territories[frm, OWNER] == self.current_player
            and self.territories[to, OWNER] != self.current_player
            and to in self.graph[frm]
        )

    def is_valid_recruit(self, territory):
        return self.territories[territory, OWNER] == self.current_player
      
    def is_valid_reinforce(self, frm, to, n_armies):
        """We can reinforce an attack if:
            - we have more armies than those we want to move in our territory 
            - we are not exceeding the maximum capacity of armies in a territory 
            - we own both the current territory and the territory we want to move armies to
            - the territory we want to move to is adjacent to the current territory 
        """
        return(
            self.territories[frm, ARMIES] > n_armies
            and self.territories[frm, OWNER] == self.current_player
            and self.territories[to, OWNER] == self.current_player
            and to in self.graph[frm]
        )
    
    def do_attack(self, frm, to):
        self.territories

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
        a_rolls = np.sort(np.random.randint(1, 7, attacker_armies))[::-1]
        d_rolls = np.sort(np.random.randint(1, 7, defender_armies))[::-1]

        for i in range(min(a_rolls.shape[0], d_rolls.shape[0])):
            if a_rolls[i] > d_rolls[i]:
                max_defender_armies -= 1
            else:
                attacker_armies -= 1
                max_attacker_armies -= 1

        if max_defender_armies == 0:
            self.territories[frm, ARMIES] = max_attacker_armies - attacker_armies
            self.territories[to, ARMIES] = attacker_armies
            self.territories[to, OWNER] = attacker_id
            result = AttackRes.WON 
        elif max_attacker_armies <= 1:
            self.territories[frm, ARMIES] = max_attacker_armies
            result = AttackRes.FAILED
        else:
            self.territories[frm, ARMIES] = max_attacker_armies
            self.territories[to, ARMIES] = max_defender_armies
            result = AttackRes.UNDECIDED

        return result
    
    def get_borders(self, territory):
        return self.graph[territory]
    
    def available_attacks(self, territory):
        borders = self.get_borders(territory)
        for country in borders:
            if self.territories[country, OWNER] == self.current_player:
                borders.remove(country)
        return borders 

    # Methods to set up te game
    # --------------------------------------------------------------------

    def setup(self):
        self.claim_territories()

    def get_player_territories(self, player_id):
        """Returns the territories owned by a player"""
        return np.where(self.territories[:, 1] == player_id)[0]
    def get_player_army_count(self, player_id):
        """Returns the army count for a given player"""
        return self.territories[ self.territories[:, 1] == player_id ][:, 0].sum()
    
    def claim_territories(self):
        order = np.resize(np.arange(self.n_players()), self.n_territories())
        np.random.shuffle(order)
        self.territories[:, 0] = np.ones(self.n_territories())
        self.territories[:, 1] = order

    def get_setup_armies(self):
        """Follows the rules of the game"""
        players_to_initial_armies = { 2: 40, 3: 35, 4: 30, 5: 25, 6: 20 }
        return players_to_initial_armies[self.n_players()]
    
    def setup_armies(self):
        armies_to_place_base = self.get_setup_armies()
        for p in range(self.n_players()):
            armies_to_place = armies_to_place_base - len(self.get_player_territories(p))
            my_territories = np.isin(element=self.territories[:, 1], test_elements=p)
            army_placement = np.ones(my_territories.sum())
            for _ in range(armies_to_place):
                army_placement[np.random.randint(army_placement.shape[0])] += 1
            self.territories[my_territories, 0] = army_placement

    def n_players(self):
        return len(self.active_players)

    def n_territories(self):
        return self.territories.shape[0]
    # --------------------------------------------------------------------

        

