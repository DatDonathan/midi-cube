from midicube.devices import *
import midicube.serialization as serialization

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
    
    def __to_dict__(self):
        return {'name': name, 'bindings': serialization.list_to_dicts(self.bindings)}
    
    def __from_dict__(dict):
        reg = Registration(dict['name'])
        reg.bindings = serialization.list_from_dicts(dict['bindings'], DeviceBinding)
        return reg

class RegistrationManager():

    def __init__(self):
        self.registrations = []
        self.cur_reg = Registration()
    
    def select(reg: Registration):
        self.cur_reg = copy.deepcopy(reg)
    
    def save(self):
        return {'registrations': serialization.list_to_dicts(self.registrations)}
    
    def load(self, dict):
        bindings = serialization.list_from_dicts(dict['bindings'])
