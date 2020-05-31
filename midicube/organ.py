from pyo import *
from midicube.devices import *
import mido
import time

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
    
    def _find_note_slot(self):
        oldest = None
        oldest_index = -1
        for i in range(self.poly):
            if self._velocity[i].value == 0:
                return i
            elif oldest == None or oldest > self._press_times[i]:
                oldest_index = i
                oldest = self._press_times[i]
    
    def note_on(self, note: int, velocity: float):
        slot = self._find_note_slot()
        self._velocity[slot].value = velocity
        self._note[slot].value = note
        self._press_times[slot] = time.time()
    
    def note_off(self, note: int):
        for i in range(self.poly):
            if self._note[i].value == note:
                self._velocity[i].value = 0.0
    
    def send(self, msg: mido.Message):
        if self._channel == msg.channel + 1 or self._channel == 0:
            if msg.type == 'note_on':
                self.note_on(msg.note, msg.velocity/127.0)
            elif msg.type == 'note_off':
                self.note_off(msg.note)
            elif msg.type == 'program_change':
                pass
            elif msg.type == 'control_change':
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


class B3OrganDeviceData:

    def __init__(self, drawbars=[8, 8, 8, 8, 8, 8, 8, 8, 8]):
        self.drawbars = drawbars

class B3OrganOutputDevice(MidiOutputDevice):

    def __init__ (self):
        super().__init__()

    def _create_synth(self, midi: MidiBuffer):
        pitch = MToF(midi.note)
        return Sine(freq=pitch, mul=Ceil(midi.velocity))

    def init(self):
        self.midis = [MidiBuffer(i + 1) for i in range(16)]
        self.synths = [self._create_synth(self.midis[i]) for i in range(16)]
        for synth in self.synths:
            synth.out()
    
    def send (self, msg: mido.Message):
        print("Recieved message ", msg)
        for midi in self.midis:
            midi.send(msg)

    def close (self):
        for synth in self.synths:
            synth.stop()

    def create_menu(sel):
        return None
    
    def get_identifier(self):
        return "B3 Organ"

    def __str__(self):
        self.get_identifier()