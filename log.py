import logging
'''
Usage:
from logging import logger

logger.info('Info data')

child = logger.getChild('ChildLog')
child.warning('Child warning')
'''


log_name = 'talpa'
fh_level = logging.DEBUG
ch_level = logging.INFO

logger = logging.getLogger(log_name)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_name+'.log', mode='w')
fh.setLevel(fh_level)
ch = logging.StreamHandler()
ch.setLevel(ch_level)
formatter_fh = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s',
                                 datefmt='%d/%m/%Y %I:%M:%S %p')
formatter_ch = logging.Formatter('%(message)s')
fh.setFormatter(formatter_fh)
ch.setFormatter(formatter_ch)
logger.addHandler(fh)
logger.addHandler(ch)
