from abc import abstractmethod, ABC
import json
import sys

class Serializable(ABC):

    @abstractmethod
    def __to_dict__(self):
        return None
    
    @abstractmethod
    def __from_dict__(dict):
        return None

class DynamicSerializableContainer(Serializable):

    def __init__(self, serializable: Serializable):
        self.serializable = serializable

    def __to_dict__(self):
        dict = {}
        dict['type'] = type(self.serializable).__name__
        dict['module'] = type(self.serializable).__module__
        dict['data'] = self.serializable.__to_dict__()
        return dict

    def __from_dict__(dict):
        className = dict['type']
        moduleName = dict['module']
        clazz = getattr(sys.modules[moduleName], className)
        serializable = clazz.__from_dict__(dict['data'])
        return DynamicSerializableContainer(serializable)

def serialize (obj):
    return json.dumps(obj.__to_dict__())

def deserialize (string: str, clazz):
    return clazz.__from_dict__(json.loads(string))

def list_to_dicts(ls):
    dicts = []
    for item in ls:
        dicts.append(item.__to_dict__())
    return dicts

def list_from_dicts(dicts, clazz):
    ls = []
    for item in dicts:
        ls.append(clazz.__from_dict__(item))
    return ls

def dict_to_serialized_dict(dict):
    serialized = {}
    for key, value in dict.items():
        serialized[key] = value.__to_dict__()
    return serialized

def dict_from_serialized_dict(serialized, clazz):
    dict = {}
    for key, value in serialized.items():
        dict[key] = clazz.__from_dict__(value)
    return dict
