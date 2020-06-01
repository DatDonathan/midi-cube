from abc import ABC, abstractmethod
import mido
import midicube
import midicube.menu

class MidiListener:

    def __init__(self, channel: int, callback: callable):
        self.channel = channel
        self.callback = callback

class MidiInputDevice(ABC):

    def __init__ (self):
        self._cube: midicube.MidiCube = None
    
    @property
    def cube(self):
        return self._cube

    @cube.setter
    def cube(self, cube):
        if self._cube == None:
            self._cube = cube
        else:
            raise ValueError('cube is already set')

    @abstractmethod
    def add_listener (self, listener: MidiListener):
        pass

    @abstractmethod
    def close (self):
        pass

    @abstractmethod
    def get_identifier(self):
        return None

class MidiOutputDevice(ABC):

    def __init__ (self):
        self._cube: midicube.MidiCube = None
    
    @property
    def cube(self):
        return self._cube

    @cube.setter
    def cube(self, cube):
        if self._cube == None:
            self._cube = cube
        else:
            raise ValueError('cube is already set')
    
    @abstractmethod
    def send (self, msg):
        pass

    @abstractmethod
    def close (self):
        pass

    @abstractmethod
    def create_menu(sel):
        return None
    
    @abstractmethod
    def get_identifier(self):
        return None
    
    @abstractmethod
    def init(self):
        pass

    def on_reg_change(self):
        pass
    
    @property
    def data_type(self):
        return dict

class PortInputDevice(MidiInputDevice):

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.listeners = []
        self.port.callback = self.port_callback

    def port_callback (self, msg):
        for listener in self.listeners:
            if listener.channel < 0 or msg.channel == listener.channel:
                listener.callback(msg)

    def add_listener (self, listener: MidiListener):
        self.listeners.append(listener)

    def close (self):
        self.port.close()

    def __str__(self):
        return self.get_identifier()
    
    def get_identifier(self):
        return self.port.name[:self.port.name.rindex(' ')]

class PortOutputDevice(MidiOutputDevice):

    def __init__ (self, port):
        super().__init__()
        self.port = port
    
    def send (self, msg):
        print("Recieved message ", msg)
        self.port.send(msg)

    def close (self):
        self.port.close()
        
    def __str__(self):
        return self.get_identifier()

    def create_menu(self):
        return None

    def get_identifier(self):
        return self.port.name[:self.port.name.rindex(' ')]
    
    def init(self):
        pass