"""
Author: humblewolf
Description: this module is responsible for invoking kaldi
"""

import os
import subprocess
import re

kh = os.environ['KALDI_HOME']

class InvokeKaldiProcess:


    def invoke_now(self, tcpt_queue_uuid, sequence_no, path):
        global kh
        executable = 'cd %s && ./decode_single.sh ' % (kh,)
        args = '%s' % (path,)
        # args = '%s 2>&1 | sed -n \'s|.*<s>\(.*\)<\/s>|\1|p\'' % (path,)
        p = subprocess.Popen(executable + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdo, stde = p.communicate()
        match = re.match(r'.*<s>(.*)<\/s>.*', str(stde))
        if match:
            # print(match.group(1))
            ts = TranscriptSegment(match.group(1), sequence_no)
            ts.jsonifyAndSendToQueue(tcpt_queue_uuid, tcpt_Queue_Vad)

