import os
import urllib.parse
import json
import re




class DBEntry():

    
    
    RANK_NONE = 0
    RANK_OFF = 1
    RANK_BAD = 2
    RANK_OK = 3
    RANK_GOOD = 4
    RANK_BEST = 5
    
    ENHANCE_NONE = 0
    ENHANCE_FOTO = 1
    ENHANCE_CLIPART = 2
    ENHANCE_BW = 3
    ENHANCE_BW2 = 4
    
    JSONEXT = ".json"
    

    def __init__(self,db):
        self.db = db
        self.day = 0
        self.mon = 0
        self.imgurl = ''
        self.wikiurl = ''
        self.text = ''
        self.rank = DBEntry.RANK_NONE
        self.enhance = 0
        self.tag = None
        self.id = None
        self.note = None


    def Update(self):
        ee = DBEntry.Load(self.db,self.id,self.mon,self.day)
        ee.enhance = self.enhance
        ee.rank = self.rank
        print("Update",self.id,self.mon,self.day,"->",self.enhance, self.rank)                
        ee.Save(True)


    @property
    def DirName(self):  
        dn =  "%02i-%02i" % (self.mon,self.day)
        return os.path.join( self.db.dbpath, dn)

  
    @property
    def JsonFileName(self):
        assert self.id != None 
        path = self.DirName
        fn = self.id+self.JSONEXT
        return  os.path.join( path, fn )
    
    @property
    def CacheFilePath(self):
        return os.path.join(self.db.imagepath,self.MakeCacheFileName() )


    def BmpFilePath(self):
        return os.path.join(self.db.bmppath,     ("%02i-%02i" % (self.mon,self.day)), "%s-r%02i%s" % (self.id,self.rank,self.db.cfg.BMPEXT ) )        

    def BmpCacheFilePath(self,enhance_mode):
        return os.path.join(self.db.bmpcachepath,("%02i-%02i" % (self.mon,self.day)), "%s-e%02i%s" % (self.id,enhance_mode,self.db.cfg.BMPEXT ) )        

            
     
        
    def MakeCacheFileName(self):
        assert self.id!=None
        MAXLEN = 20
        imgurlfix = self.imgurl.split("?", 1)[0]
        fn = str( urllib.parse.unquote(imgurlfix) )
        n =  fn.rfind('.')
        if n==-1:
            return ''
        ext = fn[n:]
        cfn = "%s-%02i-%02i%s" % (self.id,self.mon,self.day,ext)
        return cfn
        
        
    @staticmethod
    def CreateWikiId(tag,year):
        return "%s%04i" %(tag,year)
        
    @staticmethod
    def NewWiki(db,tag,year,mon,day,imgurl,wikiurl,text):
        id = DBEntry.CreateWikiId(tag,year)
        e = DBEntry.New(db,id,mon,day)
        e.imgurl = imgurl
        e.wikiurl = wikiurl
        e.text = text
        e.note = str(year)
        e.tag = tag
        return e
        
        

    @staticmethod
    def New(db,id,mon,day):
        e = DBEntry(db)
        e.day = day
        e.mon = mon
        e.id = id
        return e


    @property    
    def imgurlfixed(self):
        return "https:"+self.imgurl
     
        
    def ToDict(self):
        d = {}
        d['day']=self.day 
        d['mon']=self.mon 
        d['id']=self.id
        d['img']=self.imgurl
        d['url']=self.wikiurl
        d['text']=self.text 
        d['rank']=self.rank 
        d['enhance']=self.enhance  
        d['note']=self.note
        d['tag']=self.tag
        return d
        


        
    def Save(self,is_overwrite):
        data = self.ToDict()
        path = self.JsonFileName
        if (not os.path.isfile(path)) or  is_overwrite:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f,indent=4,ensure_ascii=False)
        else:
            print(f"File {path} already exists. Skiped.")
        
    @staticmethod 
    def Load(db,id,mon,day):
        e = DBEntry.New(db,id,mon,day)
        fn = e.JsonFileName
        if not os.path.isfile(fn):
            return None
        with open(fn, encoding='utf-8') as f:
            d = json.load(f)
            e.FromDict(d)
        return e
            
       
    def CopyFromDict(self,skey,dkey,dictdata,defaultvalue=None):
        setattr(self, skey,  dictdata[dkey] if dkey in dictdata else defaultvalue)
       
    def FromDict(self,d):
        assert d['id']==self.id 
        assert d['mon']==self.mon 
        assert d['day']==self.day 
        self.CopyFromDict('imgurl'   , 'img'     ,d)
        self.CopyFromDict('wikiurl'  , 'url'     ,d)
        self.CopyFromDict('text'     , 'text'    ,d)
        self.CopyFromDict('rank'     , 'rank'    ,d,self.RANK_NONE)
        self.CopyFromDict('note'     , 'note'    ,d)
        self.CopyFromDict('tag'      , 'tag'     ,d)
        self.CopyFromDict('enhance'  , 'enhance' ,d,self.ENHANCE_NONE)
        
        
    def FromDictEx(self,d):
        self.day = d['day']
        self.mon  = d['mon']
        self.id   = d['id']
        self.FromDict(d)


class DB():

 
    
    def make_folder(self,dir):
        if not os.path.exists(dir):
            os.makedirs(dir)        
    


    def __init__(self,cfg):
        assert cfg!=None
        self.cfg = cfg
        self.dbpath = cfg.DBDIR
        self.imagepath = cfg.IMAGEDIR
        self.bmppath = cfg.BMPDIR
        self.bmpcachepath = cfg.BMPCACHEDIR
        
        self.make_folder(self.dbpath )
        self.make_folder(self.imagepath )
        self.make_folder(self.bmppath  )

    def GetAllDay(self,mon,day):
        e = DBEntry.New(self,None,mon,day)
        daypath = e.DirName
        
        if not os.path.exists(daypath):
            return None
        
        r = []
        for file in os.listdir(daypath):
            if file.endswith(".json"): 
                filepath = os.path.join(daypath,file)
                with open(filepath, encoding='utf-8') as f:
                    d = json.load(f)
                    e = DBEntry(self)
                    e.FromDictEx(d)
                    r.append(e.ToDict())
        return r
        
        
