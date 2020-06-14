from pyo import *
import mido
import time#
import midicube.devices
from midicube.devices import *

#Like Notein, Bendin, etc. but with input from mido devices
#Channels numbers are all in pyo scale
class MidiBuffer(PyoObject):

    def __init__(self, channel=0, poly=10, mul=1, add=0):
        super().__init__(mul, add)
        self._channel = channel
        self._poly = 10
        self._press_times = [0 for i in range(poly)]
        self._note = [Sig(0) for i in range(poly)]
        self._velocity = [Sig(0.0) for i in range(poly)]
        #self._control = [Sig(0) for i in range(127)]
        #self._control_listeners = []
    
    def _find_note_slot(self):
        oldest = None
        oldest_index = -1
        for i in range(self.poly):
            if self._velocity[i].value == 0:
                return i
            elif oldest == None or oldest > self._press_times[i]:
                oldest_index = i
                oldest = self._press_times[i]
        return oldest_index
    
    def note_on(self, note: int, velocity: float):
        slot = self._find_note_slot()
        self._velocity[slot].value = velocity
        self._note[slot].value = note
        self._press_times[slot] = time.time()
    
    def note_off(self, note: int):
        for i in range(self.poly):
            if self._note[i].value == note:
                self._velocity[i].value = 0.0

    #def control_change(self, control: int, value: int):
    #    self._control[control].value = value
    #    for l in self._control_listeners:
    #        l(control, value)
    
    def send(self, msg: mido.Message):
        if self._channel == msg.channel + 1 or self._channel == 0:
            if msg.type == 'note_on':
                self.note_on(msg.note, msg.velocity/127.0)
            elif msg.type == 'note_off':
                self.note_off(msg.note)
            elif msg.type == 'program_change':
                pass
            elif msg.type == 'control_change':
                #self.control_change(msg.control, msg.value)
                pass
            elif msg.type == 'pitchwheel':
                pass

    @property
    def poly(self):
        return self._poly
    
    @property
    def note(self):
        return Dummy(self._note)
    
    @property
    def velocity(self):
        return Dummy(self._velocity)
    
    #@property
    #def control(self):
    #    return Dummy(self._control)
    
    #@property
    #def control_listeners(self):
    #    return self.control_listeners

class DummyInput(MidiInputDevice):

    def __init__(self, identifier: str):
        super().__init__()
        self.listeners = []
        self.identifier = identifier
    
    def send(self, msg: mido.Message):
        for l in self.listeners:
            if l.channel < 0 or l.channel == msg.channel:
                l.callback(msg)

    def add_listener (self, listener: midicube.devices.MidiListener):
        self.listeners.append(listener)

    def close (self):
        pass

    def get_identifier(self):
        return self.identifier


