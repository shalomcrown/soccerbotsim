#!/usr/env/python3

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
from multiprocessing import Process

# sudo apt install protobuf-compiler python3-protobuf python3-paho-mqtt mosquitto-clients mosquitto
# 

localDir = os.path.dirname(__file__)
sys.path.append(localDir)
sys.path.append(os.path.join(localDir, "../../protobuf"))

import soccer_pb2 as sc
import team1
import utils

logger = None

REFEREE_NAME = "Referee1"
REFEREE_TOPIC = utils.PARTICIPANTS_TOPIC + REFEREE_NAME

# ===========================================================

class Referee:
    def __init__(self):
        self.gameState = sc.GameState()
        self.started = False
        self.gameState.gameState = sc.GameStateType.WAITING_FOR_TEAMS
        self.teamNames = []
        self.teamSetups = {}

        self.pitchLength = 105
        self.pitchWidth = 68

        self.gameSetup = sc.GameSetup()
        self.gameSetup.pitchCorners.extend([
            sc.Vec3(x=0, y=0),
            sc.Vec3(x=self.pitchLength, y=0),
            sc.Vec3(x=self.pitchLength, y=self.pitchWidth),
            sc.Vec3(x=0, y=self.pitchWidth),
            ])
        
        self.gameSetup.playersPerTeam = 1
        self.gameSetup.teamPlayersTotalMass = 1
        self.gameSetup.teamPlayersTotalArea = 1
        self.gameSetup.teamPlayersTotalPotentialEnergy = 1000;
        self.gameSetup.coefficientOfFrictionPlayer = 0.3;
        self.gameSetup.gameDurationSeconds = 90 * 60;

        self.participant = sc.ParticipantConnection()
        self.participant.name = "Referee1"
        self.participant.participantType = sc.ParticipantType.REFEREE


        from paho.mqtt.properties import Properties
        from paho.mqtt.packettypes import PacketTypes 
        properties=Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval=120*60 # in seconds

        self.mqclient = mqtt.Client(client_id="Referee",
                     transport="TCP",
                     protocol=mqtt.MQTTv5)
        
        self.mqclient.connect('localhost',
                     clean_start = True,
                     keepalive=0,
                     properties=properties)

        self.mqclient.message_callback = self.otherMessages

        logger.debug("Publish game setup")
        self.mqclient.publish(REFEREE_TOPIC, self.participant.SerializeToString(), retain=True)
        self.mqclient.publish(utils.GAME_TOPIC, self.gameSetup.SerializeToString(), retain=True)

        self.mqclient.subscribe(utils.TEAM_SUB)
        self.mqclient.message_callback_add(utils.TEAM_SUB, self.teamMessage)

        self.mqclient.subscribe(utils.PARTICIPANTS_TOPIC + "#")
        self.mqclient.message_callback_add(utils.PARTICIPANTS_TOPIC + "#", self.participantsMessage)

        self.mqclient.loop_start()

        #=================================================================================

    def participantsMessage(self, client, userdata, message):
        if not self.started:
            logger.debug(f"Ignore Message {message} from {message.topic}")
            return
        
        msg = sc.ParticipantConnection()
        msg.ParseFromString(message.payload)
        logger.debug(f"Message {msg} from {message.topic}")

        if msg.participantType == sc.ParticipantType.TEAM:
            if len(self.teamNames) == 2:
                logger.debug(f"Already have two teams - ignore {msg.name}")
                return

            self.teamNames.append(msg.name)
            logger.debug(f"Got a team {msg.name}")

            if len(self.teamNames) == 2:
                logger.debug("Got two teams - can update dispositions")
                for i, teamName in enumerate(self.teamNames):
                    teamDisposition = sc.TeamDisposition()
                    teamDisposition.teamName = teamName
                    teamDisposition.pitchHalf.extend((
                        sc.Vec3(x = i * self.pitchLength / len(self.teamNames), y = 0),
                        sc.Vec3(x = (i + 1) * self.pitchLength / len(self.teamNames), y = 0),
                        sc.Vec3(x = (i + 1) * self.pitchLength / len(self.teamNames), y = self.pitchWidth),
                        sc.Vec3(x = i * self.pitchLength / len(self.teamNames), y = self.pitchWidth),
                        ))
                    
                    teamDisposition.ownGoal.height = 2.44
                    teamDisposition.ownGoal.post1.x = i * self.pitchLength
                    teamDisposition.ownGoal.post1.y = self.pitchWidth / 2 - 3.66
                    teamDisposition.ownGoal.post2.x = i * self.pitchLength
                    teamDisposition.ownGoal.post2.y = self.pitchWidth / 2 + 3.66

                    teamDisposition.kickingOff = True if i == 0 else False
                    self.gameSetup.teamsDispositions.append(teamDisposition)
                
                self.gameSetup.teamsDispositions[0].opponentGoal.CopyFrom(self.gameSetup.teamsDispositions[1].ownGoal)
                self.gameSetup.teamsDispositions[1].opponentGoal.CopyFrom(self.gameSetup.teamsDispositions[0].ownGoal)
                self.mqclient.publish(utils.GAME_TOPIC, self.gameSetup.SerializeToString(), retain=True)


    #=================================================================================

    def teamMessage(self, client, userdata, message):
        if not self.started:
            logger.debug(f"Ignore Message {message} from {message.topic}")
            return
        logger.debug(f"Message {message} from {message.topic}")

        teamName = os.path.basename(message.topic)

        if not teamName in self.teamNames:
            logger.debug(f"Message not from known teram - ignore")
            return
        
        msg = sc.TeamRequest()
        msg.ParseFromString(message.payload)

        if msg.HasField("teamSetup"):
            if self.gameState.gameState == sc.GameStateType.WAITING_FOR_TEAMS:
                self.teamSetups[teamName] = msg.teamSetup

                if len(self.teamSetups) == 2:
                    logger.debug("Have all setups, publish state")
                    for teamName, teamSetup in self.teamSetups.items():
                        teamState = sc.TeamState()
                        teamState.teamName = teamName
                        
                        for player in msg.teamSetup.players:
                            if player.active:
                                playerState = sc.PlayerState()
                                playerState.jerseyNumber = player.jerseyNumber
                                playerState.teamName = teamName
                                playerState.position.CopyFrom(player.startPosition)
                                teamState.playerStates.append(playerState)

                        self.gameState.teamStates.append(teamState)

                    self.gameState.gameState = sc.GameStateType.WAITING_KICKOFF
                    self.mqclient.publish(utils.GAME_STATE_TOPIC, self.gameState.SerializeToString())

        
    #=================================================================================
    
    def otherMessages(self, client, userdata, message):
        if not self.started:
            logger.debug(f"Ignore Message {message} from {message.topic}")
            return
        logger.debug(f"Message {message} from {message.topic}")

    # ===========================================================================

    def runGame(self):
        time.sleep(0.2)
        self.started = True
        while self.gameState != sc.GameStateType.FINISHED:
            time.sleep(0.2)



# ===========================================================================

def startup():
    global logger
    logger = utils.setupLogging();
    ref = Referee()

    teamBlue = Process(target=team1.createTeam, args=("Blue",))
    teamBlue.start()

    teamRed = Process(target=team1.createTeam, args=("Red",))
    teamRed.start()

    ref.runGame()    

if __name__ == '__main__':
    startup()

