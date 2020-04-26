from abc import ABC, abstractmethod
import mido
import fluidsynth
import threading

class MidiInputDevice(ABC):

    def __init__ (self):
        pass

    @abstractmethod
    def add_listener (self, callback):
        pass

    @abstractmethod
    def close (self):
        pass

class MidiOutputDevice(ABC):

    def __init__ (self):
        pass

    def bind (self, indev):
        indev.add_listener(lambda msg : self.send(msg))
    
    @abstractmethod
    def send (self, msg):
        pass

    @abstractmethod
    def close (self):
        pass

class PortInputDevice(MidiInputDevice):

    def __init__(self, port):
        super()
        self.port = port
        self.listeners = []
        self.running = True
        self.thread = threading.Thread(target=self.listen_loop, args=())

    def init(self):
        self.thread.start()
        return self

    def listen_loop (self):
        while self.running:
            msg = self.port.receive()
            for l in self.listeners:
                l(msg)

    def add_listener (self, callback):
        self.listeners.append(callback)

    def close (self):
        running = False
        self.port.close()

    def __str__(self):
        return self.port.name

class PortOutputDevice(MidiOutputDevice):

    def __init__ (self, port):
        self.port = port
    
    def send (self, msg):
        self.port.send(msg)

    def close (self):
        self.port.close()
        
    def __str__(self):
        return self.port.name

class SynthOutputDevice(MidiOutputDevice):
    def __init__(self):
        print(fluidsynth)
        self.synth = fluidsynth.Synth()
        self.synth.start('alsa')
    
    def load_sf(self, file: str):
        return self.synth.sfload(file)

    def send (self, msg: mido.Message):
        print("Recieved message ", msg)
        if msg.type == 'note_on':
            self.synth.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            self.synth.noteoff(msg.channel, msg.note)
        elif msg.type == 'program_change':
            self.synth.program_select(msg.channel, msg.program, 0, 0)
        elif msg.type == 'control_change':
            self.synth.cc(msg.channel, msg.control, msg.value)
        elif msg.type == 'pitchwheel':
            self.synth.pitch_bend(msg.channel, msg.pitch)
        else:
            print('Unrecognized message type:', msg)

    def close (self):
        self.synth.delete()
    
    def __str__ (self):
        return "FluidSynth Sythesizer"

class MidiCube:

    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        if self.inputs == None:
            self.inputs = []
        if self.outputs == None:
            self.outputs = []
    
    def load_devices (self):
        for name in mido.get_input_names():
            device = mido.open_input(name)
            self.inputs.append(PortInputDevice(device).init())
        for name in mido.get_output_names():
            device = mido.open_output(name)
            self.outputs.append(PortOutputDevice(device))

    def close (self):
        for inport in self.inputs:
            try:
                inport.close()
            except:
                pass
        for outport in self.outputs:
            try:
                outport.close()
            except:
                pass
            