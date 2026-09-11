import os
import random
import time
from draw.page import Page
from wiki_grabber.database import DB,DBEntry



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
                for em in enhance:
                    page.draw_image(e,em)
                    exit(0) # <-----
