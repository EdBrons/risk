import random
from map import Map

class Game:
    def __init__(self, map, players):
        self.map = map
        self.players = players
    def setup_game(self, randomize_ownership=True, randomize_armies=True):
        # assign ownership
        if randomize_ownership:
            l = self.map.vertices
            random.shuffle(l)
            while len(l) > 0:
                for p in self.players:
                    if l: self.map.get_tile(l.pop()).owner = p
        # place armies
        if randomize_armies:
            for p in self.players:
                armies = 20 # change this in future
                while armies > 0:
                    t = random.choice(self.map.get_tiles_owned_by(p))
                    t.armies += random.randint(1, armies+1)
                    armies -= t.armies
        else:
            raise "Unimplemented mother fucker"
    def battle(self, player1, player2): 
        pass 

test_graph = {
    'Territory 1': ['Territory 2', 'Territory 3', 'Territory 4'],
    'Territory 2': ['Territory 1', 'Territory 3', 'Territory 4'],
    'Territory 3': ['Territory 1', 'Territory 2', 'Territory 4'],
    'Territory 4': ['Territory 2', 'Territory 3', 'Territory 1']
}
m = Map(test_graph)
Test = Game(m, ["P1", "P2", "P3"])
Test.setup_game()
m.print()