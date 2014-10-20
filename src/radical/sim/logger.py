from logging import Formatter, DEBUG, INFO, WARNING, CRITICAL, ERROR
from radical.utils.logger import logger

_logger = logger.getLogger(name='radical.sim')

mp_formatter = Formatter(fmt='[%(levelname)-8s] [%(now)4d] %(message)s')

for handler in _logger.handlers:
    handler.setFormatter(mp_formatter)

def simlog(level, message, env):

    if level == INFO:
        _logger.info(message, extra={'now': env.now})
    elif level == ERROR:
        _logger.error(message, extra={'now': env.now})
    elif level == WARNING:
        _logger.warning(message, extra={'now': env.now})
    elif level == CRITICAL:
        _logger.critical(message, extra={'now': env.now})
    elif level == DEBUG:
        _logger.debug(message, extra={'now': env.now})
    else:
        raise Exception("Unknown level!")
