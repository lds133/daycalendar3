import os
import random
import time
from pathlib import Path
from draw.page import Page
from wiki_grabber.database import DB,DBEntry
import shutil
from datetime import datetime,timedelta



def MakeTopBMPs(cfg):

    page = Page(cfg)

    db = DB(cfg)
    enhance = [    DBEntry.ENHANCE_NONE, DBEntry.ENHANCE_FOTO, DBEntry.ENHANCE_CLIPART, DBEntry.ENHANCE_BW, DBEntry.ENHANCE_BW2]

    for day in range(1,32):
        for mon in range(1,13):
            dd = db.GetAllDay(mon,day)
            if (dd==None):
                continue
            for d in dd:
                e = DBEntry.Load(db,d['id'],d['mon'],d['day'])
                if (e==None):
                    continue

                bmpcachefn = e.BmpCacheFilePath(e.enhance)

                if not os.path.isfile(bmpcachefn):
                    print("Creating bmp cache %s" % e.JsonFileName )
                    for em in enhance:
                        cachefn = e.BmpCacheFilePath(em)
                        if os.path.isfile(cachefn):
                            print(cachefn, " - skipped")
                            continue
                        img = page.make_picture(e,em)
                        if img==None:
                            print(cachefn, " - error")
                        else:
                            Path(cachefn).parent.mkdir(parents=True, exist_ok=True)
                            img.save(cachefn)
                            print(cachefn, " - saved")
                 
                    
         
def CopyTopBMPs(cfg):

    page = Page(cfg)
    db = DB(cfg)

    for day in range(1,32):
        for mon in range(1,13):
            dd = db.GetAllDay(mon,day)
            if (dd==None):
                continue
            for d in dd:
                e = DBEntry.Load(db,d['id'],d['mon'],d['day'])
                if (e==None):
                    continue

                bmpcachefn = e.BmpCacheFilePath(e.enhance)
                assert os.path.isfile(bmpcachefn), "Run MakeTopBMPs first"

                if (e.rank<cfg.MIN_RANK):
                    print(e.BmpFilePath(), " - rank too low. skipped")
                else:
                    Path(e.BmpFilePath()).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bmpcachefn,e.BmpFilePath())
                    print(e.BmpFilePath(), " - copied")



         
                    
def MakeBottomBMPs(cfg):

    db = DB(cfg)
    page = Page(cfg)

    t = datetime(datetime.now().year, 1, 1)
    startyear = t.year
    endyear = startyear + cfg.CALENDAR_YEARS_COUNT
    
    
    while (t.year<=endyear):
        
        dd = db.GetAllDay(t.month,t.day)
        assert dd!=None
         
        dayfn = os.path.join( cfg.DAYSDIR , str(t.year), "day_%04i-%02i-%02i%s" % (t.year,t.month,t.day,cfg.BMPEXT))
        if os.path.isfile(dayfn):
            print(dayfn," - skipped")
        else:    
            Path(dayfn).parent.mkdir(parents=True, exist_ok=True)
            
            img = page.make_day(t.year,t.month,t.day) 
            img.save(dayfn)
            print(dayfn, " - saved")  
        
        t += timedelta(days=1)    
        
        
        