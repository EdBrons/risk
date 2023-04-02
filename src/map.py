class Tile:
    def __init__(self, name):
        self.name = name
        self.armies = 1
        self.owner = 0
    def print(self):
        print(f'Name: "{self.name}" Armies: {self.armies} Owner: "{self.owner}"')
class Map:
    def __init__(self, graph):
        self.vertices = sorted(list(graph.keys()))
        self.graph = graph
        self.tiles = {}
        for name in self.vertices:
            self.tiles[name] = Tile(name)
    def get_tile(self, tilename):
        return self.tiles[tilename]
    def get_adjacent_tiles(self, tilename):
        return [ self.tiles[n] for n in self.graph[tilename] ]
    def get_tiles_owned_by(self, player):
        return [ t for n, t in self.tiles.items() if t.owner == player ]
    def print(self):
        for tile in self.tiles.values():
            tile.print()

classic_map_graph = {
    'Alaska': ['Alberta', 'Northwest Territory', 'Kamchatka'],
    'Alberta': ['Alaska', 'Northwest Territory', 'Ontario', 'Western United States'],
    'Central America': ['Eastern United States', 'Western United States', 'Venezuela'],
    'Eastern United States': ['Central America', 'Western United States', 'Quebec', 'Ontario'],
    'Greenland': ['Northwest Territory', 'Ontario', 'Quebec', 'Iceland'],
    'Northwest Territory': ['Alaska', 'Greenland', 'Alberta', 'Ontario'],
    'Ontario': ['Northwest Territory', 'Greenland', 'Alberta', 'Western United States', 'Eastern United States', 'Quebec'],
    'Quebec': ['Ontario', 'Eastern United States', 'Greenland'],
    'Western United States': ['Alberta', 'Ontario', 'Eastern United States', 'Central America'],
    'Argentina': ['Brazil', 'Peru'],
    'Brazil': ['Argentina', 'Peru', 'Venezuela', 'North Africa'],
    'Peru': ['Venezuela', 'Brazil', 'Argentina'],
    'Venezuela': ['Central America', 'Brazil', 'Peru'],
    'Great Britain': ['Iceland', 'Scandinavia', 'Northern Europe', 'Western Europe'],
    'Iceland': ['Greenland', 'Great Britain', 'Scandinavia'],
    'Northern Europe': ['Great Britain', 'Scandinavia', 'Ukraine', 'Western Europe'],
    'Scandinavia': ['Iceland', 'Great Britain', 'Northern Europe', 'Ukraine'],
    'Southern Europe': ['Western Europe', 'Northern Europe', 'Ukraine', 'Middle East', 'Egypt', 'North Africa'],
    'Ukraine': ['Scandinavia', 'Northern Europe', 'Southern Europe', 'Middle East', 'Afghanistan', 'Ural'],
    'Western Europe': ['Great Britain', 'Northern Europe', 'Southern Europe', 'North Africa'],
    'Congo': ['North Africa', 'East Africa', 'South Africa'],
    'East Africa': ['Egypt', 'Congo', 'South Africa', 'Madagascar', 'Middle East', 'North Africa'],
    'Egypt': ['Southern Europe', 'Middle East', 'East Africa', 'North Africa'],
    'Madagascar': ['East Africa', 'South Africa'],
    'North Africa': ['Brazil', 'Western Europe', 'Southern Europe', 'Egypt', 'East Africa', 'Congo'],
    'South Africa': ['Congo', 'East Africa', 'Madagascar']
}

test_graph = {
    'Territory 1': ['Territory 2', 'Territory 3', 'Territory 4'],
    'Territory 2': ['Territory 1', 'Territory 3', 'Territory 4'],
    'Territory 3': ['Territory 1', 'Territory 2', 'Territory 4'],
    'Territory 4': ['Territory 2', 'Territory 3', 'Territory 1']
}

def nm_grid(n, m):
    for x in range(n):
        for y in range(m):
            pass