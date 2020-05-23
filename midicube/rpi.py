import midicube
import midicube.menu
import gpiozero
import RPi.GPIO
import RPLCD


class RaspberryPiMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
        self.left_pin = 17
        self.enter_pin = 27
        self.right_pin = 22
        self.increase_pin = 18
        self.return_pin = 23
        self.decrease_pin = 24
    
    def init(self):
        self.lcd = RPLCD.CharLCD(numbering_mode = RPi.GPIO.BCM, cols=16, rows=2, pin_rs=26, pin_e=19, pins_data = [13, 6, 5, 11], auto_linebreaks=False)
        def update_display(func):
            func()
            self.lcd.clear()
            #self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string(self.controller.menu.get_title().center(16)[:16])
            self.lcd.crlf()
            #self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(self.controller.menu.get_value().center(16)[:16])
            if self.controller.menu.cursor != None:
                self.lcd.cursor_pos = (1, self.controller.menu.cursor)
                self.lcd.cursor_mode = RPLCD.CursorMode.blink
            else:
                self.lcd.cursor_mode = RPLCD.CursorMode.hide
        self.left_button = gpiozero.Button(self.left_pin)
        self.right_button = gpiozero.Button(self.right_pin)
        self.enter_button = gpiozero.Button(self.enter_pin)
        self.return_button = gpiozero.Button(self.return_pin)
        self.increase_button = gpiozero.Button(self.increase_pin)
        self.decrease_button = gpiozero.Button(self.decrease_pin)

        self.left_button.when_activated = lambda : update_display(lambda : self.controller.scroll_left())
        self.left_button.when_held = lambda : update_display(lambda : self.controller.scroll_left())
        self.right_button.when_activated = lambda : update_display(lambda : self.controller.scroll_right())
        self.right_button.when_held = lambda : update_display(lambda : self.controller.scroll_right())
        self.enter_button.when_activated = lambda : update_display(lambda : self.controller.enter())
        self.enter_button.when_held = lambda : update_display(lambda : self.controller.enter())
        self.return_button.when_activated = lambda : update_display(lambda : self.controller.menu_return())
        self.return_button.when_held = lambda : update_display(lambda : self.controller.menu_return())
        self.increase_button.when_activated = lambda : update_display(lambda : self.controller.increase())
        self.increase_button.when_held = lambda : update_display(lambda : self.controller.increase())
        self.decrease_button.when_activated = lambda : update_display(lambda : self.controller.decrease())
        self.decrease_button.when_held = lambda : update_display(lambda : self.controller.decrease())
