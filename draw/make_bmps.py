import os
import random
import time
from pathlib import Path
from draw.page import Page
from wiki_grabber.database import DB,DBEntry
import shutil



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
                        img = page.make_image(e,em)
                        Path(cachefn).parent.mkdir(parents=True, exist_ok=True)
                        img.save(cachefn)
                        print(cachefn, " - saved")
                 

                if (e.rank<cfg.MIN_RANK):
                    print(e.BmpFilePath(), " - rank too low. skipped")
                else:
                    Path(e.BmpFilePath()).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bmpcachefn,e.BmpFilePath())
                    print(e.BmpFilePath(), " - created")
                    exit(0)
                    
                    
