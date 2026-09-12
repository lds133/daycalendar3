from einksdcard import EinkSDCard
from clock import Clock
import random
import time
from machine import Pin

def nextwaketime(year, month, day, hour, mins):
    if hour < 12:
        seconds_left = (12 - hour) * 3600 - mins * 60
    elif hour < 18:
        seconds_left = (18 - hour) * 3600 - mins * 60
    else:
        seconds_left = (24 - hour) * 3600 - mins * 60
    timestamp = time.mktime((year, month, day, hour, mins, 0, 0, 0))
    timestamp += seconds_left
    nyear, nmonth, nday, nhour, nmins, _, _, _ = time.localtime(timestamp)
    return (nyear, nmonth, nday, nhour, nmins)
    




eink = EinkSDCard()
clk = Clock()
led = Pin(25, Pin.OUT)

while(1):
    
    led.on()
    eink.init(False)
    try:
        year, month, day, hour, mins = clk.gettime()
        dayfilename = "/sd/days/%04i/day_%04i-%02i-%02i.bmp" % (year,year,month,day)
        imgdir = "/sd/bmp/%02i-%02i" % (month,day)
        print(imgdir)
        files = eink.getfiles(imgdir)
        print(files)
        imgfile = random.choice(files)
        
        eink.drawbmp(imgdir+"/"+imgfile,214,0)
        eink.drawbmp(dayfilename,0,0)
    finally:    
        eink.finit()
        led.off()

        
    (year, month, day, hour, mins) = nextwaketime(year, month, day, hour, mins)
    print("Waiting till %04i-%02i-%02i %02i:%02i" % (year, month, day, hour, mins))
    clk.waittill_active(year, month, day, hour, mins)

    

