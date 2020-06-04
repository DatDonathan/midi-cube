from pyo import *
from midicube.devices import *
import mido
import time
import midicube.serialization as serialization
from copy import deepcopy
from enum import Enum

third = 4
fifth = 7
octave = 12

#Adds harmonic foldback to the passed midi notes
class MidiFoldback(PyoObject):

    def __init__(self, input: PyoObject, cutoff: int=115, mul=1, add=0):
        super().__init__()
        self._input = input
        self._cutoff = cutoff
        self._fallback = input - Max(Ceil((input - cutoff)/octave), 0) * octave
        self._base_objs = self._fallback._base_objs
    
    @property
    def cutoff(self):
        return self._cutoff

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

drawbar_offsets = [-octave, fifth, 0, octave, octave + fifth, 2 * octave, 2 * octave + third, 2 * octave + fifth, 3 * octave]
drawbar_amount = 9
sound_speed = 343.2
rotary_horn_radius = 0.15
rotary_horn_slow = 0.8
rotary_horn_fast = 6.8
rotary_horn_risetime = 1
rotary_horn_falltime = 1.6
rotary_bass_radius = 0.05
rotary_bass_slow = 0.76
rotary_bass_fast = 6.5
rotary_bass_risetime = 5.5
rotary_bass_falltime = 5.5

class RotorSpeed(Enum):
    NONE = 0
    SLOW = 1
    FAST = 2

#TODO: Information per channel
class B3OrganDeviceData(serialization.Serializable):

    def __init__(self, drawbars=[8 for i in range(drawbar_amount)], rotor_speed: RotorSpeed=RotorSpeed.NONE):
        self.drawbars = drawbars
        self.rotor_speed = rotor_speed
    
    def __from_dict__(dict):
        return B3OrganDeviceData(deepcopy(dict['drawbars']), RotorSpeed[dict['rotor_speed']])
    
    def __to_dict__(self):
        return {'drawbars': deepcopy(self.drawbars), 'rotor_speed': self.rotor_speed.name}

class OrganSynth:
    def __init__(self, osc: PyoObject, drawbars: PyoObject, bass_speed: PyoObject, horn_speed: PyoObject):
        self.osc = osc
        self.drawbars = drawbars
        self.bass_speed = bass_speed
        self.horn_speed = horn_speed

class B3OrganOutputDevice(MidiOutputDevice):

    def __init__ (self):
        super().__init__()
        #TODO: Move to organ data
        self.controls = [*[i + 1 for i in range(drawbar_amount - 1)], 8]
        self.rotor_control = 9
        self.rotor_speed_control = 10

    def _drawbar_list(self):
        data: B3OrganDeviceData = self.cube.reg().data(self)
        def _db(drawbar: int):
            return data.drawbars[drawbar]/8.0
        #return [_db(0), _db(2), _db(1), _db(3), 0, _db(4), 0, _db(5), 0, _db(6), 0, _db(7), 0, 0, 0, _db(8)]
        return [_db(i) for i in range(drawbar_amount)]
    
    def _bass_speed(self):
        data: B3OrganDeviceData = self.cube.reg().data(self)
        if data.rotor_speed == RotorSpeed.NONE:
            return 0
        elif data.rotor_speed == RotorSpeed.SLOW:
            return rotary_bass_slow
        elif data.rotor_speed == RotorSpeed.FAST:
            return rotary_bass_fast

    def _horn_speed(self):
        data: B3OrganDeviceData = self.cube.reg().data(self)
        if data.rotor_speed == RotorSpeed.NONE:
            return 0
        elif data.rotor_speed == RotorSpeed.SLOW:
            return rotary_horn_slow
        elif data.rotor_speed == RotorSpeed.FAST:
            return rotary_horn_fast

    # Registration-Nr:    1   2   3   4   5   6   7   8   9
    # Harmonic:           1   3   2   4   6   8   10  12  16
    def _create_synth(self, midi: MidiBuffer):
        drawbar_sigs = [Sig(0) for i in range(drawbar_amount)]
        bass_speed = Sig(0)
        horn_speed = Sig(0)
        #Organ
        vel = Ceil(midi.velocity)/drawbar_amount
        sines = []
        for i in range(len(drawbar_offsets)):
            offset = drawbar_offsets[i]
            pitch = MToF(MidiFoldback(midi.note + offset))
            sine = FastSine(freq=pitch, mul=vel * drawbar_sigs[i]).mix(1)
            sines.append(sine)
        osc = Mix(sines, voices=2, mul=0.5)

        bass_rotation = FastSine(freq=Port(bass_speed, risetime=rotary_bass_risetime, falltime=rotary_bass_falltime), mul=rotary_bass_radius/sound_speed)
        horn_rotation = FastSine(freq=Port(horn_speed, risetime=rotary_horn_risetime, falltime=rotary_horn_falltime), mul=rotary_horn_radius/sound_speed)

        #table = HarmTable(self._drawbar_list())
        #osc = Osc(table, freq=MToF(midi.note - octave), mul=Port(Ceil(midi.velocity) * (0.5 * 0.8/len(drawbar_offsets))))

        #Rotary Speaker
        bass = Biquad(osc, freq=800, type=0, mul=0.5)
        horn = Biquad(osc, freq=800, type=1, mul=0.5)

        bass_delay = Delay(bass, delay=bass_rotation).mix(1)
        horn_delay = Delay(horn, delay=horn_rotation).mix(1)

        return OrganSynth(Chorus(Mix([osc, bass_delay, horn_delay], voices=2), depth=horn_speed/5), drawbar_sigs, bass_speed, horn_speed)
    
    def _update_synths(self):
        #TODO channel specific
        drawbars = self._drawbar_list()
        bass_speed = self._bass_speed()
        horn_speed = self._horn_speed()
        for synth in self.synths:
            for i in range(drawbar_amount):
                synth.drawbars[i].value = drawbars[i]
            synth.bass_speed.value = bass_speed
            synth.horn_speed.value = horn_speed
        #for synth in self.synths:
        #    synth.table.replace(drawbars)

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
        #Control change
        if msg.type == 'control_change':
            data: B3OrganDeviceData = self.cube.reg().data(self)
            old_drawbars = deepcopy(data.drawbars)
            #Update drawbar data
            for i in range(len(self.controls)):
                if self.controls[i] == msg.control:
                    data.drawbars[i] = round(msg.value/127 * 8)
            #Rotary
            old_rotor_speed = data.rotor_speed
            #Stop
            if msg.control == self.rotor_control:
                if msg.value == 0:
                    data.rotor_speed = RotorSpeed.NONE
            elif msg.control == self.rotor_speed_control:
                if msg.value == 0:
                    data.rotor_speed = RotorSpeed.SLOW
                else:
                    data.rotor_speed = RotorSpeed.FAST
            #Speed
            if old_drawbars != data.drawbars or old_rotor_speed != data.rotor_speed:
                print(data.drawbars)
                print(data.rotor_speed)
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