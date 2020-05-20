from abc import ABC, abstractmethod
import mido
import midicube.menu

class MidiListener:

    def __init__(self, channel: int, callback: callable):
        self.channel = channel
        self.callback = callback

class MidiInputDevice(ABC):

    def __init__ (self):
        pass

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
        pass
    
    @abstractmethod
    def send (self, msg, cube):
        pass

    @abstractmethod
    def close (self):
        pass

    @abstractmethod
    def create_menu(self, cube):
        return None
    
    @abstractmethod
    def get_identifier(self):
        return None
    
    @abstractmethod
    def init(self, cube):
        pass

    def on_reg_change(self, cube):
        pass
    
    def data_type(self):
        return dict

class PortInputDevice(MidiInputDevice):

    def __init__(self, port):
        super()
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
        return self.port.name
    
    def get_identifier(self):
        return self.port.name

class PortOutputDevice(MidiOutputDevice):

    def __init__ (self, port):
        self.port = port
    
    def send (self, msg, cube):
        print("Recieved message ", msg)
        self.port.send(msg)

    def close (self):
        self.port.close()
        
    def __str__(self):
        return self.port.name

    def create_menu(self, menu):
        return None

    def get_identifier(self):
        return self.port.name
    
    def init(self, cube):
        pass