import logging

import config
import manager

############################################################
# Configuration
############################################################

cfg = config.init()

############################################################
# Initialization
############################################################

# Setup logging
logFormatter = logging.Formatter('%(asctime)s - %(name)-20s - %(message)s')
rootLogger = logging.getLogger()

if cfg['bot.debug_file']:
    fileHandler = logging.FileHandler('status.log')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

if cfg['bot.debug_console']:
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

logger = rootLogger.getChild("BOT")
logger.setLevel(logging.DEBUG)

############################################################
# MAIN ENTRY
############################################################
if __name__ == "__main__":
    manager.run()
