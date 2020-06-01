import midicube.devices
import midicube.menu
import midicube.serialization as serialization
import pyo
import mido
import glob
import pathlib

class DrumKit(serialization.Serializable):

    def __init__(self):
        super().__init__()
        self.sounds = {}
        self.name = 'Drumkit'
        self.dir = '.'
    
    def sound(self, note):
        if note in self.sounds:
            return self.dir + '/' + self.sounds[note]
        return None
    
    def __from_dict__(dict):
        kit = DrumKit()
        kit.name = dict['name']
        sounds = dict['sounds']
        for key, value in sounds.items():
            kit.sounds[int(key)] = value
        return kit
    
    def __to_dict__(self):
        dict = {}
        dict['name'] = self.name
        dict['sounds'] = {}
        for key, value in self.sounds.items():
            dict['sounds'][str(key)] = value
        return dict

    def __str__(self):
        return self.name

class ChannelData(serialization.Serializable):

    def __init__(self, program: int=0):
        super().__init__()
        self.program = program
    
    def __to_dict__(self):
        return {'program': self.program}

    def __from_dict__(dict):
        return ChannelData(dict['program'])

class DrumKitDeviceData(serialization.Serializable):

    def __init__(self):
        super().__init__()
        self.channels = {}
    
    def channel_info(self, channel: int):
        if not channel in self.channels:
            self.channels[channel] = ChannelData()
        return self.channels[channel]
    
    def __to_dict__(self):
        dict = {'channels': {}}
        for key, value in self.channels.items():
            dict['channels'][str(key)] = value.__to_dict__()
        return dict
    
    def __from_dict__(dict):
        data = DrumKitDeviceData()
        for key, value in dict['channels'].items():
            data.channels[int(key)] = ChannelData.__from_dict__(value)
        return data
        

class DrumKitOutputDevice(midicube.devices.MidiOutputDevice):

    def __init__(self):
        super().__init__()
        self.drumkits = []
        self.dir = "/"
        self.playing = []
    
    def curr_program(self, channel: int):
        return self.cube.reg().data(self).channel_info(channel).program

    def curr_drum(self, channel: int):
        drumkit_index = self.curr_program(channel)
        if drumkit_index >= 0 and drumkit_index < len(self.drumkits):
            return self.drumkits[drumkit_index]
        return None

    def init(self):
        #Load drumkits
        self.dir = self.cube.pers_mgr.directory + '/drumkits'
        for f in glob.glob(self.dir + '/*/*.json'):
            path = pathlib.Path(f)
            try:
                with open(f, 'r') as file:
                    drumkit = serialization.deserialize(file.read(), DrumKit)
                    drumkit.dir = pathlib.Path(path.parent).name
                    self.drumkits.append(drumkit)
            except IOError:
                print("Failed to load drumkit ", f, "!")

    def program_select(self, channel: int, program: int):
        self.cube.reg().data(self).channel_info(channel).program = max(min(len(self.drumkits) - 1, program), 0)   #TODO Range check

    def send (self, msg: mido.Message):
        print("Recieved message " + str(msg))
        #Note on
        if msg.type == 'note_on':
            drumkit = self.curr_drum(msg.channel)
            if drumkit != None:
                sound = drumkit.sound(msg.note)
                if sound != None:
                    soundPath = self.dir + '/' + sound
                    sf = pyo.SfPlayer(soundPath, mul=msg.velocity/127.0).out()
                    self.playing.append(sf)
        #Program change
        elif msg.type == 'program_change':
            program_select(msg.program)
        #Clean playing
        for sf in self.playing:
            if not sf.isPlaying():
                self.playing.remove(sf)

    def close (self):
        for sf in self.playing:
            sf.stop()
        self.playing.clear()

    def create_menu(self):
        #Sounds
        def create_sound_menu():
            options = [DrumKitProgramOption(channel.curr_value(), self)]
            return midicube.menu.OptionMenu(options)
        #Channel
        channel = midicube.menu.ValueMenuOption(create_sound_menu, "Select a Channel", [*range(16)])
                
        return midicube.menu.OptionMenu([channel])
    
    def get_identifier(self):
        return 'SampleDrumkit'
    
    def __str__(self):
        return 'SampleDrumkit'
    
    @property
    def data_type(self):
        return DrumKitDeviceData

class DrumKitProgramOption(midicube.menu.MenuOption):

    def __init__(self, channel: int, drums: DrumKitOutputDevice):
        super().__init__()
        self.channel = channel
        self.drums = drums
    
    def enter(self):
        return None

    def increase(self):
        self.drums.program_select(self.channel, self.drums.curr_program(self.channel) + 1)

    def decrease(self):
        self.drums.program_select(self.channel, self.drums.curr_program(self.channel) - 1)

    def get_title(self):
        return "Select Drumkit"

    def get_value(self):
        return "(" + str(self.drums.curr_program(self.channel)) + ") " + str(self.drums.curr_drum(self.channel))
