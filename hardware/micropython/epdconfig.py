"""
epdconfig.py
MicroPython port for Raspberry Pi Pico / Pico 2.

Hardware abstraction layer for Waveshare e-Paper displays.
Replaces the Linux/CPython version (spidev + gpiozero) with
machine.Pin / machine.SPI calls.

Wiring (SPI1 peripheral):
    e-Paper   ->  Pico 2 GPIO
    VCC       ->  3V3
    GND       ->  GND
    DIN(MOSI) ->  GP11
    CLK(SCK)  ->  GP10
    CS        ->  GP13
    DC        ->  GP14
    RST       ->  GP15
    BUSY      ->  GP9
    PWR       ->  GP3   (controls the panel's power switch, if present)
"""

import time
from machine import Pin, SPI


class Logger:
    """Minimal drop-in replacement for the CPython `logging` module,
    which is not available in standard MicroPython builds."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40

    # change to Logger.DEBUG for verbose driver output
    level = INFO

    def __init__(self, name):
        self.name = name

    def _log(self, level, tag, msg, *args):
        if level >= Logger.level:
            if args:
                msg = msg % args
            print("[{}] {}: {}".format(tag, self.name, msg))

    def debug(self, msg, *args):
        self._log(Logger.DEBUG, "DEBUG", msg, *args)

    def info(self, msg, *args):
        self._log(Logger.INFO, "INFO", msg, *args)

    def warning(self, msg, *args):
        self._log(Logger.WARNING, "WARN", msg, *args)

    def error(self, msg, *args):
        self._log(Logger.ERROR, "ERROR", msg, *args)


logger = Logger(__name__)


class RaspberryPiPico:
    # ---- Pin definition (BCM-style GPIO numbers on the Pico) --------
    RST_PIN  = 15
    DC_PIN   = 14
    CS_PIN   = 13
    BUSY_PIN = 9
    PWR_PIN  = 3
    MOSI_PIN = 11
    SCLK_PIN = 10
    MISO_PIN = 12   # required by machine.SPI even though unused

    SPI_ID   = 1
    SPI_BAUD = 4_000_000

    def __init__(self):
        self.spi = None
        self.GPIO_RST_PIN  = Pin(self.RST_PIN, Pin.OUT)
        self.GPIO_DC_PIN   = Pin(self.DC_PIN, Pin.OUT)
        self.GPIO_CS_PIN   = Pin(self.CS_PIN, Pin.OUT)
        self.GPIO_PWR_PIN  = Pin(self.PWR_PIN, Pin.OUT)
        self.GPIO_BUSY_PIN = Pin(self.BUSY_PIN, Pin.IN, Pin.PULL_DOWN)

    # ---- GPIO ----------------------------------------------------------
    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            self.GPIO_RST_PIN.value(value)
        elif pin == self.DC_PIN:
            self.GPIO_DC_PIN.value(value)
        elif pin == self.CS_PIN:
            self.GPIO_CS_PIN.value(value)
        elif pin == self.PWR_PIN:
            self.GPIO_PWR_PIN.value(value)

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value()
        elif pin == self.RST_PIN:
            return self.GPIO_RST_PIN.value()
        elif pin == self.DC_PIN:
            return self.GPIO_DC_PIN.value()
        elif pin == self.CS_PIN:
            return self.GPIO_CS_PIN.value()
        elif pin == self.PWR_PIN:
            return self.GPIO_PWR_PIN.value()

    def delay_ms(self, delaytime):
        time.sleep_ms(delaytime)

    # ---- SPI -------------------------------------------------------
    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def spi_writebyte2(self, data):
        self.spi.write(bytearray(data))

    # ---- lifecycle ---------------------------------------------------
    def module_init(self, cleanup=False):
        # cleanup kept only for API compatibility with the original
        # epd7in5bc.py, which always calls module_init() with no args.
        self.GPIO_PWR_PIN.value(1)

        self.spi = SPI(
            self.SPI_ID,
            baudrate=self.SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.SCLK_PIN),
            mosi=Pin(self.MOSI_PIN),
            miso=Pin(self.MISO_PIN),
        )
        self.GPIO_CS_PIN.value(1)
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        if self.spi is not None:
            self.spi.deinit()

        self.GPIO_RST_PIN.value(0)
        self.GPIO_DC_PIN.value(0)
        self.GPIO_PWR_PIN.value(0)
        logger.debug("close 5V, Module enters 0 power consumption ...")


implementation = RaspberryPiPico()

# Re-export instance methods/attrs at module level, so callers can do
# `import epdconfig; epdconfig.digital_write(...)` exactly like before.
for _name in dir(implementation):
    if not _name.startswith('_'):
        globals()[_name] = getattr(implementation, _name)

### END OF FILE ###