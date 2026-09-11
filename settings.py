


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