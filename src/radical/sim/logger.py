from logging import Formatter
from radical.utils.logger import logger

simlog = logger.getLogger(name='radical.sim')

mp_formatter = Formatter(fmt='[%(levelname)-8s] %(message)s')

for handler in simlog.handlers:
    handler.setFormatter(mp_formatter)
