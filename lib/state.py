import os
from utilities import local_path
import json
import logging
from collections import namedtuple
from json import JSONEncoder

def stateDecoder(dict):
    return namedtuple('state', dict.keys())(*dict.values())

class state():
    DEFAULT_PATH = local_path("state.dat")
    def __init__(self):
        self.papers = []
        self.current_index = -1

    def save(self, path = DEFAULT_PATH):
        logging.debug("Saving state.")
        data = json.dumps(self.__dict__)
        
        file = open(path, "w")
        file.write(data)
        file.close()

    @staticmethod
    def load(path = DEFAULT_PATH):
        logging.info("Loading state from {}".format(path))
        if (os.path.exists(path) == False):
            return state()
        file = open(path, "r")
        data = file.read()
        return json.loads(data, object_hook=stateDecoder)
