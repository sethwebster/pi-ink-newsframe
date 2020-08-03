import os

def local_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
