import mido
import midicube.menu
from midicube.devices import *
from midicube.registration import *
import os
import os.path
import json

class PersistenceManager():

    def __init__(self, directory = './data', reg_file='registrations.json'):
        self.directory = directory
        self.reg_file = reg_file
    
    def load(self, cube):
        os.makedirs(self.directory, exist_ok=True)
        #Registrations
        reg_file = self.directory + '/' + self.reg_file
        if os.path.isfile(reg_file):
            with open(reg_file, 'r') as file:
                cube.reg_mgr.load(json.loads(file.read()))

    def save(self, cube):
        os.makedirs(self.directory, exist_ok=True)
        #Registrations
        with open(self.directory + '/' + self.reg_file, 'w') as file:
            file.write(json.dumps(cube.reg_mgr.save()))

class MidiCube:

    def __init__(self, pers_mgr = PersistenceManager()):
        self.inputs = {}
        self.outputs = {}
        self.reg_mgr = RegistrationManager()
        self.pers_mgr = pers_mgr

    def reg(self):
        return self.reg_mgr.cur_reg
    
    def add_input(self, device: MidiInputDevice):
        self.inputs[device.get_identifier()] = device
        #Add Binding callback
        def callback(msg: mido.Message):
            for binding in self.reg().bindings:
                binding.apply(msg.copy(), self, device)
        device.add_listener(MidiListener(-1, callback))

    def add_output(self, device: MidiOutputDevice):
        device.init(self)
        self.outputs[device.get_identifier()] = device
        print('Added output: ' + device.get_identifier())
    
    def load_devices (self):
        for name in mido.get_input_names():
            device = mido.open_input(name)
            self.add_input(PortInputDevice(device))
        for name in mido.get_output_names():
            device = mido.open_output(name)
            self.add_output(PortOutputDevice(device))

    def init(self):
        self.pers_mgr.load(self)
        print("Loaded Registrations")

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
        self.pers_mgr.save(self)
        print("Saved registrations!")

    def create_menu (self):
        #Option list
        options = [midicube.menu.SimpleMenuOption(self.__bind_device_menu, "Bind Devices", ""), midicube.menu.SimpleMenuOption(self.__setup_device_menu, "Set Up Devices", ""), midicube.menu.SimpleMenuOption(self.__delete_binding_menu, "Delete Bindings", ""), midicube.menu.SimpleMenuOption(self.__registration_menu, "Registrations", "")]
        menu = midicube.menu.OptionMenu(options)
        return menu

    def __bind_device_menu(self):
        #Callback
        def enter ():
            self.reg().bindings.append(DeviceBinding(in_device.curr_value(), out_device.curr_value(), in_channel.curr_value(), out_channel.curr_value()))
            #out_device.curr_value().bind(in_device.curr_value(), in_channel.curr_value(), out_channel.curr_value())
            return None
        #Options
        in_device = midicube.menu.ValueMenuOption(enter, "Input Device", [*self.inputs.keys()])
        out_device = midicube.menu.ValueMenuOption(enter, "Output Device", [*self.outputs.keys()])
        in_channel = midicube.menu.ValueMenuOption(enter, "Input Channel", range(-1, 16))
        out_channel = midicube.menu.ValueMenuOption(enter, "Output Channel", range(-1, 16))
        #Menu
        return midicube.menu.OptionMenu([in_device, out_device, in_channel, out_channel])

    def __setup_device_menu(self):
        #Callback
        def enter ():
            return device.curr_value().create_menu()
        #Options
        device = midicube.menu.ValueMenuOption(enter, "Device", [*self.outputs.values()])
        #Menu
        return midicube.menu.OptionMenu([device])

    def __delete_binding_menu(self):
        #Callback
        def enter ():
            if binding.curr_value() != None:
                self.reg().bindings.remove(binding.curr_value())
            return None
        #Options
        binding = midicube.menu.ValueMenuOption(enter, "Delete Bindings", self.reg().bindings)
        #Menu
        return midicube.menu.OptionMenu([binding])
    
    def __registration_menu(self):
        #Callbacks
        def select_reg():
            self.reg_mgr.select(registration.curr_value())
            return None
        def save_reg():
            self.reg_mgr.registrations.append(self.reg())
            return None
        #Options
        registration = midicube.menu.ValueMenuOption(select_reg, "Select Registration", self.reg_mgr.registrations)
        save = midicube.menu.SimpleMenuOption(save_reg, "Save Registration", "")
        #Menu
        return midicube.menu.OptionMenu([registration, save])
    