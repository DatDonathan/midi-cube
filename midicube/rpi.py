import midicube
import midicube.menu
import gpiozero
import RPLCD


class RaspberryPiMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
        self.left_pin = 2
        self.right_button = 3
        self.enter_button = 4
        self.shif_button = 14
    
    def init():
        pass