"""
Author: humblewolf
Description: this file talks with the pyro seg_decoder,,,,
"""
import Pyro4
from ConstantsWolf import ConstantsWolf as cw

class PyroDecoder:

    def __init__(self):
        ns = Pyro4.locateNS(host=cw.pyro_ns_address)
        name_to_uri_dict = ns.list()
        del name_to_uri_dict['Pyro.NameServer']
        self.pyro_node_uri_list = list(name_to_uri_dict.values())
        self.no_of_nodes = len(self.pyro_node_uri_list)
        PyroDecoder.work_node = 0  # this is class property, otherwise count will always start from 0. putting load on initial nodes

    def go_on_next_available_pyro_node(self):
        PyroDecoder.work_node = (PyroDecoder.work_node+1) % self.no_of_nodes

    def create_segment_decoder_obj(self, lm, segment_uuid, tcpt_queue_uuid, segment_no):
        seg_decoder = Pyro4.Proxy(self.pyro_node_uri_list[PyroDecoder.work_node])
        seg_decoder.set_lm(lm)
        seg_decoder.set_uuids(segment_uuid, tcpt_queue_uuid, segment_no)
        self.go_on_next_available_pyro_node()
        return seg_decoder