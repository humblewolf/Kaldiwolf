"""
Author: humblewolf
Description: this module is responsible for invoking kaldi
"""

import os
import subprocess
import re
import contextlib
import wave
import json
from ConstantsWolf import ConstantsWolf as cw
from RedisQueueWolf import PySimpleQueue as psq

class TranscriptSegment:
    def __init__(self, pt, sequence_no):
        self.pos = sequence_no
        self.pt = pt

    def jsonifyAndSendToQueue(self, pt_queue_id, tcpt_Queue_Vad):
        jsonStr = json.dumps(self.__dict__)
        tcpt_Queue_Vad.put(pt_queue_id, jsonStr)

    @classmethod
    def write_wave(self, path, audio, sample_rate):
        """Writes a .wav file.
        Takes path, PCM audio data, and sample rate.
        """
        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio)


def invoke_now(tcpt_queue_uuid, sequence_no, path, is_last_segment):
    executable = 'cd %s && ./%s ' % (cw.kaldi_home, cw.decode_script_name)  # notice the space in the end
    args = '%s' % (path,)
    p = subprocess.Popen(executable + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdo, stde = p.communicate()
    match = re.match(r'.*<s>(.*)<\/s>.*', str(stde))
    #print(str(stde))
    if match:
        ts = TranscriptSegment(match.group(1), sequence_no)
        ts.jsonifyAndSendToQueue(tcpt_queue_uuid, psq())

    if is_last_segment:
        ts = TranscriptSegment("###END###", sequence_no+1)
        ts.jsonifyAndSendToQueue(tcpt_queue_uuid, psq())


#TODO : commit and test code

#class InvokeKaldiProcess:
# def gen_pt_send(tcpt_queue_uuid, sequence_no, path):
#     global kh
#     executable = 'cd %s && ./decode_single.sh ' % (kh,)
#     args = '%s' % (path,)
#     #args = '%s 2>&1 | sed -n \'s|.*<s>\(.*\)<\/s>|\1|p\'' % (path,)
#     p = subprocess.Popen(executable+args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     stdo, stde = p.communicate()
#     tcpt_Queue_Vad = PySimpleQueue()
#     match = re.match(r'.*<s>(.*)<\/s>.*', str(stde))
#     if match:
#         ts = TranscriptSegment(match.group(1), sequence_no)
#         ts.jsonifyAndSendToQueue(tcpt_queue_uuid, tcpt_Queue_Vad)
