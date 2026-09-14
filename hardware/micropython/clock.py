# clock.py
# MicroPython (tested target: Raspberry Pi Pico 2 / RP2350, MicroPython 1.29.0)
# Wraps a DS3231 RTC (via the `urtc` library) into a simple Clock object with
# gettime / settime / waittill methods.
#
# NOTE on waittill(): the DS3231 alarm hardware does NOT compare year or month,
# only day-of-month, hour, minute and second. This mirrors the limitation
# already present in the original test_alarm.py (year/month were accepted but
# not actually usable by the chip). year/month are accepted here for interface
# symmetry with gettime()/settime(), but only day/hour/minute are used to
# arm the alarm. Practically this means: pick a target that is within the
# next ~28 days.

import time
import urtc
from machine import Pin, I2C, lightsleep


class Clock:
    def __init__(self, scl_pin=21, sda_pin=20, i2c_id=0, interrupt_pin=22):
        self.i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.rtc = urtc.DS3231(self.i2c)

        # SQW/INT pin from the DS3231, active-low, pulled up.
        self.sqw_pin = Pin(interrupt_pin, Pin.IN, Pin.PULL_UP)

        # Make sure nothing is left armed from a previous run.
        self.rtc.alarm(False, alarm=0)
        self.rtc.alarm(False, alarm=1)
        self.rtc.no_interrupt()

    def gettime(self):
        """Return current RTC time as (year, month, day, hours, mins)."""
        now = self.rtc.datetime()
        return (now.year, now.month, now.day, now.hour, now.minute)

    def settime(self, year, month, day, hours, mins):
        """Set the RTC to the given date/time (seconds forced to 0)."""
        dt = urtc.datetime_tuple(year, month, day, None, hours, mins, 0, 0)
        self.rtc.datetime(dt)
        
        
        
    def test_alarm(self, wait_seconds=5, timeout_s=8):
        """
        Self-test for the DS3231 alarm wiring/config: arms Alarm 1 to fire
        `wait_seconds` from now (using full year/month/day/hour/min/sec, so
        it's not subject to the day/hour/minute-only limitation noted
        above), then actively polls (no board sleep) for up to `timeout_s`
        seconds.
 
        Returns True if the alarm fired within the timeout, False
        otherwise (e.g. wiring problem, SQW/INT not connected, alarm
        register mis-set).
        """
        self.rtc.alarm(False, alarm=0)
        self.rtc.no_interrupt()
 
        # Compute now + wait_seconds via the epoch so minute/hour/day/month
        # rollovers are handled correctly (unlike naive field addition).
        now = self.rtc.datetime()
        now_epoch = time.mktime(
            (now.year, now.month, now.day, now.hour, now.minute, now.second, 0, 0)
        )
        ty, tmo, td, th, tmi, ts, _wd, _yd = time.localtime(now_epoch + wait_seconds)
 
        target = urtc.datetime_tuple(ty, tmo, td, None, th, tmi, ts, 0)
        self.rtc.alarm_time(target, alarm=0)
        self.rtc.interrupt(0)
 
        triggered = False
        start = time.ticks_ms()
        try:
            while time.ticks_diff(time.ticks_ms(), start) < timeout_s * 1000:
                if self.rtc.alarm(alarm=0):
                    triggered = True
                    break
                time.sleep_ms(100)
        finally:
            self.rtc.alarm(False, alarm=0)
            self.rtc.no_interrupt()
 
        return triggered
        
        

    def waittill_active(self, year, month, day, hours, mins, poll_ms=500):
        """
        Block until the RTC reaches the given date/time, WITHOUT putting the
        board to sleep (no lightsleep/deepsleep, no DS3231 alarm/IRQ used).

        This just re-reads the RTC in a loop and compares full
        (year, month, day, hour, minute) tuples directly, sleeping briefly
        between polls with time.sleep_ms() to avoid pegging the CPU at
        100%. Unlike the alarm-based waittill(), this correctly compares
        year and month too (the DS3231 alarm hardware can't), at the cost
        of keeping the board fully awake and drawing normal run-time power
        the whole time.
        """
        target = (year, month, day, hours, mins)
        while self.gettime() < target:
            time.sleep_ms(poll_ms)

    @staticmethod
    def _wake_only(pin):
        # IMPORTANT: never talk to the DS3231 over I2C from inside a GPIO
        # interrupt handler. Doing I2C transactions in a hard IRQ can lock
        # up the bus / hang the board. This handler's only job is to end
        # the WFI so lightsleep() returns; the real work happens below in
        # normal (non-interrupt) context.
        pass

    def waittill(self, year, month, day, hours, mins, poll_timeout_ms=2000):
        """
        Block (sleeping the board) until the RTC reaches the given time.
        Uses DS3231 Alarm 1 + the SQW interrupt pin to wake the board from
        machine.lightsleep(), then confirms/clears the alarm over I2C from
        normal context afterwards.

        year/month are accepted for API symmetry but are not usable by the
        DS3231 alarm hardware (see module note above); only day/hours/mins
        are actually armed.

        poll_timeout_ms bounds each lightsleep() call so the board also
        wakes up periodically on its own -- this guards against a missed
        falling edge (e.g. if the alarm flag/SQW was already active when
        armed, in which case no further falling edge would ever occur).
        """
        self.rtc.alarm(False, alarm=0)
        self.rtc.no_interrupt()

        target = urtc.datetime_tuple(year, month, day, None, hours, mins, 0, 0)
        self.rtc.alarm_time(target, alarm=0)
        self.rtc.interrupt(0)

        self.sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._wake_only)

        try:
            # Ground truth is always the I2C-read alarm flag, checked here
            # in normal context -- never inside the IRQ.
            while not self.rtc.alarm(alarm=0):
                lightsleep(poll_timeout_ms)
            self.rtc.alarm(False, alarm=0)  # clear the flag on the chip
        finally:
            self.sqw_pin.irq(handler=None)
            self.rtc.no_interrupt()