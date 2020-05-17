import midicube.devices
import midicube.menu
import midicube.serialization as serialization
import pyo
import mido
import glob
import pathlib

class DrumKit(serialization.Serializable):

    def __init__(self):
        self.sounds = {}
        self.name = 'Drumkit'
        self.dir = '.'
    
    def sound(self, note):
        if note in self.sounds:
            return self.dir + '/' + self.sounds[note]
        return None
    
    def __from_dict__(dict):
        kit = DrumKit()
        print(dict)
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

class DrumKitOutputDevice(midicube.devices.MidiOutputDevice):

    def __init__(self):
        self.drumkits = []
        self.drumkit_index = 0
        self.dir = "/"
        self.playing = []
    
    def curr_drum(self):
        if self.drumkit_index < len(self.drumkits):
            return self.drumkits[self.drumkit_index]
        return None

    def init(self, cube):
        #Load drumkits
        self.dir = cube.pers_mgr.directory + '/drumkits'
        for f in glob.glob(self.dir + '/*/*.json'):
            print(f)
            path = pathlib.Path(f)
            try:
                with open(f, 'r') as file:
                    drumkit = serialization.deserialize(file.read(), DrumKit)
                    drumkit.dir = pathlib.Path(path.parent).name
                    self.drumkits.append(drumkit)
            except IOError:
                print("Failed to load drumkit ", f, "!")
        print(self.drumkits)
        #Server
        self.server = pyo.Server(audio='jack').boot()
        self.server.start()
        pass

    def program_select(self, index):
        self.drumkit_index = index #TODO Range check

    def send (self, msg: mido.Message):
        print(msg)
        #Note on
        if msg.type == 'note_on':
            print('Note on')
            drumkit = self.curr_drum()
            if drumkit != None:
                print('Found drumkit')
                sound = drumkit.sound(msg.note)
                if sound != None:
                    soundPath = self.dir + '/' + sound
                    print(soundPath)
                    print(msg.velocity/127.0)
                    sf = pyo.SfPlayer(soundPath).out()
                    self.playing.append(sf)
                    print('Playing sound')
        #Program change
        elif msg.type == 'program_change':
            program_select(msg.program)
        
        #Clean playing
        for sf in self.playing:
            if not sf.isPlaying():
                self.playing.remove(sf)

    def close (self):
        pass

    def create_menu(self):
        return None
    
    def get_identifier(self):
        return 'SampleDrumkit'
    
    def __str__(self):
        return 'SampleDrumkit'
