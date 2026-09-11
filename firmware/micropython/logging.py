"""
logging.py
Minimal drop-in shim for CPython's `logging` module, for boards/builds of
MicroPython that don't ship one. Supports just enough of the API used by
epd7in5bc.py: logging.getLogger(name) -> object with .debug/.info/.warning/
.error(msg, *args).

If your MicroPython build already provides a real `logging` module, this
file is not needed - just delete it and the real one will be used instead.
"""

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40

# Global level: raise to WARNING/ERROR to silence debug/info output.
_level = INFO


class Logger:
    def __init__(self, name):
        self.name = name

    def setLevel(self, level):
        global _level
        _level = level

    def _log(self, level, tag, msg, *args):
        if level >= _level:
            if args:
                msg = msg % args
            print("[{}] {}: {}".format(tag, self.name, msg))

    def debug(self, msg, *args):
        self._log(DEBUG, "DEBUG", msg, *args)

    def info(self, msg, *args):
        self._log(INFO, "INFO", msg, *args)

    def warning(self, msg, *args):
        self._log(WARNING, "WARN", msg, *args)

    def error(self, msg, *args):
        self._log(ERROR, "ERROR", msg, *args)


_loggers = {}


def getLogger(name):
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]


def basicConfig(level=INFO, **kwargs):
    global _level
    _level = level

### END OF FILE ###
