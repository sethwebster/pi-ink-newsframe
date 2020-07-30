import logging
import time

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