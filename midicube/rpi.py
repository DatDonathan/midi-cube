import midicube
import midicube.menu
import gpiozero
import RPLCD


class RaspberryPiMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
        self.left_pin = 2
        self.right_pin = 3
        self.enter_pin = 4
        self.return_pin = 14
        self.increase_pin = 15
        self.decrease_pin = 17
    
    def init():
        left_button = gpiozero.Button(self.left_pin)
        right_button = gpiozero.Button(self.right_pin)
        enter_button = gpiozero.Button(self.ente_button)
        return_button = gpiozero.Button(self.return_pin)
        increase_button = gpiozero.Button(self.increase_pin)
        decrease_button = gpiozero.Button(self.decrease_button)
        