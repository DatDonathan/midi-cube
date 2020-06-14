import midicube
from midicube.devices import *
import midicube.serialization as serialization
import midicube.registration
from pyo import *
import mido
from midicube.utils import DummyInput
import time
import threading
import copy

class ChannelData(serialization.Serializable):

    def __init__(self, bars: int = 1):
        self.bars = bars
    
    def __from_dict__(dict):
        return ChannelData(dict['bars'])
    
    def __to_dict__(self):
        return { 'bars': self.bars }

class LooperDeviceData(midicube.registration.AbstractDeviceData):

    def __init__(self):
        super().__init__()
    
    def __from_dict__(dict):
        return LooperDeviceData().__channels_from_dict__(dict)
    
    @property
    def channel_data_type(self):
        return ChannelData

class RuntimeChannelData(serialization.Serializable):

    def __init__(self):
        self.messages = []
        self.last_start = 0
    
    def __to_dict__(self):
        return {}
    
    def __from_dict__(dict):
        return RuntimeChannelData()

class LooperRuntimeData(midicube.registration.AbstractDeviceData):

    def __init__(self):
        super().__init__()
    
    def __from_dict__(dict):
        return LooperRuntimeData().__channels_from_dict__(dict)
    
    @property
    def channel_data_type(self):
        return RuntimeChannelData


class LooperOutputDevice(MidiOutputDevice):

    def __init__ (self):
        super().__init__()
        self.input = DummyInput("Looper")
        self.runtime_data = LooperRuntimeData()
        self.bar_counter = 0
        self.bpm = 120
        self.beats = 4
        self.running = True
        self.last_bar = 0
    
    def play_thread(self, ch: int):
        index = 0
        channel: RuntimeChannelData = self.runtime_data.channel_data(ch)
        messages = copy.deepcopy(channel.messages)
        while self.running:
            data: ChannelData = self.cube.reg().data(self).channel_data(ch)
            if index >= len(messages):
                time.sleep(max(0, (self.last_bar + self.bar_duration_ns() * data.bars - time.clock_gettime_ns(time.CLOCK_BOOTTIME))/1000000000))
                index = 0
                messages = copy.deepcopy(channel.messages)
            else:
                delay = (channel.last_start + messages[index].time - time.clock_gettime_ns(time.CLOCK_BOOTTIME))/1000000000
                print(delay)
                if delay > 0:
                    time.sleep(delay)
                self.input.send(messages[index])
                print(messages[index])
                index += 1
    
    def bar_duration_ns(self):
        return self.bpm / 60 * 1000000000
    
    def send (self, msg: mido.Message):
        self.input.send(msg)
        channel: RuntimeChannelData = self.runtime_data.channel_data(msg.channel)
        data: ChannelData = self.cube.reg().data(self).channel_data(msg.channel)
        index = 0
        curr_bar = self.bar_counter % data.bars
        msg.time = time.clock_gettime_ns(time.CLOCK_BOOTTIME) - channel.last_start
        #Find postition
        for i in range(len(channel.messages)):
            if channel.messages[len(channel.messages) - i - 1].time < msg.time:
                index = len(channel.messages) - i
        #Insert
        channel.messages.insert(index, msg)

    def close (self):
        self.beat.stop()
        self.metronome.stop()
        self.running = False

    def create_menu(self):
        return None
    
    def get_identifier(self):
        return "Looper"

    def _bar_end(self):
        print("Bar end")
        self.bar_counter += 1
        self.last_bar = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        print(self.last_bar)
        for i in range(16):
            channel = self.runtime_data.channel_data(i)
            data = self.cube.reg().data(self).channel_data(i)
            if (self.bar_counter % data.bars) == 0:
                channel.last_start = self.last_bar

    def init(self):
        #Create Beat
        self.beat = Beat(time=60.0/self.bpm, taps=self.beats, w1=100, w2=100, w3=100)
        self.bar_trig = TrigFunc(self.beat['end'], lambda : self._bar_end())
        self.last_bar = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        #Init Data
        for i in range(16):
            data = self.runtime_data.channel_data(i)
            data.last_start = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
        #Create metronome
        trig_env = TrigEnv(self.beat, CosTable(), dur=0.2, mul=self.beat['amp'])
        self.metronome = FastSine(freq=440, mul=trig_env).out()
        self.beat.store(0)
        print(self.beat.getPresets())
        #Start beat
        self.beat.play()
        for i in [0]:
            threading.Thread(target=lambda ch=i : self.play_thread(ch)).start()

    def on_reg_change(self):
        pass
    
    @property
    def data_type(self):
        return LooperDeviceData