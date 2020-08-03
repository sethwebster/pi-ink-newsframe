import os
from utilities import local_path
import json
import logging
from collections import namedtuple
from json import JSONEncoder
import time

def stateDecoder(dict):
    return namedtuple('state', dict.keys())(*dict.values())

def safeKey(key, default, dict):
    found_key = False
    for k in dict.keys():
        if (key == k):
            found_key = k
            break
    
    if (found_key):
        return dict[found_key]
    else:
        return default

class state():
    DEFAULT_PATH = local_path("state.dat")
    def __init__(self):
        self.state = {"papers":[], "current_index":-1, "next_render": time.time() }

    @property
    def current_index(self):
        return self.state["current_index"]

    @current_index.setter
    def current_index(self, value):
        self.state["current_index"] = value

    @property
    def papers(self):
        return self.state["papers"]

    @papers.setter
    def papers(self, value):
        self.state["papers"] = value

    @property
    def next_render(self):
        return safeKey('next_render', time.time(), self.state)

    @next_render.setter
    def next_render(self, value):
        self.state["next_render"] = value

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
        s = state()
        s.state = json.loads(data)["state"]
        return s
