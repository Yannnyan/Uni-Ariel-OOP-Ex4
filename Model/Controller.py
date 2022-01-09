import math
from types import SimpleNamespace

from Model.DiGraph import DiGraph
from Model.Graph_Algo import GraphAlgo
from client_python.client import Client
from Model.classes.agents import *
from Model.classes.pokemons import *
import threading
import json
import random


class controller:

    def __init__(self):

        ip = '127.0.0.1'
        port = 6666

        # start connection
        self.client = Client()
        self.client.start_connection(ip, port)

        # declare variables
        self.graphAlgo = GraphAlgo()
        self.graphAlgo.load_from_json_string(self.client.get_graph())
        self.graph = self.graphAlgo.graph

        self.pokemons = Pokemons(self.client.get_pokemons())
        self.add_agents()
        self.agents = Agents(self.client.get_agents())  # initialize agents and pokemons

        self.pokemon_for_agent = {}  # dict of {agent.id : ( path to pokemon,pokemon.pos, pokemon_time)}
        for agent in self.agents.agents:
            self.pokemon_for_agent[agent.id] = ([], -1, math.inf)

        self.last_node_for_agent = {}  # dict of {agent.id : node.id}
        for agent in self.agents.agents:
            self.last_node_for_agent[agent.id] = -1

        self.times_to_move = []

        self.ttl = float(self.client.time_to_end())
        self.grade = 0

    def find_next_route(self):
        # implement algorithm here
        pass

    def close(self):
        self.client.stop_connection()

    # def update_GUI(self):
    #     # if gui returns false then close the controler
    #     if not self.gui.update(self.pokemons.pokemons, self.agents.agents, self.grade, self.gui.mc, self.ttl):
    #         close()

    def update_Agents(self):  # TODO if its not fast enough change this
        agents_json = self.client.get_agents()
        self.agents = Agents(agents_json)

    def update_Pokemons(self):  # TODO if its not fast enough change this
        pokemons_json = self.client.get_pokemons()  # setting pokemons and agents
        self.pokemons = Pokemons(pokemons_json)

    def add_agents(self):
        # get the amount of agents in this game - n
        info = json.loads(self.client.get_info())
        n = info['GameServer']['agents']
        print(n)
        # find the n pokemon with the highest value if they exist
        pokList = []
        copyList = self.pokemons.pokemons.copy()
        for i in range(n):
            if len(copyList) is not 0:
                bestPokemon = copyList[0]
                for pok in copyList:
                    if pok.value > bestPokemon.value:
                        bestPokemon = pok
                pokList.append(bestPokemon)
                copyList.remove(bestPokemon)
        # use the pokemon finder for each pokemon
        for j in range(len(pokList)):
            pokList[j] = self.graphAlgo.PokemonPlacement(pokList[j].type, pokList[j].pos)
        if len(pokList) is not n:
            for i in range(n - len(pokList)):
                pokList.append((random.randint(0, self.graph.v_size()), 0, 0))
        # add the agents to the node next to the pokemon
        for l in range(len(pokList)):
            if self.client.add_agent("{\"id\"" + f":{pokList[l][0]}" + "}") is False:
                print("Agent wasn't added, you fucked up")

    def determine_next_edges(self):
        edges = []
        for agent in self.agents.agents:
            if agent.dest == -1:
                if len(self.pokemon_for_agent[agent.id][0]) != 0:
                    nextnode = (self.pokemon_for_agent[agent.id][0]).pop(0)
                    self.last_node_for_agent[agent.id] = agent.src
                    tup = (agent.id, nextnode)
                    edges.append(tup)
                else:
                    return None
        return edges
        # insert algorithm here

    def insert_edges_to_client(self, list_tup_id_edge):
        if list_tup_id_edge is not None:
            for tup in list_tup_id_edge:
                #                            '{"agent_id":'+str(agent.id)+', "next_node_id":'+str(next_node)+'}'
                self.client.choose_next_edge('{"agent_id":' + str(tup[0]) + ', "next_node_id":' + str(tup[1]) + '}')
                # self.client.choose_next_edge(
                #     '{\"agent_id\":' + str(tup[0]) + ', \"next_node_id\":' + str(tup[1]) + '}')

    def move_agents(self):
        self.client.move()

    def add_paths_to_agents(self):
        self.pokemon_for_agent = self.graphAlgo.best_Path_foreach_agent(self.agents, self.pokemons)
