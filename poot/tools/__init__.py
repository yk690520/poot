import logging as _logger
import platform
_logger.basicConfig(level=_logger.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
def get_logger():
    return _logger

def get_system():
    return platform.system()
