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

class MidiOutputDevice(ABC):

    def __init__ (self):
        pass

    def bind (self, indev, inchannel=-1, outchannel=-1):
        indev.add_listener(MidiListener(inchannel, lambda msg : self.callback(msg, outchannel)))

    def callback(self, msg, outchannel):
        if outchannel >= 0:
            msg.channel = outchannel
        self.send(msg)
    
    @abstractmethod
    def send (self, msg):
        pass

    @abstractmethod
    def close (self):
        pass

    @abstractmethod
    def create_menu():
        return None

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

class PortOutputDevice(MidiOutputDevice):

    def __init__ (self, port):
        self.port = port
    
    def send (self, msg):
        self.port.send(msg)

    def close (self):
        self.port.close()
        
    def __str__(self):
        return self.port.name

    def create_menu():
        return None

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
            self.inputs.append(PortInputDevice(device))
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

    def create_menu (self):
        #Bind device menu

        #Option list
        options = [midicube.menu.SimpleMenuOption(self.__bind_device_menu, "Bind Devices", ""), midicube.menu.SimpleMenuOption(self.__bind_device_menu, "Set Up Devices", "")]
        menu = midicube.menu.OptionMenu(options)
        return menu

    def __bind_device_menu(self):
        #Callback
        def enter ():
            out_device.curr_value().bind(in_device.curr_value(), in_channel.curr_value(), out_channel.curr_value())
            return None
        #Options
        in_device = midicube.menu.ValueMenuOption(enter, "Input Device", self.inputs)
        out_device = midicube.menu.ValueMenuOption(enter, "Output Device", self.outputs)
        in_channel = midicube.menu.ValueMenuOption(enter, "Input Channel", range(-1, 16))
        out_channel = midicube.menu.ValueMenuOption(enter, "Output Channel", range(-1, 16))
        #Menu
        return midicube.menu.OptionMenu([in_device, out_device, in_channel, out_channel])

    def __setup_device_menu(self):
        #Callback
        def enter ():
            return device.curr_value().create_menu()
        #Options
        device = midicube.menu.ValueMenuOption(enter, "Device", self.output)
        #Menu
        return midicube.menu.OptionMenu([device])
