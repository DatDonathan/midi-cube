import midicube.devices
import midicube.menu
import mido
import fluidsynth


class SoundFontEntry:

    def __init__(self, name, sfid):
        self.name = name
        self.sfid = sfid

class SynthOutputDevice(midicube.devices.MidiOutputDevice):
    def __init__(self):
        print(fluidsynth)
        self.synth = fluidsynth.Synth(gain=1)
        #fluidsynth.fluid_settings_setnum(self.synth.settings, b'synth.audio-period-size', 64)
        #fluidsynth.fluid_settings_setnum(self.synth.settings, b'synth.audio-periods', 4)
        fluidsynth.fluid_settings_setstr(self.synth.settings, b'audio.driver', b'jack')
        fluidsynth.fluid_settings_setint(self.synth.settings, b'audio.jack.autoconnect', 1)
        self.synth.start('jack')
        self.soundfonts = []
    
    def load_sf(self, file: str):
        sfid = self.synth.sfload(file)
        self.soundfonts.append(SoundFontEntry(file, sfid))
        return sfid

    def select_sf(self, channel: int, sfid: int):
        self.synth.sfont_select(channel, sfid)
    
    def bank_change(self, channel: int, bank: int):
            self.synth.bank_select(channel, bank)
    
    def program_change(self, channel: int, program: int):
            self.synth.program_change(channel, program)

    def sound_name(self, channel: int):
        return self.synth.channel_info(channel)[3].decode('utf-8')
    
    def curr_program(self, channel: int):
        return self.synth.channel_info(channel)[2]

    def curr_bank(self, channel: int):
        return self.synth.channel_info(channel)[1]

    def curr_sf(self, channel: int):
        return self.soundfonts[self.synth.channel_info(channel)[0] - 1]

    def program_select(self, channel: int, sfid: int, bank: int, program: int):
        self.synth.program_select(channel, sfid, bank, program)

    def send (self, msg: mido.Message):
        print("Recieved message ", msg)
        print(str(self.synth.channel_info(msg.channel)))
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
        return "FluidSynth"

    def create_menu(self):
        #Sounds
        def create_sound_menu(channel: int):
            print("opening menu for channel ", str(channel))
            options = [SynthSoundFontOption(channel, self), SynthBankOption(channel, self), SynthProgramOption(channel, self)]
            return midicube.menu.OptionMenu(options)
        
        #Channel
        options = []
        for channel in range(16):
            options.append(midicube.menu.SimpleMenuOption(lambda ch = channel: create_sound_menu(ch), "Select a Channel", str(channel)))
                
        return midicube.menu.OptionMenu(options)
    
    def get_identifier(self):
        return "FluidSynth"
    
    def init(self, cube):
        pass

class SynthSoundFontOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice):
        self.channel = channel
        self.synth = synth

    def enter(self):
        return None
    
    def get_title(self):
        return "SoundFont"
    
    def get_value(self):
        return "(" + str(self.synth.curr_sf(self.channel).sfid) + ") " + self.synth.curr_sf(self.channel).name

    def increase(self):
        sf = self.synth.curr_sf(self.channel).sfid + 1
        if sf > len(self.synth.soundfonts):
            sf = 1
        self.synth.program_select(self.channel, sf, self.synth.curr_bank(self.channel), self.synth.curr_program(self.channel))

    def decrease(self):
        sf = self.synth.curr_sf(self.channel).sfid - 1
        if sf < 1:
            sf = len(self.synth.soundfonts)
        self.synth.program_select(self.channel, sf, self.synth.curr_bank(self.channel), self.synth.curr_program(self.channel))

class SynthProgramOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice):
        self.channel = channel
        self.synth = synth

    def enter(self):
        return None
    
    def get_title(self):
        return "Sound"
    
    def get_value(self):
        return "(" + str(self.synth.curr_program(self.channel)) + ") " + self.synth.sound_name(self.channel)

    def increase(self):
        prog = self.synth.curr_program(self.channel) + 1
        if prog > 127:
            prog = 0
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, self.synth.curr_bank(self.channel), prog)

    def decrease(self):
        prog = self.synth.curr_program(self.channel) - 1
        if prog < 0:
            prog = 127
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, self.synth.curr_bank(self.channel), prog)

class SynthBankOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice):
        self.channel = channel
        self.synth = synth

    def enter(self):
        return None
    
    def get_title(self):
        return "Bank"
    
    def get_value(self):
        return "(" + str(self.synth.curr_bank(self.channel)) + ") " + self.synth.sound_name(self.channel)

    def increase(self):
        bank = self.synth.curr_bank(self.channel) + 1
        if bank > 127:
            bank = 0
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, bank, self.synth.curr_program(self.channel))

    def decrease(self):
        bank = self.synth.curr_bank(self.channel) - 1
        if bank < 0:
            bank = 127
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, bank, self.synth.curr_program(self.channel))
