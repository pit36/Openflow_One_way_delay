import numpy as np
#import plotting

#choices: 'latency', 'bw'
def create_matrix(data_map, choice):
    dimension = len(data_map.keys())
    s = (dimension, dimension)
    map = np.zeros(s)
    # with high dpids - order for llist of keys
    keyList_sorted = sorted(list(data_map.keys()))
    # create new object
    i = 0
    keyDict = {}
    for element in keyList_sorted:
        keyDict[element] = i
        i = i + 1
    for key1 in data_map.keys():
        for key2 in data_map[key1].keys():
            map[keyDict[key1]][keyDict[key2]] = data_map[key1][key2][choice][-1]['value']
            #print(map)
            # for datapathIDs
            #map[key1-1][key2-1] = data_map[key1][key2][choice][-1]['value']
            # TODO: FALSCH
    return map










