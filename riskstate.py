import numpy as np
from enum import Enum, auto
from maps import default_map, default_graph

ARMIES = 0
OWNER = 1
NO_OWNER = -1

class AttackRes(Enum):
    WON = 0
    UNDECIDED = auto()
    FAILED = auto()

class Move(Enum):
    INVALID = 0
    VALID = auto()

def new_game(n_players):
    n_territories = len(default_graph.keys())
    
    initial_territories = np.array([np.array([0, -1])] * n_territories)
    return RiskState( 0, 0, [ _ for _ in range(n_players) ], initial_territories )

class RiskState:

    def __init__(self, turn, current_player, active_players, territories ):
        self.turn = turn
        self.current_player = current_player
        self.active_players = active_players
        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.territories = territories
    def step(self, move):
        pass
    def finished(self):
        return False
    def n_territories(self):
        return self.territories.shape[0]
    def get_next_player(self):
        n_players = len(self.active_players)
        if n_players == 0:
            return 0
        if self.current_player not in self.active_players:
            return 0
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
    def is_valid_attack(self, player, frm, to):
        return (
            self.territories[frm, ARMIES] > 1
            and self.territories[frm, OWNER] == player
            and self.territories[to, OWNER] != player
            and to in self.graph[frm]
        )
    def do_attack(self, frm, to):
        territories = self.territories.copy()

        # sanity checks
        assert territories[frm, OWNER] != territories[to, OWNER]
        assert territories[frm, ARMIES] >= 2
        assert territories[to, ARMIES] > 0
        assert to in self.graph[frm]

        attacker_armies = min(3, territories[frm, ARMIES] - 1)
        attacker_id = territories[frm, OWNER]
        max_attacker_armies = territories[frm, ARMIES]
        max_defender_armies = territories[to, ARMIES]
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
            territories[frm, ARMIES] = max_attacker_armies - attacker_armies
            territories[to, ARMIES] = attacker_armies
            territories[to, OWNER] = attacker_id
            result = AttackRes.WON 
        elif max_attacker_armies <= 1:
            territories[frm, ARMIES] = max_attacker_armies
            result = AttackRes.FAILED
        else:
            territories[frm, ARMIES] = max_attacker_armies
            territories[to, ARMIES] = max_defender_armies
            result = AttackRes.UNDECIDED

        return (result, territories)

class SetupPhase(RiskState):
    def __init__(self, turn, current_player, active_players, n_armies, territories):
        super().__init__(turn, current_player, active_players, territories)
        self.n_armies = n_armies
    def action_space(self):
        # return (self.territories[:, OWNER] == NO_OWNER or self.territories[:, OWNER] == self.current_player).nonzero()
        return list(range(self.n_territories()))
    def is_valid(self, move):
        return move in self.action_space() and (self.territories[move, OWNER] == NO_OWNER or self.territories[move, OWNER] == self.current_player)
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        new_territories[move, OWNER] = self.current_player
        new_territories[move, ARMIES] += 1
        new_n_armies = self.n_armies - 1
        new_player = self.get_next_player()
        if new_n_armies == 0:
            return ( Move.VALID, RecruitmentPhase( self.turn + 1, new_player, self.active_players, new_territories, self.n_recruits(new_player) ) )
        else:
            return ( Move.VALID, SetupPhase( self.turn + 1, new_player, self.active_players, new_territories, new_n_armies ) )

class RecruitmentPhase(RiskState):
    def __init__(self, turn, current_player, active_players, territories, n_recruits):
        super().__init__(turn, current_player, active_players, territories)
        self.n_recruits = n_recruits
    def action_space(self):
        # return (self.territories[:, OWNER] == self.current_player).nonzero()
        return list(range(self.n_territories()))
    def is_valid(self, move):
        return self.territories[move, OWNER] == self.current_player
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        new_territories[move, ARMIES] += 1
        new_n_recruits = self.n_recruits - 1
        if new_n_recruits == 0:
            return ( Move.VALID, FirstAttackPhase( self.turn + 1, self.current_player, self.active_players, new_territories ) )
        else:
            return ( Move.VALID, RecruitmentPhase( self.turn, self.current_player, self.active_players, new_territories, new_n_recruits ) )

# some code shared between the attack phases
def handle_attack_res(phase, frm, to, res, new_territories):
    if res == AttackRes.FAILED:
        return ( Move.VALID, FortifyPhase1(phase.turn, phase.current_player, phase.active_players, phase.territories) )
    elif res == AttackRes.UNDECIDED:
        if new_territories[frm, ARMIES] > 1:
            return ( Move.VALID, ContinueAttackPhase(phase.turn, phase.current_player, phase.active_players, new_territories, frm, to) )
        else:
            return ( Move.VALID, FortifyPhase1(phase.turn, phase.current_player, phase.active_players, phase.territories) )
    elif res == AttackRes.WON:
        return ( Move.VALID, ReinforcePhase(phase.turn, phase.current_player, phase.active_players, new_territories, frm, to) )
    raise ValueError("res must be an AttackRes.")

