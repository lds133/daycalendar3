from bs4 import BeautifulSoup
from .utils import ReadHTML
import json
import time
from .database import DB,DBEntry
import re 
import os

WIKI_TAG = 'uk'

def FixText(text):
    text = str(text).strip(" \r\n\t")
    text = text.replace("\n","")
    text = re.sub(r"[\{\[].*?[\}\]]", "", text)
    return text



def SavePage(db,year,mon):

    suffix = "%04i-%02i" % (year,mon)
    URL = "https://uk.wikipedia.org/wiki/Шаблон:Potd/"+suffix
    TXT = "potd_"+suffix+".html" 
    print("PAGE "+suffix)
    html = ReadHTML(db.cfg,URL,TXT)
    assert html!=None
    
    soup =  BeautifulSoup(html, 'html.parser')
    
    for block in soup.select("div[id='feat-pic']"):
    
        try:
            bb = block.find('div', {'class':'main-block-header'})
            title  = str(bb.text).strip(" \r\n\t")
            day = int(title.split(' ')[0])
            b = block.find('div', {'class':'main-block-content'})
            f = b.find('figure')
            a = f.find('a')
            i = a.find('img')
            pageurl = a['href']
            imageurl = i['src']
            descr = FixText(b.text)
        except:
            print(day,"ERROR!")
            continue

        
        print(day,descr)
        
        e = DBEntry.NewWiki(db,WIKI_TAG,year,mon,day,imageurl,pageurl,descr)
        
        if not os.path.exists(e.DirName):
            os.makedirs(e.DirName)

        e.Save(db.cfg.IS_OVERWRITE_JSON)
        
 

def CollectWikiPOTD(cfg):


    db = DB(cfg)
        
    #SavePage(db,2010,1)
    #exit()



    for y in range(cfg.FIRSTYEAR,cfg.LASTYEAR):
        for m in range(1,13):
            SavePage(db,y,m)
            time.sleep(cfg.POLITE_DELAY_SEC * 3)