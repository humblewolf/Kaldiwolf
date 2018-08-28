"""
Author: humblewolf
Description: <write description here...>
"""

import RedisQueueWolf as rqw

queue = rqw.PySimpleQueue()
queue.put("amar", "233")
print(queue.get("amar"))

# from decoder_wolf import PyroDecoder as pd
# import Pyro4
# import sys
#
# uri = 'PYRO:obj_bad3b20540ff414a94c2180e703ec349@10.131.10.117:37366'
# remote = Pyro4.Proxy(uri)
# remote.shutdown()
# remote._pyroRelease()
# print('uri exiting')
#
# ns = Pyro4.locateNS(host="10.131.10.64")
# ns.remove(uri)
# print('removed from ns')
