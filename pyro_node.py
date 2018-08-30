"""
Author: humblewolf
Description: this file will work as a remote kaldi decoder, pyro is being used for rmi.
"""
import Pyro4
import sys
import os
import threading
from ConstantsWolf import ConstantsWolf as cw
from kaldi_invoker import TranscriptSegment, invoke_now
from RedisQueueWolf import PySimpleQueue as psq
from multiprocessing import Process

@Pyro4.behavior(instance_mode="session")
class KaldiDecoder():

    def __init__(self):
        self.aud_binary_data = b''
        self.psq = psq()

    @Pyro4.expose
    @Pyro4.oneway
    def get_aud_data(self):
        msg = self.psq.get(self.segment_uuid)
        self.aud_binary_data += msg

    @Pyro4.expose
    @Pyro4.oneway
    def set_uuids(self, segment_uuid, tcpt_queue_uuid, segment_no):
        print("Setting segment uuids")
        self.segment_uuid = segment_uuid
        self.tcpt_queue_uuid = tcpt_queue_uuid
        self.segment_no = segment_no

    @Pyro4.expose
    @Pyro4.oneway
    def get_pt(self, is_last_segment):
        segment_audio_path = '%stmp/' % (cw.kaldi_home,)
        self.check_and_create_dir(segment_audio_path)
        path = '%schunk-%s.wav' % (segment_audio_path, self.segment_uuid)
        print(' Writing file %s of size %i' % (path,len(self.aud_binary_data)))
        TranscriptSegment.write_wave(path, self.aud_binary_data, cw.sampling_rate)
        opth = Process(name="ServerWolf_op_queue_feed_proc", target=invoke_now, args=(self.tcpt_queue_uuid, self.segment_no, path, is_last_segment))
        opth.start()
        self.psq.remove((self.segment_uuid,))  # remove garbage psq queue
        print("New process spawned for pt generation")

    def check_and_create_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)


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
        ns = Pyro4.locateNS(host=cw.pyro_ns_address)
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
