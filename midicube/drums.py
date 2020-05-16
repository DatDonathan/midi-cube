import midicube.devices
import midicube.menu
import midicube.serialization as serialization
import pyo
import mido

class DrumKit(serialization.Serializable):

    def __init__(self):
        self.sounds = {}
        self.name = 'Drumkit'
        self.dir = '.'
    
    def sound(self, note):
        if self.sounds[note] != None:
            return self.dir + '/' + self.sounds[note]
        return None
    
    def __from_dict__(dict):
        kit = DrumKit()
        for key, value in dict:
            kit.sounds[int(key)] = value
        return kit
    
    def __to_dict__(self):
        dict = {}
        for key, value in self.sounds:
            dict[str(key)] = value
        return dict

class DrumKitOutputDevice(midicube.devices.MidiOutputDevice):

    def __init__(self):
        self.drumkits = []
        self.drumkit_index = 0
        self.dir = "/"
    
    def curr_drum(self):
        if self.drumkit_index < len(self.drumkits):
            return self.drumkits[self.drumkit_index]
        return None

    def init(self, cube):
        self.dir = cube.pers_mgr.directory + '/drumkits'
        self.server = pyo.Server()
        self.server.start()
        pass

    def program_select(self, index):
        self.drumkit_index = index #TODO Range check

    def send (self, msg: mido.Message):
        #Note on
        if msg.type == 'note_on':
            drumkit = self.curr_drum()
            if drumkit != None:
                sound = drumkit.sound(msg.note)
                if sound != None:
                    soundPath = self.dir + '/' + sound
                    pyo.SfPlayer(soundPath, mul=msg.velocity/127).out()
        #Program change
        elif msg.type == 'program_change':
            program_select(msg.program)

    def close (self):
        pass

    def create_menu(self):
        return None
    
    def get_identifier(self):
        return 'SampleDrumkit'
