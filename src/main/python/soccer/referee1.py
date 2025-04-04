#!/usr/env/python3

import numpy as np
import os
import os.path
import tarfile
import logging
import datetime
import time
import traceback
import threading
import datetime
import sys
import logging.handlers
import threading

# sudo apt install protobuf-compiler python3-protobuf
# sudo apt install  python3-paho-mqtt mosquitto-clients mosquitto

localDir = os.path.dirname(__file__)
sys.path.append(localDir)
sys.path.append(os.path.join(localDir, "../../protobuf"))

import soccer_pb2 as sc
import paho.mqtt.client as mqtt


# ===========================================================

class Referee:
    def __init__(self):
        self.gameState = sc.GameState()
        self.gameState.gameState = sc.GameStateType.NOT_STARTED
        
        self.mqclient = mqtt.Client(client_id="Refereee",
                     transport="TCP",
                     protocol=mqtt.MQTTv5)
        
        

# ===========================================================================

def setupLogging():

    logdir = '/tmp/soccer/logs'
    logger = logging.getLogger('soccer')
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    
    handler = logging.handlers.RotatingFileHandler(os.path.join(logdir, 'klvplayerQt5.log'),
                                                backupCount=30, maxBytes=1024 * 1024 * 10)
    
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s  %(filename)s(%(lineno)d)  %(funcName)s %(message)s')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    outhandler = logging.StreamHandler()
    outhandler.setLevel(logging.DEBUG)
    outhandler.setFormatter(formatter)
    logger.addHandler(outhandler)
    logger.debug("Starting up")



# ===========================================================================


if __name__ == '__main__':
    setupLogging();

