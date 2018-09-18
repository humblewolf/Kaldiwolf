Near real-time decoding with Kaldi using websockets.
------------------------------------------------------------

How to install and use this ?

0. Common for all nodes :

0. Open 2 terminals with sudo access.
1. create a kw_deployment folder somewhere and cd into that.
2. git clone https://github.com/humblewolf/Kaldiwolf.git
3. virtualenv -p /usr/bin/python3.5 kw_venv
4. . kw_venv/bin/activate
5. Install all the above given modules

        > Modules used :
        1. for client/server: pip install gevent ws4py webrtcvad redis pyaudio
        2. for pyro_node: pip install pyro4

        > In case pyaudio is not getting installed via pip, installing following packages would most probably resolve the issue
        apt update
        apt install python3-dev
        apt install portaudio19-dev



6. Install and start redis server (in a second terminal screen)

        > Install

        wget http://download.redis.io/redis-stable.tar.gz
        tar xvzf redis-stable.tar.gz
        cd redis-stable
        make

        > Starting redis server:
        "in forground" -> redis-server


7. Install and start pyroname server (in a second terminal screen)

        > Start name server bound to 0.0.0.0 on any machine of network
        apt install pyro4
        pyro4-ns -n 0.0.0.0

8. Check all the relevent settings in ConstantsWolf.py
9. Run master server on one machine in the network , python ServerWolf.py , (in a second terminal screen)
10. Run pyro node on all worker machines, python pyro_node.py, (in a second terminal screen)

------------------------------------------------------------just a note-----------------------------------------------------------
> Editor Settings:

Source Code pro, 0.7, 11