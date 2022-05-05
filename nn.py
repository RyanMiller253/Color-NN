import sys
import numpy as np
import lib
import fileinput
import random
import operator
import configparser
import copy

# Ant class


class Ant:
    def __init__(self, pheromone_map, cities_map, dimension):
        self.cost = 0.0  # cost of ant's current traversal
        self.pheromone_change = []  # list of change in pheromone
        # random starting place for each ant
        self.start = random.randint(0, dimension - 1)
        self.cities_visited = []  # list of cities ant already visited
        # list of cities ant hasn't visited
        self.cities_left_to_visit = [i for i in range(dimension)]
        # add starting city to list of cities visited
        self.cities_visited.append(self.start)
        # remove starting city from list that ant needs to visit
        self.cities_left_to_visit.remove(self.start)
        self.current_city = self.start  # set ant's current city to random start
        self.attractiveness = [[0 if i == j else 1 / int(cities_map[i][j]) for j in range(
            dimension)] for i in range(dimension)]  # ant's attractiveness of next move


# function for ants to choose next city in tour
def choose_next_city(ant, pheromone_map, alpha, beta, dimension):
    temp = 0  # temp used for bottom half of pheromone equation from slides
    probabilities = [0 for i in range(dimension)]  # list of probablities
    for i in ant.cities_left_to_visit:  # loop for summation of bottom of equation
        temp += float(pheromone_map[ant.current_city][i]) ** alpha * \
            float(ant.attractiveness[ant.current_city][i]) ** beta
    for i in range(dimension):  # loop to copmlete equation for each city
        try:
            ant.cities_left_to_visit.index(i)  # test value
            probabilities[i] = float(pheromone_map[ant.current_city][i])**alpha * float(
                ant.attractiveness[ant.current_city][i]) ** beta / temp
        except ValueError:
            pass
    choice = 0  # initilize ant's choice
    rand = random.random()  # random number
    # roulette randomization. concept from https://stackoverflow.com/questions/10324015/fitness-proportionate-selection-roulette-wheel-selection-in-python
    # enumerate list of probablities for traversing
    for i, probability in enumerate(probabilities):
        rand -= probability
        if rand <= 0:
            choice = i
            break
        # resets ant's tour
    if len(probabilities) > 0:  # if not empty list of probabliites
        if not ant.cities_left_to_visit:  # and an empty list of cities left ot visit
            choice = ant.start  # move ant back to start
            ant.cities_left_to_visit = []  # emptys the list of cities left to visit
            for city in [i for i in range(dimension)]:  # for every city
                if city != ant.start:  # if city isnt starting city
                    # add city to list of cities to visit
                    ant.cities_left_to_visit.append(city)
        else:
            # remove ant's choice from list of cities to visit
            ant.cities_left_to_visit.remove(choice)
            # add ant's choice to list of cities visited
            ant.cities_visited.append(choice)
            # add cost of choice to ant's total cost
            ant.cost += float(cities_map[ant.current_city][choice])
            ant.current_city = choice  # move ant to choice ccity

# this function adjusts pheromone map with ants' pheromones


def lay_pheromones(pheromone_map, ant_list, rho):
    for i, row in enumerate(pheromone_map):
        for j, column in enumerate(row):
            pheromone_map[i][j] *= rho  # pheromone dissapation
            for ant in ant_list:
                # addition of ants' pheromones
                pheromone_map[i][j] += ant.pheromone_change[i][j]


# instantiate configuration file parser
config = configparser.ConfigParser()
config.read('config.ini')  # select config file to use
# import config values into program
alpha = float(config['DEFAULT']['alpha'])
beta = float(config['DEFAULT']['beta'])
rho = float(config['DEFAULT']['rho'])
q = float(config['DEFAULT']['q'])
num_iterations = int(config['DEFAULT']['numIterations'])
num_ants = int(config['DEFAULT']['numAnts'])
file_name = str(config['DEFAULT']['fileName'])

cities_map = []
ant_list = []
# pull cities map from supplied text file
with open(file_name) as f:
    cityLetters = f.readline().split()
    line = 1
    while line:
        line = f.readline()
        if line:
            city = line.split()
            for entry in city:
                if isinstance(entry, int):
                    entry = int(entry)
            city = city[1:]
        cities_map.append(city)

dimension = len(cityLetters)
pheromone_map = [[1 / (dimension * dimension) for j in range(dimension)]
                 for i in range(dimension)]  # pheromone map inversely proportional to distance

lowest_cost = 10000.0  # initialize lowest cost to a high number
solution = []
for i in range(num_iterations):  # loop for iterations
    for j in range(num_ants):  # loop for adding newly created ants to list
        ant_list.append(Ant(pheromone_map, cities_map, dimension))
    for ant in ant_list:  # for every ant
        for i in range(dimension - 1):  # choose next city n times
            choose_next_city(ant, pheromone_map, alpha, beta, dimension)
        # add ants costs tos um
        ant.cost += float(cities_map[ant.cities_visited[-1]]
                          [ant.cities_visited[0]])
        # if lower than lowest, make new lowest adn add to solution
        if ant.cost < lowest_cost:
            lowest_cost = ant.cost
            solution = [] + ant.cities_visited
        ant.pheromone_change = [[0 for _ in range(dimension)]for _ in range(
            dimension)]  # empty ant's phermone change map
        # loop for updating ant pheromone map
        for k in range(1, len(ant.cities_visited)):
            temp1 = int(ant.cities_visited[k-1])
            temp2 = int(ant.cities_visited[k])
            ant.pheromone_change[temp1][temp2] = q / \
                float(cities_map[temp1][temp2])
    # lay new pheromones for all ants
    lay_pheromones(pheromone_map, ant_list, rho)

# print final results
print("Pheromone map: ")
for i in range(dimension):
    for j in range(dimension):
        print(pheromone_map[i][j], end=' ')
    print('')
print("\nSolution: ", solution, "\nCost: ", lowest_cost)
