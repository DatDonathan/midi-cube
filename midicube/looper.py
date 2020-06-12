import midicube
from midicube.devices import *
import midicube.serialization as serialization
import midicube.registration
from pyo import *
import mido
from midicube.utils import DummyInput
import time

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
        return LooperRuntimeData().__channels_from_dict__(dict)
    
    @property
    def channel_data_type(self):
        return ChannelData

class RuntimeChannelData(serialization.Serializable):

    def __init__(self):
        self.messages = []
    
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
        self.input = DummyInput()
        self.runtime_data = LooperRuntimeData
    
    def send (self, msg):
        pass

    def close (self):
        pass

    def create_menu(sel):
        return None
    
    def get_identifier(self):
        return "Looper"
    
    def init(self):
        self.beat = Beat(time=60/120.0/4, taps=4)
        self.beat.play()

    def on_reg_change(self):
        pass
    
    @property
    def data_type(self):
        return LooperDeviceData