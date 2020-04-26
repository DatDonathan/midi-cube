import midicube
from abc import ABC, abstractmethod

class Menu:

    def __init__(self, options = []):
        self.options = options

class MenuOption(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def increase():
        pass

    @abstractmethod
    def decrease():
        pass

    @abstractmethod
    def get_title():
        return "Title"

    @abstractmethod
    def get_value():
        return "Value"

class MenuHistoryEntry:

    def __init__(menu: Menu, option_index: int):
        self.menu = menu
        self.option_index = option_index

class MenuController:

    def __init__(menu: Menu):
        self.menu = menu
        self.history = []
        self.option_index

    def scroll_left(self):
        self.option_index -= 1
        if self.option_index < 0:
            self.option_index = len(self.menu.options) - 1
        
    def scroll_right(self):
        self.option_index += 1
        if self.option_index >= len(self.menu.options):
            self.option_index = 0
            
    def curr_option(self):
        return self.menu.options[self.option_index]

    def increase(self):
        self.curr_option().increase()

    def decrease(self):
        self.curr_option().decrease()



    