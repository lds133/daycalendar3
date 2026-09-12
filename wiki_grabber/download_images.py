import os
import time
from .database import DB,DBEntry
import requests



def download_file(cfg,url,local_filename):
    if os.path.isfile(local_filename):
        return ("Skip", False)
    try:
        with requests.get(url, stream=True,headers=cfg.READ_IMAGE_HEADERS) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
    except Exception as e:
        if os.path.isfile(local_filename):
            os.remove(local_filename)
        return ("Error",True)
            
    return ("Ok",True)



def DownloadWikiImages(cfg):

    db = DB(cfg)

    for day in range(1,32):
        for mon in range(1,13):
            dd = db.GetAllDay(mon,day)
            if (dd==None):
                continue
            for d in dd:
                e = DBEntry.Load(db,d['id'],d['mon'],d['day'])
                print(e.ImageFilePath,end='')
                (msg,isdelay) = download_file(cfg,e.imgurlfixed,e.ImageFilePath)
                if (isdelay):
                    time.sleep(cfg.POLITE_DELAY_SEC)
                print(' ',msg)
            

