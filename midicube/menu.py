import midicube
from abc import ABC, abstractmethod

class Menu:

    def __init__(self, options = []):
        self.options = options

class MenuOption(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def enter(self):
        return None

    @abstractmethod
    def increase(self):
        pass

    @abstractmethod
    def decrease(self):
        pass

    @abstractmethod
    def get_title(self):
        return "Title"

    @abstractmethod
    def get_value(self):
        return "Value"

class SimpleMenuOption(MenuOption):

    def __init__(self, next_menu: Menu, title: str, value: str):
        self.next_menu = next_menu
        self.title = title
        self.value = value

    def enter(self):
        return self.next_menu
    
    def get_title(self):
        return self.title
    
    def get_value(self):
        return self.value

    def increase(self):
        pass

    def decrease(self):
        pass

class MenuHistoryEntry:

    def __init__(menu: Menu, option_index: int):
        self.menu = menu
        self.option_index = option_index

class MenuController:

    def __init__(self, menu: Menu):
        self.menu = menu
        self.history = []
        self.option_index = 0

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

    def enter(self):
        nextm = self.curr_option().enter()
        if (nextm == None):
            self.menu_return()
        else:
            self.history.push(MenuHistoryEntry(self.menu, self.option_index))
            self.menu = nextm
            self.option_index = 0

    def menu_return(self):
        if len(self.history) > 0:
            entry = self.history.pop()
            self.option_index = entry.option_index
            self.menu = entry.menu
