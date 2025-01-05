import logging
from logging.handlers import RotatingFileHandler


path = 'log/'
fileName = 'basic.log'

# Log a message at the start of the program
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Max size of 10 MB
handler = RotatingFileHandler(f'{path}{fileName}', maxBytes=10*1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

logger.warning(f"Logging started with filename: {fileName}, level: {logger.level}")

