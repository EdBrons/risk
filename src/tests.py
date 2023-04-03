import unittest
from risk import Risk
from player import RandomPlayer

class TestRisk(unittest.TestCase):

    def test_players_len(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    
    def n_players(self, n):
        return [ RandomPlayer(i) for i in range(n) ]
    
    def test_min_max_players(self):
        with self.assertRaises(ValueError):
            Risk(self.n_players(1))
        with self.assertRaises(ValueError):
            Risk(self.n_players(7))
    
    def test_random_claim_territories(self):
        r = Risk(self.n_players(2), random_setup=True)
        r.claim_territories()
        t = [ len(r.get_player_territories(i)) for i in range(2) ]
        self.assertListEqual(t, [21, 21])

        r = Risk(self.n_players(6), random_setup=True)
        r.claim_territories()
        t = [ len(r.get_player_territories(i)) for i in range(6) ]
        self.assertListEqual(t, [7, 7, 7, 7, 7, 7])
    
    def test_random_place_armies(self):
        r = Risk(self.n_players(2), random_setup=True)
        r.claim_territories()
        r.place_armies()
        t = [ r.get_player_army_count(i) for i in range(2) ]
        self.assertListEqual(t, [40, 40])

        r = Risk(self.n_players(6), random_setup=True)
        r.claim_territories()
        r.place_armies()
        t = [ r.get_player_army_count(i) for i in range(6) ]
        self.assertListEqual(t, [20, 20, 20, 20, 20, 20])

if __name__ == '__main__':
    unittest.main()