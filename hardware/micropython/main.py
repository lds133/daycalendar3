from einksdcard import EinkSDCard,RED,BLACK
from clock import Clock
import random
import time
from machine import Pin
import gc


def nextwaketime(year, month, day, hour, mins):
    if hour < 12:
        seconds_left = (12 - hour) * 3600 - mins * 60
    elif hour < 18:
        seconds_left = (18 - hour) * 3600 - mins * 60
    else:
        seconds_left = (24 - hour) * 3600 - mins * 60
    timestamp = time.mktime((year, month, day, hour, mins, 0, 0, 0))
    #timestamp += seconds_left
    timestamp += 180
    
    nyear, nmonth, nday, nhour, nmins, _, _, _ = time.localtime(timestamp)
    return (nyear, nmonth, nday, nhour, nmins)
    



def runclockupdate(eink,clk,files,posttext):
    
    CFN = 'clock.txt'
  
    if not (CFN in files):
        posttext.append(      "Clock set ..... SKIP")
        print(CFN + " not found. Clock update skipped.")
        return
    
    
    print(CFN + " detected")
    text = eink.getfiletext("/sd/"+CFN,textlimit=30)
    print(CFN +" text:"+text)
    
    year, month, day, hour, mins = map(int, text.replace("-", " ").replace(":", " ").split())
    print("Closk set: %04i-%02i-%02i %02i:%02i" % (year, month, day, hour, mins ))

    clk.settime( year, month, day, hour, mins)
    year, month, day, hour, mins = clk.gettime()
    
    print("Clock get: %04i-%02i-%02i %02i:%02i" % (year, month, day, hour, mins ))

    eink.deletefile("/sd/"+CFN)
    files = eink.getfiles("/sd")
    if (CFN in files):
        raise RuntimeError("Unable to delete "+CFN+" file")
    print(CFN+ " deleted")    
    posttext.append(      "Clock set ..... DONE")
    
    
    
    
    



def runpost(eink,clk,led):
        
    print("P.O.S.T.")
    posttext = []
    post = True
    led.on()
    try:
        eink.init(False)
    except Exception as e:
        print("EINK Exception:", e)
        post = False


    if (post):
        posttext.append(      "EInk test ..... PASS")
        try:

            files = eink.getfiles("/sd")
            print("SD card files: ",files)
            rc = ('days' in files) and ('bmp' in files)
            if (rc):
                posttext.append(       "SDCard test ... PASS")
            else:
                posttext.append(       "SDCard test ... FAIL")
                post = False
            
            if ('readme.bmp' in files):
               eink.drawbmp("/sd/readme.bmp",214,0)
            else:
               eink.print("readme.bmp file not found", 400, 96, color=RED, scale=1)

            runclockupdate(eink,clk,files,posttext)

            year, month, day, hour, mins = clk.gettime()
            posttext.insert(0,"")
            posttext.insert(0,"  %04i-%02i-%02i %02i:%02i" % (year, month, day, hour, mins))
            
            if (year>=2026):
                posttext.append(   "Clock test .... PASS")
            else:
                posttext.append(   "Clock test .... FAIL")
                post = False
            
            rc = clk.test_alarm()
            if (rc):
                posttext.append(   "Alarm test .... PASS")
            else:
                posttext.append(   "Alarm test .... FAIL")
                post = False
            
          
            posttext.append("")
            if post:
                posttext.append(        "P.O.S.T. ...... PASS")
                posttext.append("")
                posttext.append(        "    Wait 30 sec")
            else:   
                posttext.append(        "P.O.S.T. ...... FAIL")
                posttext.append("")
                posttext.append(        "      Stopped")    
            
            x = 195
            for s in posttext:
                print(s)
                eink.print(s, x, 32, color=BLACK, scale=2)
                x-=18
                
        except Exception as e:
            print("POST Exception:",e)
            eink.print(str(e), 300, 0, color=RED, scale=1)
            post = False
            
        finally:
            eink.finit()
            led.off()
            
    if post:
        print("Waiting 30 sec...")
        time.sleep(30)
    else:
        print("POST failed. Stopped.")
        while(1):
            led.toggle()
            time.sleep(0.2)            
            
            
            
            
            
        


eink = EinkSDCard()
clk = Clock()
led = Pin(25, Pin.OUT)


#check for clock.txt file


runpost(eink,clk,led)


year, month, day, hour, mins = clk.gettime()            
random.seed(mins | (hour << 6) | (day << 11) | (month << 16) | (year << 20))


while(1):

    led.on()
    print("\n")
    gc.collect()
    print("Free mem:",gc.mem_free())
    eink.init(False)
    isexception = False
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
        
    except Exception as e:
        print("Exception:",e)
        eink.print("EXCEPTION", 400, 0, color=RED, scale=2)
        eink.print(str(e), 300, 0, color=RED, scale=1)
        
    finally:    
        eink.finit()
        led.off()

    if (isexception):
        print("Exception. Stopped.")
        while(1):
            led.toggle()
            time.sleep(0.2)

    
    (year, month, day, hour, mins) = nextwaketime(year, month, day, hour, mins)
    print("Waiting till %04i-%02i-%02i %02i:%02i" % (year, month, day, hour, mins))
    clk.waittill_active(year, month, day, hour, mins)

    

