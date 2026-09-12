from einksdcard import EinkSDCard
from clock import Clock
import random

eink = EinkSDCard()
clk = Clock()

while(1):
    
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
    
    break

    
