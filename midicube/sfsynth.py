import midicube.devices
import midicube.menu
import midicube.registration
import midicube.serialization as serialization
import mido
import fluidsynth
import glob

class ChannelData(serialization.Serializable):

    def __init__(self, sfid: int = 0, bank: int = 0, program: int = 0):
        super().__init__()
        self.sfid = sfid
        self.bank = bank
        self.program = program
    
    def __to_dict__(self):
        return {'sfid': self.sfid, 'bank': self.bank, 'program': self.program}
    
    def __from_dict__(dict):
        return ChannelData(dict['sfid'], dict['bank'], dict['program'])
    

class SoundFontSynthDeviceData(midicube.registration.AbstractDeviceData):

    def __init__(self):
        super().__init__()
    
    def __from_dict__(dict):
        inst = SoundFontSynthDeviceData()
        inst.__channels_from_dict__(dict)
        return inst
    
    @property
    def channel_data_type(self):
        return ChannelData


#TODO Clean Sound Font system
class SoundFontEntry:

    def __init__(self, name, sfid):
        self.name = name
        self.sfid = sfid

class SynthOutputDevice(midicube.devices.MidiOutputDevice):
    def __init__(self):
        super().__init__()
        self.synth: fluidsynth.Synth = None
    
    def load_sf(self, file: str):
        sfid = self.synth.sfload(file)
        split = file.split('/')
        self.soundfonts.append(SoundFontEntry(split[len(split) - 1], sfid))
        return sfid

    #def select_sf(self, channel: int, sfid: int):
    #    self.synth.sfont_select(channel, sfid)
    
    #def bank_change(self, channel: int, bank: int):
    #        self.synth.bank_select(channel, bank)
    
    #def program_change(self, channel: int, program: int):
    #        self.synth.program_change(channel, program)

    def sound_name(self, channel: int):
        return self.synth.channel_info(channel)[3].decode('utf-8')
    
    def curr_program(self, channel: int):
        return self.synth.channel_info(channel)[2]

    def curr_bank(self, channel: int):
        return self.synth.channel_info(channel)[1]

    def curr_sf(self, channel: int):
        return self.soundfonts[self.synth.channel_info(channel)[0] - 1]

    def program_select(self, channel: int, sfid: int, bank: int, program: int, save: bool = True):
        self.synth.program_select(channel, sfid, bank, program)
        if save:
            data = self.cube.reg().data(self).channel_data(channel)
            data.sfid = sfid
            data.bank = bank
            data.program = program

    def send (self, msg: mido.Message):
        print("Recieved message ", msg)
        print(str(self.synth.channel_info(msg.channel)))
        if msg.type == 'note_on':
            self.synth.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            self.synth.noteoff(msg.channel, msg.note)
        elif msg.type == 'program_change':
            #TODO Support banks
            self.program_select(msg.channel, curr_sf(msg.channel), curr_bank(msg.channel), msg.program)
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
        def create_sound_menu():
            options = [SynthSoundFontOption(channel.curr_value(), self, self.cube), SynthBankOption(channel.curr_value(), self, self.cube), SynthProgramOption(channel.curr_value(), self, self.cube)]
            return midicube.menu.OptionMenu(options)
        #Channel
        channel = midicube.menu.ValueMenuOption(create_sound_menu, "Select a Channel", [*range(16)])
                
        return midicube.menu.OptionMenu([channel])
    
    def get_identifier(self):
        return "FluidSynth"
    
    def init(self):
        #Create Synth
        self.synth = fluidsynth.Synth(gain=1)
        fluidsynth.fluid_settings_setstr(self.synth.settings, b'audio.driver', b'jack')
        fluidsynth.fluid_settings_setint(self.synth.settings, b'audio.jack.autoconnect', 1)
        self.synth.start('jack')
        self.soundfonts = []
        #Load soundfonts
        for f in glob.glob(self.cube.pers_mgr.directory + '/soundfonts/*.sf2'):
            self.load_sf(f)
        #Set up synth (Will be removed later)
        self.program_select(0, 1, 0, 0)
        self.on_reg_change()

    def on_reg_change(self):
        super().on_reg_change()
        data = self.cube.reg().data(self)
        for channel, sound in data.channels.items():
            self.program_select(channel, sound.sfid, sound.bank, sound.program)
    
    @property
    def data_type(self):
        return SoundFontSynthDeviceData

class SynthSoundFontOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice, cube):
        super().__init__()
        self.channel = channel
        self.synth = synth
        self.cube = cube

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
        self.synth.program_select(self.channel, sf, self.synth.curr_bank(self.channel), self.synth.curr_program(self.channel), self.cube)

    def decrease(self):
        sf = self.synth.curr_sf(self.channel).sfid - 1
        if sf < 1:
            sf = len(self.synth.soundfonts)
        self.synth.program_select(self.channel, sf, self.synth.curr_bank(self.channel), self.synth.curr_program(self.channel), self.cube)

class SynthProgramOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice, cube):
        super().__init__()
        self.channel = channel
        self.synth = synth
        self.cube = cube

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
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, self.synth.curr_bank(self.channel), prog, self.cube)

    def decrease(self):
        prog = self.synth.curr_program(self.channel) - 1
        if prog < 0:
            prog = 127
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, self.synth.curr_bank(self.channel), prog, self.cube)

class SynthBankOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, synth: SynthOutputDevice, cube):
        super().__init__()
        self.channel = channel
        self.synth = synth
        self.cube = cube

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
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, bank, self.synth.curr_program(self.channel), self.cube)

    def decrease(self):
        bank = self.synth.curr_bank(self.channel) - 1
        if bank < 0:
            bank = 127
        self.synth.program_select(self.channel, self.synth.curr_sf(self.channel).sfid, bank, self.synth.curr_program(self.channel), self.cube)
