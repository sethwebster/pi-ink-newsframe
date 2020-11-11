import logging
import time
import urllib
import os

class network():

    @property
    def is_network_connected(self):
        try:
            urllib.request.urlretrieve('https://google.com')
            return True
        except:
            return False

    @classmethod
    def wait_for_network(self):
        while (self.is_network_connected == False):
            logging.info("No network connection. Waiting 5 seconds.")
            time.sleep(5)

    @staticmethod
    def download_file(url, destination, force = False):
        path = os.path.dirname(destination)

        if (os.path.exists(path) == False):
            os.system("mkdir -p {}".format(path))
            
        if (os.path.exists(destination)):
            if (force):
                os.remove(destination)
            else:
                return destination

        exit_code = os.system("wget {}".format(url))
        
        if exit_code == 0:
            downloaded_file = os.path.basename(url)
            os.rename(downloaded_file, destination)
        else:
            raise IOError()

        return destination

