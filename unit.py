from log import logger

module_logger = logger.getChild('UNIT')

LB2KG = 0.453592
_unit = 'lb'


def set(unit):
    global _unit
    if unit not in ['lb', 'kg']:
        module_logger.error('Unit must be either "kg" or "lb"')
        exit(1)
    else:
        _unit = unit


def check(W):
    if _unit != 'lb':
        W = W * LB2KG

    return W


def get():
    return _unit