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
    def create_menu(self):
        return None
    
    @abstractmethod
    def get_identifier(self):
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
    
    def get_identifier(self):
        return self.port.name

class PortOutputDevice(MidiOutputDevice):

    def __init__ (self, port):
        self.port = port
    
    def send (self, msg):
        print("Recieved message ", msg)
        self.port.send(msg)

    def close (self):
        self.port.close()
        
    def __str__(self):
        return self.port.name

    def create_menu(self):
        return None

    def get_identifier(self):
        return self.port.name

class DeviceBinding:

    def __init__(self, input_id, output_id, input_channel = -1, output_channel = -1):
        self.input_id = input_id
        self.output_id = output_id
        self.input_channel = input_channel
        self.output_channel = output_channel

    def apply (msg, cube, inport: MidiInputDevice):
        outport = cube.outputs[self.output_id]
        if outport != None and inport.get_identifier() == self.input_id and (self.input_channel < 0 or msg.channel == self.input_channel):
            if self.output_channel >= 0:
                msg.channel = self.output_channel
            listener.callback(msg)


class MidiCube:

    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.bindings = []
    
    def add_input(self, device: MidiInputDevice):
        self.inputs[device.get_identifier()] = device
        #Add Binding callback
        def callback(msg: mido.Message):
            for binding in bindings:
                binding.apply(msg.copy(), self, device)

    def add_output(self, device: MidiOutputDevice):
        self.outputs[device.get_identifier()] = device
    
    def load_devices (self):
        for name in mido.get_input_names():
            device = mido.open_input(name)
            self.add_input(PortInputDevice(device))
        for name in mido.get_output_names():
            device = mido.open_output(name)
            self.add_output(PortOutputDevice(device))

    def close (self):
        for key, inport in self.inputs.items():
            try:
                inport.close()
            except:
                pass
        for key, outport in self.outputs.items():
            try:
                outport.close()
            except:
                pass

    def create_menu (self):
        #Bind device menu

        #Option list
        options = [midicube.menu.SimpleMenuOption(self.__bind_device_menu, "Bind Devices", ""), midicube.menu.SimpleMenuOption(self.__setup_device_menu, "Set Up Devices", "")]
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
        device = midicube.menu.ValueMenuOption(enter, "Device", self.outputs)
        #Menu
        return midicube.menu.OptionMenu([device])
