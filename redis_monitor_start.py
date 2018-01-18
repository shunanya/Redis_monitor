#!/usr/bin/env python

import sys, time, getopt

from common import logger
import monitor_constants as constants
from monitor import *
from redis_monitor import measure

logger.debug('RedisMonitor starting...')
optlist, args = getopt.gnu_getopt(sys.argv[1:], 'd:', ['duration=']) #duration of sending measured info [min]
for opt, value in optlist:
    if opt == "-d" or opt == "--duration":
        constants.DURATION = int(value)
        logger.info("Duration was redefined: "+str(constants.DURATION)+" min")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

custom = Monitor(constants.MONITOR_ID)
if not custom.prepareMonitor():
    logger.critical("Cannot obtain/create monitor:(")
    sys.exit(1)

logger.info("Starting loop...")
while 1 :
    time.sleep(int(constants.DURATION*60))
    data=measure()
    custom.send(data)        

logger.info('FINISHED')