from abc import abstractmethod, ABC
import json

class Serializable(ABC):

    @abstractmethod
    def __to_dict__(self):
        return None
    
    @abstractmethod
    def __from_dict__(dict):
        return None

def serialize (obj):
    return json.dumps(obj.__to_dict__())

def deserialize (string: str, clazz):
    return clazz.__from_dict__(json.loads(string))

def list_to_dicts(ls):
    dicts = []
    for item in ls:
        dicts.append(item.__to_dict())
    return dicts

def list_from_dicts(dicts, clazz):
    ls = []
    for item in dicts:
        ls.append(clazz.__from_dict__(item))
    return ls