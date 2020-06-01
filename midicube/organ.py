from pyo import *
from midicube.devices import *
import mido
import time
import midicube.serialization as serialization
from copy import deepcopy

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

third = 4
fifth = 7
octave = 12
drawbar_offset = [-octave, fifth, 0, octave, octave + fifth, 2 * octave, 2 * octave + third, 2 * octave + fifth, 3 * octave]
drawbar_amount = 9

#TODO: Information per channel
class B3OrganDeviceData(serialization.Serializable):

    def __init__(self, drawbars=[8 for i in range(drawbar_amount)]):
        self.drawbars = drawbars
    
    def __from_dict__(dict):
        return B3OrganDeviceData(deepcopy(dict['drawbars']))
    
    def __to_dict__(self):
        return {'drawbars': deepcopy(self.drawbars)}

class OrganSynth:

    def __init__(self, table: HarmTable, osc: Osc):
        self.table = table
        self.osc = osc

class B3OrganOutputDevice(MidiOutputDevice):

    def __init__ (self):
        super().__init__()
        #TODO: Move to organ data
        self.controls = [*[i + 1 for i in range(drawbar_amount - 1)], 8]
    
    def _drawbar_list(self):
        data: B3OrganDeviceData = self.cube.reg().data(self)
        def _db(drawbar: int):
            return data.drawbars[drawbar]/8.0
        return [_db(0), _db(2), _db(1), _db(3), 0, _db(4), 0, _db(5), 0, _db(6), 0, _db(7), 0, 0, 0, _db(8)]

    # Registration-Nr:    1   2   3   4   5   6   7   8   9
    # Harmonic:           1   3   2   4   6   8   10  12  16
    def _create_synth(self, midi: MidiBuffer):
        def _db(drawbar: int, midi: MidiBuffer):
            return Floor(midi.control[self.controls[drawbar]]*(8/127))/8
        #sines = []
        #for offset in drawbar_offset:
        #    pitch = MToF(midi.note + offset)
        #    sine = Sine(freq=pitch, mul=Ceil(midi.velocity) * 1.0/len(drawbar_offset))
        #    sines.append(sine)
        #return Mix(sines)
        table = HarmTable(self._drawbar_list())
        osc = Osc(table, freq=MToF(midi.note - octave), mul=Ceil(midi.velocity) * 0.8/len(drawbar_offset))
        return OrganSynth(table, osc)
    
    def _update_synths(self):
        #TODO channel specific
        drawbars = self._drawbar_list()
        for synth in self.synths:
            synth.table.replace(drawbars)

    def init(self):
        self.midis = [MidiBuffer(i + 1) for i in range(16)]
        self.synths = [self._create_synth(self.midis[i]) for i in range(16)]
        for synth in self.synths:
            synth.osc.out()
    
    def send (self, msg: mido.Message):
        #TODO update registration
        print("Recieved message ", msg)
        #Midi ins
        for midi in self.midis:
            midi.send(msg)
        #Control change
        if msg.type == 'control_change':
            data: B3OrganDeviceData = self.cube.reg().data(self)
            old_drawbars = deepcopy(data.drawbars)
            #Update drawbar data
            for i in range(len(self.controls)):
                if self.controls[i] == msg.control:
                    data.drawbars[i] = round(msg.value/127 * 8)
            if old_drawbars != data.drawbars:
                print(data.drawbars)
                self._update_synths()
                

    def close (self):
        for synth in self.synths:
            synth.osc.stop()

    def create_menu(sel):
        return None
    
    def get_identifier(self):
        return "B3 Organ"

    def __str__(self):
        self.get_identifier()
    
    def on_reg_change(self):
        super().on_reg_change()
        self._update_synths()
        #data: B3OrganDeviceData = self.cube.reg().data(self)
        #for i in range(len(data.drawbars)):
        #    for midi in self.midis:
        #        midi.control_change(data.controls[i], data.drawbars[i])
    
    @property
    def data_type(self):
        return B3OrganDeviceData