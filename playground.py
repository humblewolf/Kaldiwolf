"""
Author: humblewolf
Description: <write description here...>
"""

from decoder_wolf import PyroDecoder as pd
import Pyro4

pdd = pd()

pdd.decode_now()
pdd.decode_now()
pdd.decode_now()
pdd.decode_now()

# msg = input("Type yr msg.").strip()
#
# ns = Pyro4.locateNS(host="10.131.10.64")
# uri = ns.lookup("kaldiwolf_pyro_node.1")
# obj = Pyro4.Proxy(uri)
# print(obj.decode_by_kaldi(msg))

#TODO: do this from a serverwolf area