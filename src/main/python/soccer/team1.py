#!/usr/env/python3
####################################################
#
# Simple team implementation
#
####################################################

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

import paho.mqtt.client as mqtt

import soccer_pb2 as sc
import referee1
import utils

logger = None

class Team:
    def __init__(self, teamName):
        self.teamName = teamName

        from paho.mqtt.properties import Properties
        from paho.mqtt.packettypes import PacketTypes 
        properties=Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval=120*60 # in seconds

        self.mqclient = mqtt.Client(client_id=teamName,
                     transport="TCP",
                     protocol=mqtt.MQTTv5)
        
        self.mqclient.connect('localhost',
                clean_start = False,
                keepalive=0,
                properties=properties)

        self.mqclient.message_callback = self.otherMessages

        self.participant = sc.ParticipantConnection()
        self.participant.name = self.teamName
        self.participant.participantType = sc.ParticipantType.TEAM

        self.teamTopic = utils.PARTICIPANTS_TOPIC + f"{teamName}"

        logger.debug("Publish participant")
        self.mqclient.publish(utils.PARTICIPANTS_TOPIC, self.participant.SerializeToString(), retain=False)
        self.mqclient.subscribe(utils.GAME_TOPIC)

        self.mqclient.message_callback_add(utils.GAME_TOPIC, self.onGameMessage)

        self.mqclient.loop_start()

    #=================================================================================

    def onGameMessage(self, client, userdata, message):
        logger.debug(f"{self.teamName} Message {message} from {message.topic}")
        

    def otherMessages(self, client, userdata, message):
        logger.debug(f"{self.teamName} Message {message} from {message.topic}")

    #=================================================================================

    def startGame(self):
        logger.debug(f"Team start {self.teamName}")

        while True:
            time.sleep(0.2)

# ===========================================================================

def createTeam(teamName):
    global logger
    logger = utils.setupLogging()
    logger.debug(f"Starting team {teamName}")
    team = Team(teamName)
    team.startGame()


#=================================================================================

if __name__ == '__main__':
    referee1.setupLogging()
    logger = logging.getLogger('soccer')
    team = Team(sys.argv[1])