


class CFG():

    DIRSEP = '/'
    SDCARDDIR = 'sdcard'
    
    
    DBDIR = SDCARDDIR + DIRSEP +'db' # database. json files
    CACHEDIR = SDCARDDIR + DIRSEP +'cache' # wiki source images (color)
    BMPDIR = SDCARDDIR + DIRSEP +'bmp' # images converted to 3 color bmp
    BMPEXT= '.bmp'
    
    FIRSTYEAR = 2008 # grabbing start year
    LASTYEAR = 2026  # grabbing end year (not include)
    
    
    
    IS_OVERWRITE_JSON = False # overwrite json file if it already exists
    
    
    READ_HTML_HEADERS =  {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'} # wiki html grabbing user agent
    READ_IMAGE_HEADERS =  {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'} # wiki image grabbing user agent
        
    TMP_FOLDER = SDCARDDIR + DIRSEP + 'tmp'   # html files grabbed from wikipedia 
       
       
    POLITE_DELAY_SEC = 0.5 # small polite delay
    
    
    EINK_HEIGHT = 640
    EINK_WIDTH = 384    
    EINK_TOP = 426  # height of the top part 

    
    
    DRAW_DIR = 'draw'
    
    SPRITE_DIR =  DRAW_DIR+DIRSEP+'sprite'
    SPRITE_EXT = '.bmp'
    
    
    EINK_TEMPLATE_PATH = DRAW_DIR+DIRSEP+ 'eink_template.bmp'
    
    
    FONT_DIR = DRAW_DIR+DIRSEP+'font'
    
    
    DOW_STR_LIST = ["ПОНЕДІЛОК","ВІВТОРОК","СЕРЕДА","ЧЕТВЕР","П'ЯТНИЦЯ","СУБОТА","НЕДІЛЯ"]
    MON_STR_LIST = ["СІЧЕНЬ","ЛЮТИЙ","БЕРЕЗЕНЬ","КВІТЕНЬ","ТРАВЕНЬ","ЧЕРВЕНЬ","ЛИПЕНЬ","СЕРПЕНЬ","ВЕРЕСЕНЬ","ЖОВТЕНЬ","ЛИСТОПАД","ГРУДЕНЬ"]      
    
    
    ASTRO_NAME = 'Warsaw'
    ASTRO_REGION = 'Poland'
    ASTRO_TIMEZONE_NAME = 'Europe/Warsaw'
    ASTRO_LATITUDE = 52.20
    ASTRO_LONGITUDE = 21.01
    
    DAY_MONSTR = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    DAY_MOONPHASE = ['Новий місяць','Перша чверть','Повний місяць','Ост. чверть']
    DAY_MONNSPRITENAMES = ["newmoon","youngmoon","fullmoon","oldmoon"]    
    
    DAY_LINE_HEIGHT = 20
    DAY_YMARGIN     = 5
    DAY_XMARGIN     = 2
    DAY_SEPWIDTH    = 40
    DAY_SEPHEIGHT   = 0
    DAY_TINYMARGIN  = 1    