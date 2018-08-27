"""
Author: humblewolf
Description: This file reads data from a file/audio device and send it to websocket server, it also gives out partial hypothesis
Audio should be sampled at 8khz, fixed
"""


import gevent
import contextlib
import wave
import logging
import json
import pyaudio
import argparse
import sys
from gevent import monkey; monkey.patch_all()
from ws4py.client.geventclient import WebSocketClient
from ConstantsWolf import ConstantsWolf as cw
from time import sleep
import time

logging.basicConfig(filename=cw.client_log_loc, level=logging.DEBUG, format= '%(asctime)s %(levelname)s %(message)s')

def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == cw.channels
        sample_width = wf.getsampwidth()
        assert sample_width == cw.bytes_per_sample
        sample_rate = wf.getframerate()
        assert sample_rate == cw.sampling_rate
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data

def packet_generator(packet_length_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (packet_length_ms / 1000.0) * cw.bytes_per_sample)#grab 30x8 = 240 samples per packet or 240x2=480 bits per packet
    offset = 0
    while offset + n < len(audio):
        yield audio[offset:offset + n]
        offset += n


def writeToWavFileFromMic(p, frames):
    #  create a wav file from captured data
    wf = wave.open("test.wav", 'wb')
    wf.setnchannels(cw.channels_mic)
    wf.setsampwidth(p.get_sample_size(cw.sampling_format))
    wf.setframerate(cw.sampling_rate_mic)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == '__main__':

    ap = argparse.ArgumentParser(usage="python ClientWolf.py --mode file/mic")
    ap.add_argument('-m', '--mode', default="file", required=True, help='From where to take input data ? Can be file/mic')
    args = ap.parse_args()

    ws = WebSocketClient('ws://%s:%i/ws' % (cw.ws_server_host,cw.ws_server_port), protocols=['http-only', 'chat'])
    ws.connect()
    logging.info("Client connected to server.")
    print('------Client Started at %s--------' % (time.time()))

    def incoming():
        i = 0
        op_buffer = {}
        while True:
            m = ws.receive(block=True)
            msg = str(m)
            if msg.startswith("*"):
                print(msg)
            elif msg is not None:
                ts = json.loads(msg)
                op_buffer[ts['pos']] = ts['pt']
                print('segment %i pt received at %s' % (ts['pos'], time.time()))
                while True:
                    try:
                        print('%i =============> %s => %s' % (i, time.time(), op_buffer[i]))
                        i += 1
                    except:
                        break
            else:
                break

        logging.info("Client disconnected from server.")

    def outgoing_file():
        """
        Send frames fron audio file here, use generators here, try to use some throttling here
        """

        raw_aud = read_wave(cw.test_file_wav)
        for packet in packet_generator(cw.packet_length_ms, raw_aud, cw.sampling_rate):
            if isinstance(packet, bytes):
                sleep(cw.loop_sleep_secs)
                ws.send(packet, binary=True)

    def outgoing_mic():
        """
        Send frames fron audio mic here, use generators here, try to use some throttling here
        """
        print("-----------Please wait, Setting up your mic------------")

        #  first record audio
        p = pyaudio.PyAudio()
        stream = p.open(format=cw.sampling_format,
                        channels=cw.channels_mic,
                        rate=cw.sampling_rate_mic,
                        input=True,
                        frames_per_buffer=cw.record_buffer_samples)

        print("* recording, please speak")

        packet_size = int((cw.packet_length_ms_mic/1000)*cw.sampling_rate_mic)  # normally 240 packets or 480 bytes

        frames = []

        #while True:
        for i in range(0, 1000):
            packet = stream.read(packet_size)
            ws.send(packet, binary=True)
            sleep(cw.loop_sleep_secs_mic)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        #writeToWavFileFromMic(p, frames)
        p.terminate()

    if args.mode == "file":
        greenlets = [
            gevent.spawn(incoming),
            gevent.spawn(outgoing_file),
        ]
    elif args.mode == "mic":
        greenlets = [
            gevent.spawn(incoming),
            gevent.spawn(outgoing_mic),
        ]
    else:
        print("Only file or mic mode is supported")
        sys.exit(0)

    print('------Client ready at %s--------' % (time.time()))
    gevent.joinall(greenlets)
