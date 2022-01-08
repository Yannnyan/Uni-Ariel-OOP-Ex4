from unittest import TestCase
import fucked_graph_algo
from Controller import controller

class Test_Graphalgo(TestCase):
    def setUp(self) -> None:
        self.cntrl = controller()
        self.cntrl.add_agents([])
        self.cntrl.client.start()

    def test_best_Path_foreach_agent(self):
        while self.cntrl.client.time_to_end():
            self.cntrl.update_Agents()
            self.cntrl.update_Pokemons()
            self.cntrl.add_paths_to_agents()
            print(self.cntrl.pokemon_for_agent)
            list_tup = self.cntrl.determine_next_edges()  # list of (agent id, next node)
            self.cntrl.insert_edges_to_client(list_tup)
            self.cntrl.ttl = float(self.cntrl.client.time_to_end())
            self.cntrl.client.get_info()
            # print(self.cntrl.ttl, self.cntrl.client.get_info())
            self.cntrl.client.move()


