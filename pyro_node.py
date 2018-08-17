"""
Author: humblewolf
Description: this file will work as a remote kaldi decoder, pyro is being used for rmi.
"""
import Pyro4
import sys
from ConstantsWolf import ConstantsWolf as cw


@Pyro4.behavior(instance_mode="single")
class KaldiDecoder():
    @Pyro4.expose
    def decode_by_kaldi(self, msg):
        print('Message is %s' % (msg,))
        return 'Message is %s' % (msg,)
        #init a new kaldi process using subprocess.popen


def get_available_pyroname(ns):
    for i in range(1,cw.max_pyro_nodes):
        pyroname = '%s.%d' % (cw.pyro_node_name_prefix, i)
        try:
            ns.lookup(pyroname)
        except Exception as ex:
            return pyroname

    print("It seems you have reached your limit of max pyro nodes, Please increase the no of max pyro nodes in constants file.")
    sys.exit(0)


if __name__ == "__main__":

    print("Checking a pyro name-server on network, please allow udp in all firewalls")
    try:
        ns = Pyro4.locateNS()
    except Exception as ex:
        print("Please start a pyro name server, visit README.md for details of starting a pyro nameserver.")
        sys.exit(0)

    pyro_name = get_available_pyroname(ns)
    print('Pyroname found: %s, trying to register it with a pyro uri' % (pyro_name,))

    try:
        ip = input("Please enter your ip address that is visible from all of your pyro clients.").strip()
        daemon = Pyro4.Daemon(host=ip)
        uri = daemon.register(KaldiDecoder)
        ns.register(pyro_name, uri)
        print('kaldi decoder class registered to uri %s, with name %s' % (uri, pyro_name))
        daemon.requestLoop()
    except Exception as ex:
        print('Some exception occured in creating daemon/registering to a uri/attaching uri to a name' % (uri, pyro_name))

    print("-----------------Shutting down pyro daemon-----------------")
    ns.remove(pyro_name)
    daemon.unregister(KaldiDecoder)
    daemon.close()
