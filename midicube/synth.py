import midicube
import midicube.menu
import mido
import fluidsynth


class SoundFontEntry:

    def __init__(self, name, sfid):
        self.name = name
        self.sfid = sfid

class SynthOutputDevice(midicube.MidiOutputDevice):
    def __init__(self):
        print(fluidsynth)
        self.synth = fluidsynth.Synth(gain=1)
        self.synth.start('alsa')
        self.soundfonts = []
    
    def load_sf(self, file: str):
        sfid = self.synth.sfload(file)
        self.soundfonts.append(SoundFontEntry(file, sfid))
        return sfid

    def select_sf(self, sfid: int, channel: int):
        self.synth.sfont_select(channel, sfid)
    
    def sound_name(self, channel: int):
        return self.synth.channel_info(channel).name
    
    def curr_program(self, channel: int):
        return self.synth.channel_info(channel).program

    def curr_bank(self, channel: int):
        return self.synth.channel_info(channel).bank

    def program_select(self, channel: int, bank: int, program: int):
        self.synth.program_select(channel, bank, preset)

    def send (self, msg: mido.Message):
        print("Recieved message ", msg)
        if msg.type == 'note_on':
            self.synth.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            self.synth.noteoff(msg.channel, msg.note)
        elif msg.type == 'program_change':
            #TODO Support banks
            self.synth.program_change(msg.channel, msg.program)
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

    def create_menu():
        options = []
        for sf in self.soundfonts:
            values = []
            #TODO
        return None

class SynthProgramOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice):
        self.channel = channel
        self.synth = synth

    def enter(self):
        return None
    
    def get_title(self):
        return "Sound"
    
    def get_value(self):
        return "(" + str(self.synth.curr_program()) + ") " + self.synth.sound_name()

    def increase(self):
        prog = self.synth.curr_program() + 1
        if prog > 127:
            prog = 0
        self.synth.program_select(self.channel, self.synth.curr_bank(), prog)

    def decrease(self):
        prog = self.synth.curr_program() - 1
        if prog < 0:
            prog = 127
        self.synth.program_select(self.channel, self.synth.curr_bank(), prog)

class SynthBankOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice):
        self.channel = channel
        self.synth = synth

    def enter(self):
        return None
    
    def get_title(self):
        return "Bank"
    
    def get_value(self):
        return "(" + str(self.synth.curr_bank()) + ") " + self.synth.sound_name()

    def increase(self):
        bank = self.synth.curr_bank() + 1
        if bank > 127:
            bank = 0
        self.synth.program_select(self.channel, bank, self.synth.curr_program())

    def decrease(self):
        bank = self.synth.curr_bank() - 1
        if bank < 0:
            bank = 127
        self.synth.program_select(self.channel, bank, self.synth.curr_program())