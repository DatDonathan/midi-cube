from midicube.devices import *
import midicube.serialization as serialization
import copy

class DeviceBinding(serialization.Serializable):

    def __init__(self, input_id: str, output_id: str, input_channel: int = -1, output_channel: int = -1):
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
        self.name = name
        self.bindings = []
        self.device_data = {}
    
    def __to_dict__(self):
        device_data = {}
        for key, items in self.device_data.items():
            device_data[key] = serialization.DynamicSerializableContainer(self.device_data[key])
        return {'name': self.name, 'bindings': serialization.list_to_dicts(self.bindings), 'device_data': serialization.dict_to_serialized_dict(self.device_data)}
    
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
        self.registrations = []
        self.cur_reg = Registration()
    
    def select(self, reg: Registration):
        self.cur_reg = copy.deepcopy(reg)
    
    def save(self):
        return {'registrations': serialization.list_to_dicts(self.registrations)}
    
    def load(self, dict):
        self.registrations = serialization.list_from_dicts(dict['registrations'], Registration)
