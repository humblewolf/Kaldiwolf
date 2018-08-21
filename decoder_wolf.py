"""
Author: humblewolf
Description: this file talks with the pyro seg_decoder,,,,
"""
import Pyro4


class PyroDecoder:

    def __init__(self):
        ns = Pyro4.locateNS(host="10.131.10.64")
        name_to_uri_dict = ns.list()
        del name_to_uri_dict['Pyro.NameServer']
        self.pyro_node_uri_list = list(name_to_uri_dict.values())
        self.no_of_nodes = len(self.pyro_node_uri_list)
        PyroDecoder.work_node = 0  # this is class property, otherwise count will always start from 0. putting load on initial nodes

    def go_on_next_available_pyro_node(self):
        PyroDecoder.work_node = (PyroDecoder.work_node+1) % self.no_of_nodes

    def create_segment_decoder_obj(self):
        # TODO : connect with pyro instances in a round robin manner
        # TODO : implement decoding in a pyro node(ubuntu machine)
        seg_decoder = Pyro4.Proxy(self.pyro_node_uri_list[PyroDecoder.work_node])
        self.go_on_next_available_pyro_node()
        return seg_decoder

    @staticmethod
    def send_aud_to_seg_decoder(seg_decoder, data):
        seg_decoder.get_aud_data(data)

    @staticmethod
    def get_segment_pt(seg_decoder):
        return seg_decoder.get_pt()