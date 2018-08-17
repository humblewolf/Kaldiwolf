Near real-time decoding with Kaldi using websockets.
------------------------------------------------------------

> Modules used :

1. for client/server: pip install gevent ws4py webrtcvad redis pyaudio
2. for pyro_node: pip install pyro4

> Editor Settings:

Source Code pro, 0.7, 11

> Starting redis server:

"in forground" -> redis-server 

> Start name server bound to 0.0.0.0 on any machine of network

pyro4-ns -n 0.0.0.0