import midicube
import midicube.menu

class ConsoleMenuView:

    def __init__(self, controller: midicube.menu.MenuController):
        self.controller = controller
        self.textlen = 16
        self.hpadding = 1
        self.vpadding = 1
    
    def loop(self):
        running = True
        while running:
            #Title
            print()
            print("Midi Cube".center(self.textlen + self.hpadding * 2 + 4))
            print()
            #Top line
            print('+', ''.center(self.textlen + self.hpadding * 2 + 2, '-'), '+')
            #Vertical Padding
            for i in range(self.vpadding):
                print('|', ''.center(self.textlen + self.hpadding * 2 + 2), '|')
            #Title
            print('|', ''.center(self.hpadding), self.controller.menu.get_title().center(self.textlen), ''.center(self.hpadding), '|')
            #Vertical Padding
            for i in range(self.vpadding):
                print('|', ''.center(self.textlen + self.vpadding * 2 + 2), '|')
            #Value
            print('|', ''.center(self.hpadding), self.controller.menu.get_value().center(self.textlen), ''.center(self.hpadding), '|')
            #Vertical Padding
            for i in range(self.vpadding):
                print('|', ''.center(self.textlen + self.hpadding * 2 + 2), '|')
            #Bottom line
            print('+', ''.center(self.textlen + self.hpadding * 2 + 2, '-'), '+')
            #Input
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
            elif i == 'q':
                running = False
                