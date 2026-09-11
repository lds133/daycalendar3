
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageFont, ImageDraw
from astral import LocationInfo
import datetime
from astral import moon
from astral.moon import moonrise, moonset
from astral.sun import sunrise, sunset
from astral.location import Location
from draw.sprite import sprite_put

class AstroData():



    def __init__(self,cfg):
        self.cfg = cfg

        self.monstr =           cfg.DAY_MONSTR
        self.moonphase =        cfg.DAY_MOONPHASE
        self.moonspritenames =  cfg.DAY_MONNSPRITENAMES
        self.FONT  = ImageFont.truetype(cfg.FONT_DIR + '/times.ttf', size=14)
        self.FONT2 = ImageFont.truetype(cfg.FONT_DIR +'/times.ttf', size=16)
        self.FONT3 = ImageFont.truetype(cfg.FONT_DIR +'/timesbd.ttf', size=25)
        self.LINE_HEIGHT =  cfg.DAY_TINYMARGIN   
        self.YMARGIN =      cfg.DAY_SEPHEIGHT    
        self.XMARGIN =      cfg.DAY_SEPWIDTH     
        self.SEPWIDTH =     cfg.DAY_XMARGIN      
        self.SEPHEIGHT =    cfg.DAY_YMARGIN      
        self.TINYMARGIN =   cfg.DAY_LINE_HEIGH  
        self.DASH ="\u2012"
        
        self.city = LocationInfo(cfg.ASTRO_NAME, cfg.ASTRO_REGION, cfg.ASTRO_TIMEZONE_NAME, cfg.ASTRO_LATITUDE, cfg.ASTRO_LONGITUDE)
        self.sunset = None
        self.sunrise = None
        self.moonset = None
        self.moonrise = None
        self.daysleft = None
        self.daysright = None
        self.daylong = None
        self.moonstate = None
        self.moondate = None
        self.sunsprite = None
        self.moonsprite = None
        self.XL = None
        self.XR = None
        self.YT = None
        
        
        
    def SetPos(self,x_pos_left,x_pos_right,y_pos_top,x_pos_max,y_pos_max):
        self.XL = x_pos_left-self.XMARGIN
        self.XR = x_pos_right+self.XMARGIN
        self.YT = y_pos_top+self.YMARGIN
        self.WL = self.LINE_HEIGHT
        self.XMAX = x_pos_max - self.TINYMARGIN 
        self.XMIN = self.TINYMARGIN 
        self.YMAX = y_pos_max
        
        
    def is_leap_year(self,year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)        
        
        
    def TimeDiffToHoursMins(self,time_diff):
        dd_totalmin = time_diff.total_seconds() // 60
        dd_h = dd_totalmin // 60
        dd_m = dd_totalmin - dd_h*60
        return (dd_h,dd_m)
        
       
    def AccurateMoon(self,curr_date):
        i = self.MoonPhaseInt(curr_date)
        dt = datetime.timedelta(days=1)
        
        d0 = curr_date
        while (self.MoonPhaseInt(d0-dt)==i):
            d0-=dt
        d1 = curr_date
        while (self.MoonPhaseInt(d1+dt)==i):
            d1+=dt
        dm = d0 + (d1-d0)/2
        return dm
            
        

    def MoonPhaseInt(self,curr_date):
        moonphase = moon.phase(curr_date)
        if moonphase > 0 and moonphase < 6.99 :
            moonphase_int = 0
        elif moonphase > 6.99 and moonphase < 13.99 :
            moonphase_int = 1
        elif moonphase > 13.99 and moonphase < 20.99 :
            moonphase_int = 2
        elif moonphase > 20.99 and moonphase < 27.99 :
            moonphase_int = 3
        return moonphase_int

       
    def SetDay(self, year,mon,day):
        d = datetime.datetime(year, mon, day)
        
        sr = sunrise(self.city.observer, d, self.city.tzinfo)
        print('Sun Rise: ', sr)
        ss = sunset(self.city.observer, d, self.city.tzinfo)
        print('Sun Set: ', ss)        
        self.sunrise = "%i.%02i" % (sr.hour,sr.minute)
        self.sunset = "%i.%02i" % (ss.hour,ss.minute)
        (dd_h,dd_m) = self.TimeDiffToHoursMins(ss-sr)
        self.daylong = "%i.%02i" % (dd_h,dd_m)
        self.sunsprite = "sun"
        
        try:
            mr = moonrise(self.city.observer, d, self.city.tzinfo)
            if (mr==None):
                raise "None"
            print('Moon Rise: ', mr)
            self.moonrise = "%i.%02i" % (mr.hour,mr.minute)
        except Exception as e:
            print('Moon Rise: ', str(e))
            self.moonrise = self.DASH
            
        try:
            ms = moonset(self.city.observer, d, self.city.tzinfo)
            if (ms==None):
                raise "None"
            print('Moon Set: ', ms)
            self.moonset = "%i.%02i" % (ms.hour,ms.minute)
        except Exception as e:
            print('Moon Set: ', str(e))
            self.moonset = self.DASH

        moonphase_int = self.MoonPhaseInt(d)
        moonphase_str = self.moonphase[moonphase_int]
        self.moonsprite = self.moonspritenames[moonphase_int]
        print('Moon Phase: ', moonphase_str)      
        m_date = self.AccurateMoon(d)
        self.moonstate = moonphase_str
        
        if (m_date.day==d.day) and (m_date.month==d.month):
            self.moondate =  "" 
        else:
            self.moondate =  "%i.%s" % (m_date.day,self.monstr[ m_date.month - 1 ])


        self.year = str(year)
        doy = d.timetuple().tm_yday
        self.weekno = str(  (doy-1)//7 +1 )
        dmax = 366 if self.is_leap_year(year) else 365        
        self.daysleft = self.DASH+str( doy )
        self.daysright = "+"+str( dmax-doy )
    
        
    def draw(self, image):
        img = ImageDraw.Draw(image) 
        
        
        y = self.YT
        sprite_put(image,self.sunsprite,self.XMIN,y)
        
        y += self.WL
        img.text((self.XMIN,y),"Схід", font=self.FONT)
        img.text((self.XL,y),self.sunrise, font=self.FONT,anchor="ra")

        y += self.WL
        img.text((self.XMIN,y),"Зах.", font=self.FONT)
        img.text((self.XL,y),self.sunset, font=self.FONT,anchor="ra")
        
        y += self.WL
        img.text((self.XMIN,y),"Довжина", font=self.FONT)

        y += self.WL
        img.text((self.XMIN,y),"дня", font=self.FONT)
        img.text((self.XL,y),self.daylong, font=self.FONT,anchor="ra")
        
        y += self.WL+self.YMARGIN
        img.rectangle([(self.XMIN , y), (self.XMIN+self.SEPWIDTH,y+ self.SEPHEIGHT)] , fill = 0) 
        
        y += self.YMARGIN
        img.text((self.XMIN,y),self.daysleft, font=self.FONT2)
        

        
        y = self.YT
        sprite_put(image,self.moonsprite,self.XR,y)
        
        y += self.WL
        img.text((self.XMAX,y),self.moonstate, font=self.FONT,anchor="ra")
        
        y += self.WL
        img.text((self.XMAX,y),self.moondate , font=self.FONT,anchor="ra")
        
        y += self.WL
        img.text((self.XR,y),"Схід", font=self.FONT)
        img.text((self.XMAX,y),self.moonrise, font=self.FONT,anchor="ra")
        
        y += self.WL
        img.text((self.XR,y),"Зах.", font=self.FONT)
        img.text((self.XMAX,y),self.moonset, font=self.FONT,anchor="ra")
        
        y += self.WL+self.YMARGIN
        img.rectangle([(self.XMAX- self.SEPWIDTH, y), (self.XMAX, y+self.SEPHEIGHT)] , fill = 0)         
        
        y += self.YMARGIN
        img.text((self.XMAX,y),self.daysright, font=self.FONT2,anchor="ra")        
        
        
        y = self.YMAX-self.FONT3.size-self.YMARGIN
        img.text((self.XMIN, y), self.weekno+" т.", font=self.FONT3)        
        img.text((self.XMAX, y), self.year , font=self.FONT3,anchor="ra")
        
        