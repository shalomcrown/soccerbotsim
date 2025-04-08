
import os
import os.path
import logging
import logging.handlers
import random
import sys
import os

localDir = os.path.dirname(__file__)
sys.path.append(localDir)
sys.path.append(os.path.join(localDir, "../../protobuf"))

GAME_TOPIC = "soccer/game"
GAME_STATE_TOPIC = "soccer/game/state"
GAME_EVENT_TOPIC = "soccer/game/event"
PARTICIPANTS_TOPIC = "soccer/participants/"
TEAM_SUB = "soccer/team/#"

last_names = []
male_names = []
female_names = []


# ===========================================================================

def setupLogging(teamName = "ref"):
    logdir = '/tmp/soccer/logs'

    logger = logging.getLogger('soccer')
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    
    handler = logging.handlers.RotatingFileHandler(os.path.join(logdir, f'soccer.{teamName}.log'),
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
    return logger

#=================================================================================

def loadNames():
    last_names.clear()
    male_names.clear()
    female_names.clear()
    with open(os.path.join(localDir, "last-names.txt"), "r") as fl:
        for line in fl:
            last_names.append(line)

    with open(os.path.join(localDir, "first-names.txt"), "r") as fl:
        for line in fl:
            items = line.split()
            male_names.append(items[1].strip())
            female_names.append(items[2].strip())

#=================================================================================

def getMaleName():
    if not last_names:
        loadNames()

    return f"{random.choice(male_names)} {random.choice(last_names)}"

def getFemaleName():
    if not last_names:
        loadNames()
    return f"{random.choice(female_names)} {random.choice(last_names)}"
