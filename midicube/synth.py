from pyo import *
from midicube.devices import *
import mido
import midicube.serialization as serialization
from copy import deepcopy
from midicube.utils import *

class SynthInstance:

    def __init__(self, osc: PyoObject):
        self.osc = osc

class SynthOutputDevice(MidiOutputDevice):

    def __init__ (self):
        super().__init__()

    # Registration-Nr:    1   2   3   4   5   6   7   8   9
    # Harmonic:           1   3   2   4   6   8   10  12  16
    def _create_synth(self, midi: MidiBuffer):
        #Detuned Saw sound
        table = SawTable(order=50)
        velocity = MidiAdsr(Ceil(midi.velocity), 0.001, -1, 1.0, 0.05, mul=1/3)
        osc1 = Osc(table, freq=MToF(midi.note), mul=velocity).mix(1)
        osc2 = Osc(table, freq=MToF(midi.note + 0.1), mul=velocity).mix(1)
        osc3 = Osc(table, freq=MToF(midi.note - 0.1), mul=velocity).mix(1)
        return SynthInstance(Mix([osc1, osc2, osc3], voices=2))

    def _update_synths(self):
        #TODO channel specific
        pass

    def init(self):
        #TODO channel specific
        self.midis = [MidiBuffer(i + 1) for i in range(16)]
        self.synths = [self._create_synth(self.midis[i]) for i in range(1)]
        self.synths[0].osc.out()
    
    def send (self, msg: mido.Message):
        #TODO update registration
        print("Recieved message ", msg)
        #Midi ins
        for midi in self.midis:
            midi.send(msg)

    def close (self):
        for synth in self.synths:
            synth.osc.stop()

    def create_menu(sel):
        return None
    
    def get_identifier(self):
        return "Synth"

    def __str__(self):
        self.get_identifier()
    
    def on_reg_change(self):
        super().on_reg_change()
        self._update_synths()
    
    @property
    def data_type(self):
        return dict
