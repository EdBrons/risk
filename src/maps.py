default_graph = {
    0:[1, 3, 35], 1:[0, 2, 3, 4], 2:[5, 1, 4, 23], 3:[0, 4, 1, 6], 4:[1, 2, 3, 5, 6, 7],
    5:[2, 4, 7], 6:[3, 4, 7, 8], 7:[5, 4, 6, 8], 8:[6, 7, 9], 9:[8, 10, 11],
    10:[9, 12, 11, 13], 11:[10, 12, 9], 12:[10, 11], 13:[10, 14, 16, 28, 29, 15],
    14:[13, 15, 28, 30], 15:[13, 16, 17, 14, 30, 18], 16:[13, 15, 17], 17:[16, 15, 18],
    18:[17, 15], 19:[41, 20, 21], 20:[22, 21, 19], 21:[22, 19, 20], 22:[20, 21],
    23:[2, 24, 25], 24:[23, 25, 27, 29], 25:[23, 27, 26, 24], 26:[25, 27, 28, 30, 31, 32],
    27:[26, 28, 29, 25, 24], 28:[29, 27, 26, 30, 13, 14], 29:[13, 28, 27, 24],
    30:[31, 40, 14, 15, 26, 28], 31:[32, 30, 26, 40, 39], 32:[31, 26, 33, 39],
    33:[32, 39, 37, 34, 36], 34:[33, 36, 35], 35:[38, 34, 36, 0], 36:[35, 34, 33, 37],
    37:[36, 38, 39, 33, 35], 38:[35, 37], 39:[31, 37, 33, 41, 40, 32], 40:[39, 41, 31, 30],
    41:[39, 40, 19]
}

default_continent_rewards = {"Europe":5, "N_America":5, "Africa":3, "Australia":2, "Asia":7, "S_America":2}

default_continents = {
    "Europe":[23, 24, 25, 26, 27, 28, 29],
    "N_America":[0, 1, 2, 3, 4, 5, 6, 7, 8],
    "Africa":[14, 18, 13, 15, 16, 17],
    "Australia":[19, 20, 21, 22],
    "Asia":[30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41],
    "S_America":[9, 12, 10, 11]
}

default_names = [
#North America
    "Alaska", "NW_Territory", "Greenland", "Alberta",
    "Ontario", "Quebec", "W_US", "E_US", "C_America",
#South America
    "Venezuela", "Brazil", "Peru", "Argentina",
#Africa
    "N_Africa", "Egypt", "E_Africa", "Congo", "S_Africa", "Madagascar",
#Australia
    "Indonesia", "New_Guinea", "W_Australia", "E_Australia",
#Europe
    "Iceland", "Great_Britain", "Scandanavia",
    "Ukraine", "N_Europe", "S_Europe", "W_Europe",
#Asia
    "Mid_East", "Afghanistan", "Ural", "Siberia",
    "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia",
    "Japan", "China", "India", "Siam"
]

def default_map():
    return (default_graph, default_continents, default_continent_rewards, default_names)