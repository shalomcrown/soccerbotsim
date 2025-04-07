
import os
import os.path
import logging
import logging.handlers


GAME_TOPIC = "soccer/game"
PARTICIPANTS_TOPIC = "soccer/participants/"
TEAM_SUB = "soccer/team/#"


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
