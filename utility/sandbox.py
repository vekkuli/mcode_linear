import os, sys
sys.path.append(os.getcwd()) # isort:skip

import logging
from src.ethernetmcode import EthernetMCodeInterface

logging.basicConfig(level=logging.DEBUG)


stepper = EthernetMCodeInterface("192.168.10.77")

print(stepper.get_microstepping())

stepper.close()
