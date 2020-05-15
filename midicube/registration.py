from midicube.devices import *

class DeviceBinding:

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

    def __str__(self):
        return str(self.input_channel) + " " + self.input_id + ":" + str(self.output_channel) + " " + self.output_id

class Registration:

    def __init__(self):
        self.bindings = []

    
class RegistrationManager:

    def __init__(self):
        self.registrations = []
        self.cur_reg = Registration()
    
    def select(reg: Registration):
        self.cur_reg = copy.deepcopy(reg)
