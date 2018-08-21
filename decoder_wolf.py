"""
Author: humblewolf
Description: this file talks with the pyro decoder,,,,
"""
import Pyro4

class PyroDecoder():

    def get_all_running_pyro_nodes(self):
        msg = input("Type yr msg.").strip()

        ns = Pyro4.locateNS(host="10.131.10.64")
        name_to_uri_dict = ns.list()
        #TODO : get list of all up pyro instances so that we can rotate between them

    def get_pyro_kaldi_node_instance(self):
        pass
        # TODO : connect with pyro instances in a round robin manner
        # TODO : implement decoding in a pyro node(ubuntu machine)
