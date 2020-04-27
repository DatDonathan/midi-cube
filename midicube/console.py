import midicube
import midicube.menu

class ConsoleMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
    
    def loop(self):
        running = True
        while running:
            print(self.controller.curr_option().get_title())
            print(self.controller.curr_option().get_value())
            print("Enter l/r to scroll, +/- minus to change the value, e to enter, r to return and q to quit")
            i = input()
            if i == 'l':
                self.controller.scroll_left()
            elif i == 'r':
                self.controller.scroll_right()
            elif i == '+':
                self.controller.increase()
            elif i == '-':
                self.controller.decrease()
            elif i == 'e':
                self.controller.enter()
            elif i == 'r':
                self.controller.menu_return()
                