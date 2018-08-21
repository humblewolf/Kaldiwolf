"""
Author: humblewolf
Description: this file does the chunking,,,,
"""

from multiprocessing import Process
from RedisQueueWolf import PySimpleQueue
from Frame import Frame
from ConstantsWolf import ConstantsWolf as cw
from decoder_wolf import PyroDecoder as pd
import collections
import sys
import webrtcvad
import contextlib
import wave
import subprocess, os
import re
import json
import pickle

#kh = os.environ['KALDI_HOME']

class TranscriptSegment:
    def __init__(self, pt, sequence_no):
        self.pos = sequence_no
        self.pt = pt

    def jsonifyAndSendToQueue(self, pt_queue_id, tcpt_Queue_Vad):
        jsonStr = json.dumps(self.__dict__)
        tcpt_Queue_Vad.put(pt_queue_id, jsonStr)


def gen_pt_send(tcpt_queue_uuid, sequence_no, path):
    global kh
    executable = 'cd %s && ./decode_single.sh ' % (kh,)
    args = '%s' % (path,)
    #args = '%s 2>&1 | sed -n \'s|.*<s>\(.*\)<\/s>|\1|p\'' % (path,)
    p = subprocess.Popen(executable+args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdo, stde = p.communicate()
    tcpt_Queue_Vad = PySimpleQueue()
    match = re.match(r'.*<s>(.*)<\/s>.*', str(stde))
    if match:
        ts = TranscriptSegment(match.group(1), sequence_no)
        ts.jsonifyAndSendToQueue(tcpt_queue_uuid, tcpt_Queue_Vad)


# def vadetectwork(aud_queue_uuid, tcpt_queue_uuid):
#
#     global kh
#     # generate frames here
#     vad = webrtcvad.Vad(cw.vad_agressiveness)
#     frames = VadWolf.frame_generator(aud_queue_uuid)
#     segments = VadWolf.vad_collector(cw.sampling_rate, cw.packet_length_ms, cw.padding_duration_ms, vad, frames)
#     for i, segment in enumerate(segments):
#         path = '%stmp/chunk-%s-%002d.wav' % (kh, tcpt_queue_uuid, i)
#         print(' Writing %s' % (path,))
#         VadWolf.write_wave(path, segment, cw.sampling_rate)
#         #decode a file here - take care of sequence of chunk, use an env variable for kaldi
#         # spawn a proc for STT and feed text into transcript queue.......
#         opth = Process(name="ServerWolf_op_queue_feed_proc", target=gen_pt_send, args=(tcpt_queue_uuid, i, path))
#         opth.start()
#         print("New process spawned for pt generation")

def vadetectwork(aud_queue_uuid, tcpt_queue_uuid):

    global kh
    # generate frames here
    vad = webrtcvad.Vad(cw.vad_agressiveness)
    frames = VadWolf.frame_generator(aud_queue_uuid)
    segments = VadWolf.vad_collector(cw.sampling_rate, cw.packet_length_ms, cw.padding_duration_ms, vad, frames)
    tcpt_Queue_Vad = PySimpleQueue()
    for i, segment in enumerate(segments):
        ts = TranscriptSegment(pd.get_segment_pt(segment), i)
        ts.jsonifyAndSendToQueue(tcpt_queue_uuid, tcpt_Queue_Vad)#TODO test this......monday end


class VadWolf:

    @classmethod
    def frame_generator(self, aud_queue_uuid):
        """Function to yield frames object"""

        timestamp = 0.0
        duration = cw.packet_length_ms / 1000  # duration of a frame in secs

        aud_Queue_Vad = PySimpleQueue()
        while True:
            try:
                yield Frame(aud_Queue_Vad.get(aud_queue_uuid), timestamp, duration)
                #print("Frame generated "+str(timestamp))
                timestamp += duration
            except:
                pass

    # @classmethod
    # def vad_collector(self, sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    #     """Filters out non-voiced audio frames.
    #     Given a webrtcvad.Vad and a source of audio frames, yields only
    #     the voiced audio.
    #     Uses a padded, sliding window algorithm over the audio frames.
    #     When more than 90% of the frames in the window are voiced (as
    #     reported by the VAD), the collector triggers and begins yielding
    #     audio frames. Then the collector waits until 90% of the frames in
    #     the window are unvoiced to detrigger.
    #     The window is padded at the front and back to provide a small
    #     amount of silence or the beginnings/endings of speech around the
    #     voiced frames.
    #     Arguments:
    #     sample_rate - The audio sample rate, in Hz.
    #     frame_duration_ms - The frame duration in milliseconds.
    #     padding_duration_ms - The amount to pad the window, in milliseconds.
    #     vad - An instance of webrtcvad.Vad.
    #     frames - a source of audio frames (sequence or generator).
    #     Returns: A generator that yields PCM audio data.
    #     """
    #
    #     print("inside collector --------")
    #
    #     num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    #     # We use a deque for our sliding window/ring buffer.
    #     ring_buffer = collections.deque(maxlen=num_padding_frames)
    #     # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    #     # NOTTRIGGERED state.
    #     triggered = False
    #
    #     voiced_frames = []
    #
    #     for frame in frames:
    #         #print("frame obtained by collector - "+str(frame.timestamp))
    #         is_speech = vad.is_speech(frame.bytes, sample_rate)
    #
    #         sys.stdout.write('1' if is_speech else '0')
    #         if not triggered:
    #             ring_buffer.append((frame, is_speech))
    #             num_voiced = len([f for f, speech in ring_buffer if speech])
    #             # If we're NOTTRIGGERED and more than 90% of the frames in
    #             # the ring buffer are voiced frames, then enter the
    #             # TRIGGERED state.
    #             if num_voiced > 0.9 * ring_buffer.maxlen:
    #                 triggered = True
    #                 sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
    #                 # We want to yield all the audio we see from now until
    #                 # we are NOTTRIGGERED, but we have to start with the
    #                 # audio that's already in the ring buffer.
    #                 seg_decoder = pd()
    #                 for f, s in ring_buffer:
    #                     voiced_frames.append(f)
    #                     # TODO: create a decoder_wolf instance with available pyro-nodes here, and send frames to it, once a segment is done decode it.....
    #                 ring_buffer.clear()
    #         else:
    #             # We're in the TRIGGERED state, so collect the audio data
    #             # and add it to the ring buffer.
    #             #TODO : keep sending frames here
    #             voiced_frames.append(frame)
    #             ring_buffer.append((frame, is_speech))
    #             num_unvoiced = len([f for f, speech in ring_buffer if not speech])
    #             # If more than 90% of the frames in the ring buffer are
    #             # unvoiced, then enter NOTTRIGGERED and yield whatever
    #             # audio we've collected.
    #             if num_unvoiced > 0.9 * ring_buffer.maxlen:
    #                 sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    #                 triggered = False
    #                 yield b''.join([f.bytes for f in voiced_frames])
    #                 # TODO : stop sending frames here, start decoding
    #                 ring_buffer.clear()
    #                 voiced_frames = []
    #     if triggered:
    #         sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    #     sys.stdout.write('\n')
    #     # If we have any leftover voiced audio when we run out of input,
    #     # yield it.
    #     if voiced_frames:
    #         yield b''.join([f.bytes for f in voiced_frames])

    @classmethod
    def vad_collector(self, sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):

        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False
        decoder = pd()
        seg_decoder = None

        for frame in frames:
            is_speech = vad.is_speech(frame.bytes, sample_rate)
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    seg_decoder = decoder.create_segment_decoder_obj()
                    for f, s in ring_buffer:
                        pd.send_aud_to_seg_decoder(seg_decoder, f.bytes)
                    ring_buffer.clear()
            else:
                pd.send_aud_to_seg_decoder(seg_decoder, frame.bytes)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    yield seg_decoder
                    ring_buffer.clear()
                    print("-------------------segment done---------------------")

        if not triggered:
            yield seg_decoder

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