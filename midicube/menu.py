import midicube
from abc import ABC, abstractmethod

class Menu(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_title(self):
        return "Title"

    @abstractmethod
    def get_value(self):
        return "Value"

    @abstractmethod
    def increase(self):
        pass

    @abstractmethod
    def decrease(self):
        pass

    @abstractmethod
    def scroll_left(self):
        pass

    @abstractmethod
    def scroll_right(self):
        pass

    @abstractmethod
    def enter(self):
        return None
    
    @property
    def cursor():
        return None


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

    def __init__(self, next_menu: callable, title: str, value: str):
        super().__init__()
        self.next_menu = next_menu
        self.title = title
        self.value = value

    def enter(self):
        return self.next_menu()
    
    def get_title(self):
        return self.title
    
    def get_value(self):
        return self.value

    def increase(self):
        pass

    def decrease(self):
        pass

class ValueMenuOption(MenuOption):

    def __init__(self, next_menu: callable, title: str, values):
        super().__init__()
        self.next_menu = next_menu
        self.title = title
        self.values = values
        self.value_index = 0

    def enter(self):
        return self.next_menu()
    
    def get_title(self):
        return self.title
    
    def get_value(self):
        return str(self.curr_value())

    def increase(self):
        self.value_index += 1
        if self.value_index >= len(self.values):
            self.value_index = 0

    def decrease(self):
        self.value_index -= 1
        if self.value_index < 0:
            self.value_index = len(self.values) - 1

    def curr_value(self):
        if self.value_index >= len(self.values):
            return None
        return self.values[self.value_index]

class OptionMenu (Menu):

    def __init__(self, options=[]):
        super().__init__()
        self.options = options
        self.option_index = 0
        pass

    def curr_option(self):
        return self.options[self.option_index]

    def get_title(self):
        return self.curr_option().get_title()

    def get_value(self):
        return self.curr_option().get_value()

    def increase(self):
        self.curr_option().increase()

    def decrease(self):
        self.curr_option().decrease()

    def scroll_left(self):
        self.option_index -= 1
        if self.option_index < 0:
            self.option_index = len(self.options) - 1

    def scroll_right(self):
        self.option_index += 1
        if self.option_index >= len(self.options):
            self.option_index = 0

    def enter(self):
        return self.curr_option().enter()

def chars(start, end):
    chars = []
    for i in range(ord(start), ord(end)):
        chars.append(chr(i))
    return chars

class InputMenu (Menu):

    def __init__(self, action: callable, title: str, value: str=""):
        super().__init__()
        self.action = action
        self.title = title
        self.value = value.ljust(16)
        self._cursor = 0
        self.characters = [' ', *chars('a', 'z'), *chars('A', 'Z'), *chars('0', '9'), '.', ',', ':', ';', '-']

    def get_title(self):
        return self.title

    def get_value(self):
        return self.value.strip()

    def increase(self):
        index = 0
        try:
            index = self.characters.index(self.value[self._cursor]) + 1
        except ValueError:
            pass
        index %= len(self.characters)
        value = list(self.value)
        value[self._cursor] = self.characters[index]
        self.value = "".join(value)

    def decrease(self):
        index = 0
        try:
            index = self.characters.index(self.value[self._cursor]) - 1
        except ValueError:
            pass
        index %= len(self.characters)
        value = list(self.value)
        value[self._cursor] = self.characters[index]
        self.value = "".join(value)

    def scroll_left(self):
        self._cursor = (self._cursor - 1) % len(self.value)

    def scroll_right(self):
        self._cursor = (self._cursor + 1) % len(self.value)

    def enter(self):
        return self.action(self.get_value())
    
    @property
    def cursor(self):
        return self._cursor

class MenuHistoryEntry:

    def __init__(self, menu: Menu):
        self.menu = menu

class MenuController:

    def __init__(self, menu: Menu):
        self.menu = menu
        self.history = []

    def scroll_left(self):
        self.menu.scroll_left()
        
    def scroll_right(self):
        self.menu.scroll_right()

    def decrease(self):
        self.menu.decrease()
    
    def increase(self):
        self.menu.increase()

    def enter(self):
        nextm = self.menu.enter()
        if (nextm == None):
            self.menu_return()
        else:
            self.history.append(MenuHistoryEntry(self.menu))
            self.menu = nextm
            self.option_index = 0

    def menu_return(self):
        if len(self.history) > 0:
            entry = self.history.pop()
            self.menu = entry.menu