class FirstAttackPhase(RiskState):
    def __init__(self, turn, current_player, active_players, territories):
        super().__init__(turn, current_player, active_players, territories)
    def action_space(self):
        return (list(range(self.n_territories())), list(range(self.n_territories())))
    def is_valid(self, move): # move = (frm, to)
        frm, to = move
        return self.is_valid_attack(self.current_player, frm, to)
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        frm, to = move
        res, new_territories = self.do_attack(frm, to)
        return handle_attack_res(self, frm, to, res, new_territories)

class ContinueAttackPhase(RiskState):
    def __init__(self, turn, current_player, active_players, territories, frm, to):
        super().__init__(turn, current_player, active_players, territories)
        self.frm = frm
        self.to = to
    def action_space(self):
        return [ True, False ]
    def is_valid(self, move):
        return move in self.action_space()
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        res, new_territories = self.do_attack(self.frm, self.to)
        return handle_attack_res(self, self.frm, self.to, res, new_territories)

class ReinforcePhase(RiskState):
    def __init__(self, turn, current_player, active_players, territories, frm, to):
        super().__init__(turn, current_player, active_players, territories)
        self.frm = frm
        self.to = to
    def action_space(self):
        return [ True, False ]
    def is_valid(self, move):
        #      make sure move is bool      move is T    check if frm territory has enough units
        return move in self.action_space() and move and self.territories[self.frm, ARMIES] > 1
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        if move:
            new_territories[self.frm, ARMIES] -= 1
            new_territories[self.to, ARMIES] += 1
            return ( Move.VALID, ReinforcePhase(self.turn, self.current_player, self.active_players, new_territories, self.frm, self.to) )
        else:
            if new_territories[self.to, ARMIES] > 1:
                return ( Move.VALID, SubsequentAttackPhase(self.turn, self.current_player, self.active_players, self.territories, self.to) )
            else:
                return ( Move.VALID, FortifyPhase1(self.turn, self.current_player, self.active_players, self.territories) )

class SubsequentAttackPhase(RiskState):
    def __init__(self, turn, current_player, active_players, territories, frm):
        super().__init__(turn, current_player, active_players, territories)
        self.frm = frm
    def action_space(self):
        return list(range(self.n_territories()))
    def is_valid(self, move): # move = (frm, to)
        return self.is_valid_attack(self.current_player, self.frm, move)
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        res, new_territories = self.do_attack(self.frm, move)
        return handle_attack_res(self, self.frm, move, res, new_territories)

class FortifyPhase1(RiskState):
    def __init__(self, turn, current_player, active_players, territories):
        super().__init__(turn, current_player, active_players, territories)
    def action_space(self):
        # return (self.territories[:, OWNER] == self.current_player).nonzero()
        return list(range(self.n_territories()))
    def is_valid(self, move):
        return self.territories[move, OWNER] == self.current_player
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        return ( Move.VALID, FortifyPhase2(self.turn, self.current_player, self.active_players, new_territories, move) )

class FortifyPhase2(RiskState):
    def __init__(self, turn, current_player, active_players, territories, frm):
        super().__init__(turn, current_player, active_players, territories)
        self.frm = frm
    def action_space(self):
        # return (self.territories[:, OWNER] == self.current_player).nonzero()
        return list(range(self.n_territories()))
    def is_valid(self, move):
        return self.territories[move, OWNER] == self.current_player and move in self.graph[self.frm]
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        return ( Move.VALID, FortifyPhase3(self.turn, self.current_player, self.active_players, new_territories, self.frm, move) )

class FortifyPhase3(RiskState):
    def __init__(self, turn, current_player, active_players, territories, frm, to):
        super().__init__(turn, current_player, active_players, territories)
        self.frm = frm
        self.to = to
    def action_space(self):
        # return (self.territories[:, OWNER] == self.current_player).nonzero()
        return [ True, False ]
    def is_valid(self, move):
        return move in self.action_space() and move and self.territories[self.frm, ARMIES] > 0
    def step(self, move):
        if not self.is_valid(move):
            return ( Move.INVALID, self )
        new_territories = self.territories.copy()
        if move:
            new_territories[self.frm, ARMIES] -= 1
            new_territories[self.to, ARMIES] += 1
            return ( Move.VALID, FortifyPhase3(self.turn, self.current_player, self.active_players, new_territories, self.frm, self.to) )
        else:
            new_player = self.get_next_player()
            n_recruits = self.n_recruits(new_player)
            return ( Move.VALID, RecruitmentPhase(self.turn, new_player, self.active_players, new_territories, n_recruits) )