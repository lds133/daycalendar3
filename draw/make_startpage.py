import os
from draw.page import Page
from draw.template import CreateImageTemplate
from PIL import Image,  ImageDraw,ImageOps









def MakeReadmeBMP(cfg):

    page = Page(cfg)
    tmp = CreateImageTemplate(cfg.EINK_WIDTH,cfg.EINK_TOP)    
    img = ImageDraw.Draw(tmp)
    
    dx = 25
    x=30
    img.text((cfg.EINK_WIDTH/2, x), cfg.STARTPAGE_TITLE1, font=page.FONT_MID, anchor="mm")
    x+=dx
    img.text((cfg.EINK_WIDTH/2, x), cfg.STARTPAGE_TITLE2, font=page.FONT_MID, anchor="mm")
    x+=dx*3
    img.text((cfg.EINK_WIDTH/2, x), cfg.ASTRO_NAME, font=page.FONT_SML, anchor="mm")
    x+=dx
    img.text((cfg.EINK_WIDTH/2, x), "LAT %.2f, LON %.2f" % (cfg.ASTRO_LATITUDE,cfg.ASTRO_LONGITUDE), font=page.FONT_SML, anchor="mm")
    x+=dx*2
    img.text((cfg.EINK_WIDTH/2, x), cfg.STARTPAGE_URL, font=page.FONT_SML, anchor="mm")
    x+=dx*2
    img.text((cfg.EINK_WIDTH/2, x), cfg.STARTPAGE_VERSION, font=page.FONT_SML, anchor="mm")
    
    qr = Image.open(cfg.STARTPAGE_QRCODE_FILE).convert("1")
    qr = ImageOps.invert(qr)
    (qrh,qrv) = qr.size
    tmp.paste(qr, ( int((cfg.EINK_WIDTH-qrh)/2), cfg.EINK_TOP-qrv-10), qr)
    
    tmp.save( os.path.join(cfg.SDCARDDIR,cfg.STARTPAGE_BMP) )
    
    
    
def MakeReadmeTXT(cfg):
    lf = "\n"
    file = open( os.path.join(cfg.SDCARDDIR,cfg.STARTPAGE_TXT), "w",encoding="utf-8")

    
    file.write("Title:   "+ cfg.STARTPAGE_TITLE1+" "+ cfg.STARTPAGE_TITLE2+lf)
    file.write("Place:   "+ "%s [ %.2f , %.2f ]" % (cfg.ASTRO_NAME,cfg.ASTRO_LATITUDE,cfg.ASTRO_LONGITUDE)+lf)
    file.write("URL:     "+ cfg.STARTPAGE_URL+lf)
    file.write("Version: "+ cfg.STARTPAGE_VERSION+lf)    
    file.write(lf)    
    file.write("To set clock create a 'clock.txt' file with text using format 'YYYY-MM-DD HH:MM'"+lf)    
    
    
    file.close()
    
    
    
    

def MakeReadme(cfg):
    MakeReadmeBMP(cfg)
    MakeReadmeTXT(cfg)

    