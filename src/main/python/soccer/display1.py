
import numpy as np
import os
import os.path
import tarfile
import logging
import datetime
import time
import traceback
import datetime
import sys
import logging.handlers
import math
import threading

import paho.mqtt.client as mqtt

import soccer_pb2 as sc
import referee1
import utils
import random
import functools

import shapely
from shapely import Point, LineString
import pyglet

localDir = os.path.dirname(__file__)
sys.path.append(localDir)
sys.path.append(os.path.join(localDir, "../../protobuf"))

import soccer_pb2 as sc
import team1
import utils

logger = None

#=================================================================================

class Display(pyglet.window.Window):

    def __init__(self):
        super().__init__(1280, 960, "Soccer Federation viewer")
        self.pitchColor = 149, 250, 185
        self.border = 0,0,0
        self.batch = pyglet.graphics.Batch()

        from paho.mqtt.properties import Properties
        from paho.mqtt.packettypes import PacketTypes 
        properties=Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval=120*60 # in seconds

        threading.Thread(target=self.mqttThread).start()


    #=================================================================================

    def mqttThread(self):
        self.mqclient = mqtt.Client(client_id="display1",
                     transport="TCP",
                     protocol=mqtt.MQTTv5)
        
        self.mqclient.connect('localhost',
                clean_start = False,
                keepalive=0,
                properties=properties)


        logger.debug("Publish game setup")
        self.mqclient.publish(REFEREE_TOPIC, self.participant.SerializeToString(), retain=True)
        self.mqclient.publish(utils.GAME_TOPIC, self.gameSetup.SerializeToString(), retain=True)

        self.mqclient.subscribe(utils.TEAM_SUB)
        self.mqclient.message_callback_add(utils.TEAM_SUB, self.teamMessage)

        self.mqclient.subscribe(utils.PARTICIPANTS_TOPIC + "#")
        self.mqclient.message_callback_add(utils.PARTICIPANTS_TOPIC + "#", self.participantsMessage)

        self.mqclient.loop_start()        

    #=================================================================================
    

    def on_draw(self):
        clear()


    def start(self):
        pyglet.app.run()


    #=================================================================================

    def otherMessages(self, client, userdata, message):
        logger.debug(f"{self.teamName} Message {message} from {message.topic}")


#=================================================================================


def createDisplay():
    global logger
    logger = utils.setupLogging()
    display = Display()
    display.start()


#=================================================================================

if __name__ == '__main__':
    referee1.startup()