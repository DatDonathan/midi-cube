import midicube
import midicube.menu
import gpiozero
import RPi.GPIO
import RPLCD


class RaspberryPiMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
        self.left_pin = 22
        self.right_pin = 23
        self.enter_pin = 18
        self.return_pin = 17
        self.increase_pin = 16
        self.decrease_pin = 20
    
    def init(self):
        lcd = RPLCD.CharLCD(numbering_mode = RPi.GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data = [33, 31, 29, 23])
        def update_display(func):
            func()
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(self.controller.get_title().center(16, '0')[:16] + '\r\n')
            lcd.cursor_pos = (1, 0)
            lcd.write_string(elf.controller.get_value().center(16, '0')[:16]+ '\r\n')
        left_button = gpiozero.Button(self.left_pin)
        right_button = gpiozero.Button(self.right_pin)
        enter_button = gpiozero.Button(self.ente_button)
        return_button = gpiozero.Button(self.return_pin)
        increase_button = gpiozero.Button(self.increase_pin)
        decrease_button = gpiozero.Button(self.decrease_button)

        left_button.when_activated = lambda : update_display(lambda : self.controller.scroll_left())
        left_button.when_held = lambda : update_display(lambda : self.controller.scroll_left())
        right_button.when_activated = lambda : update_display(lambda : self.controller.scroll_right())
        right_button.when_held = lambda : update_display(lambda : self.controller.scroll_right())
        enter_button.when_activated = lambda : update_display(lambda : self.controller.enter())
        enter_button.when_held = lambda : update_display(lambda : self.controller.enter())
        return_button.when_activated = lambda : update_display(lambda : self.controller.menu_return())
        return_button.when_held = lambda : update_display(lambda : self.controller.menu_return())
        increase_button.when_activated = lambda : update_display(lambda : self.controller.increase())
        increase_button.when_held = lambda : update_display(lambda : self.controller.increase())
        decrease_button.when_activated = lambda : update_display(lambda : self.controller.decrease())
        decrease_button.when_held = lambda : update_display(lambda : self.controller.decrease())
        