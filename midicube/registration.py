from midicube.devices import *
import midicube.serialization as serialization
import copy
from abc import ABC, abstractmethod

class AbstractDeviceData(serialization.Serializable, ABC):

    def __init__(self):
        super().__init__()
        self.channels = {}

    def channel_data(self, channel: int):
        if not channel in self.channels:
            self.channels[channel] = self.channel_data_type()
        return self.channels[channel]
    
    def __to_dict__(self):
        dict = {'channels': {}}
        for key, value in self.channels.items():
            dict['channels'][str(key)] = value.__to_dict__()
        return dict
    
    def __channels_from_dict__(self, dict):
        for key, value in dict['channels'].items():
            self.channels[int(key)] = self.channel_data_type.__from_dict__(value)
    
    @property
    @abstractmethod
    def channel_data_type(self):
        return None

class DeviceBinding(serialization.Serializable):

    def __init__(self, input_id: str, output_id: str, input_channel: int = -1, output_channel: int = -1):
        super().__init__()
        self.input_id = input_id
        self.output_id = output_id
        self.input_channel = input_channel
        self.output_channel = output_channel

    def apply (self, msg: mido.Message, cube, inport: MidiInputDevice):
        outport = cube.outputs[self.output_id]
        if outport != None and inport.get_identifier() == self.input_id and (self.input_channel < 0 or msg.channel == self.input_channel):
            if self.output_channel >= 0:
                msg.channel = self.output_channel
            outport.send(msg)
    
    def __to_dict__(self):
        return {'input_id': self.input_id, 'output_id': self.output_id, 'input_channel': self.input_channel, 'output_channel': self.output_channel}

    def __from_dict__(dict):
        return DeviceBinding(dict['input_id'], dict['output_id'], dict['input_channel'], dict['output_channel'])

    def __str__(self):
        return str(self.input_channel) + " " + self.input_id + ":" + str(self.output_channel) + " " + self.output_id

class Registration(serialization.Serializable):

    def __init__(self, name: str = 'unnamed'):
        super().__init__()
        self.name = name
        self.bindings = []
        self.device_data = {}

    def data(self, device: MidiOutputDevice):
        if not device.get_identifier() in self.device_data:
            self.device_data[device.get_identifier()] = device.data_type()
        return self.device_data[device.get_identifier()]

    def __to_dict__(self):
        device_data = {}
        for key, items in self.device_data.items():
            device_data[key] = serialization.DynamicSerializableContainer(self.device_data[key])
        return {'name': self.name, 'bindings': serialization.list_to_dicts(self.bindings), 'device_data': serialization.dict_to_serialized_dict(device_data)}
    
    def __from_dict__(dict):
        reg = Registration(dict['name'])
        reg.bindings = serialization.list_from_dicts(dict['bindings'], DeviceBinding)
        device_data = serialization.dict_from_serialized_dict(dict['device_data'], serialization.DynamicSerializableContainer)
        for key, value in device_data.items():
            reg.device_data[key] = device_data[key].serializable
        return reg
    
    def __str__(self):
        return self.name

class RegistrationManager():

    def __init__(self):
        self._listeners = []
        self.registrations = {}
        self._cur_reg = Registration()
    
    def add_listener(self, listener: callable):
        self._listeners.append(listener)
    
    def select(self, reg: Registration):
        if reg != None:
            self._cur_reg = copy.deepcopy(reg)
            for l in self._listeners:
                l(self)
    
    def add_registration(self, reg):
        self.registrations[reg.name] = reg
    
    @property
    def cur_reg(self):
        return self._cur_reg
    
    def save(self):
        return {'registrations': serialization.dict_to_serialized_dict(self.registrations)}
    
    def load(self, dict):
        self.registrations = serialization.dict_from_serialized_dict(dict['registrations'], Registration)
