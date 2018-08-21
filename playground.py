"""
Author: humblewolf
Description: <write description here...>
"""

import Pyro4

msg = input("Type yr msg.").strip()

ns = Pyro4.locateNS(host="10.131.10.64")
uri = ns.lookup("kaldiwolf_pyro_node.1")
obj = Pyro4.Proxy(uri)
print(obj.decode_by_kaldi(msg))

#TODO: do this from a serverwolf area