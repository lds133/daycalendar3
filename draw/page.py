
import os
import datetime
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageFont, ImageDraw
from draw.astro import AstroData
from wiki_grabber.database import DB,DBEntry
from draw.template import CreateImageTemplate



class Page():


   
    
    def __init__(self,cfg):
        self.cfg = cfg
        self.eink_width = cfg.EINK_WIDTH
        self.eink_height = cfg.EINK_TOP        
        self.FONT_SML = ImageFont.truetype(cfg.FONT_DIR + '/mini_pixel-7.ttf', size=20)
        self.FONT_BIG = ImageFont.truetype(cfg.FONT_DIR + '/ClementFive.ttf', size=150)
        self.FONT_MID = ImageFont.truetype(cfg.FONT_DIR + '/timesbd.ttf', size=25)
        self.dowstr = cfg.DOW_STR_LIST
        self.monstr = cfg.MON_STR_LIST
        self.eink_margin = 0
        self.LINE_SPACING = 0.9  

        self.cal_page = "tmp_calpage.bmp"
        
            


    def filter_colors(self,image):
        image = image.convert("RGB")
        pixels = image.load()

        for y in range(image.height):
            for x in range(image.width):
                r, g, b = pixels[x, y]
                if (r > g and r > b and g<50 and b<50):  
                    pixels[x, y] = (255, 0, 0)  
                elif (r < 50 and g <50 and b<50 ):  
                    pixels[x, y] = (0, 0, 0)  
                else: 
                    pixels[x, y] = (255, 255, 255)  
                    
        return image


    def increase_contrast(self,image, contrast_factor):
        image = image.convert("RGB")
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(contrast_factor)
        return enhanced_image
        
        
        
        
        
    def make_bmp(self,dbentry,enhance_mode,maxheight):

        if not os.path.isfile(dbentry.ImageFilePath):
            print("Image %s not found" % dbentry.ImageFilePath)
            return None
        im = Image.open(dbentry.ImageFilePath) 

        if (enhance_mode==DBEntry.ENHANCE_FOTO):
            im = self.increase_contrast(im,2)
        elif (enhance_mode==DBEntry.ENHANCE_CLIPART):
            im = self.increase_contrast(im,5)
            im = self.filter_colors(im)
        elif (enhance_mode==DBEntry.ENHANCE_BW):
            im = im.convert('L')
        elif (enhance_mode==DBEntry.ENHANCE_BW2):
            im = im.convert('L')            
            im = self.increase_contrast(im,2)

            
        width,height = im.size
        actiontxt = ''
        if (width>self.eink_width) or (height>maxheight):
            actiontxt = 'Resize'
            im.thumbnail((self.eink_width-self.eink_margin ,maxheight-self.eink_margin ), Image.LANCZOS)
        else:
            actiontxt = 'Image'
        w,h = im.size
        print("%s %ix%i" % (actiontxt,w,h))
        

        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette([
            0, 0, 0,      
            255, 255, 255, 
            255, 0, 0     
        ] * 85)  

        dithered_image = im.convert("RGB").quantize(palette=palette_image, dither=Image.FLOYDSTEINBERG)
        #dithered_image = im.convert("RGB").quantize(palette=palette_image, dither=Image.NONE)

        dithered_image = dithered_image.convert("RGB")
        px = dithered_image.load()

        #dithered_image.save(dbentry.BmpFilePath)
        
        return dithered_image
        
        
        

        
        
    def save_tmp(self,tmp,issavefile=True):
        tmp = tmp.rotate(270,expand=True)
        if issavefile:
            tmp.save(self.cal_page)
            print("Saved",self.cal_page)
        return tmp   


    def draw_img(self,tmp,img,xoffset,yoffset):
        w,h = img.size
        px = img.load()
        for x in range(w):
            for y in range(h):
                r, g, b = px[x, y]
                pos = (x+xoffset,y+yoffset)
                if (r==0 and g==0 and b==0):
                    tmp.putpixel( pos,  0)
                elif (r==255 and g==255 and b==255):
                    tmp.putpixel( pos,  2)
                else:
                    tmp.putpixel( pos,  1)
                    



    def wrap_txt(self,text, max_width, font):
        lines = []
        words = text.split(' ')
         
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            #line_width, _ = font.getsize(test_line)
            
            fleft, ftop, fright, fbottom = font.getbbox(test_line)
            line_width  = fright - fleft        
            
            
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line[:-1])
                current_line = word + ' '
     
        lines.append(current_line[:-1])
        return lines
        
        
    def draw_txt(self,image, font, sentence, ypos ):
         
        font_size = font.size
        max_width = int(image.width * 0.9)
        wrapped_text = self.wrap_txt(sentence, max_width, font)
        line_spacing = self.LINE_SPACING 
        draw = ImageDraw.Draw(image)
        x = (image.width - max_width) // 2
        #y = (image.height - int(font_size * len(wrapped_text) * line_spacing)) // 2
        y=ypos
         
        for line in wrapped_text:
            line_width  = self.measure_txt_ex(font, line )
            draw.text(((image.width - line_width) // 2, y), line, 0, font=font)
            y += int(font_size * line_spacing)
     


    def print_wide(self,draw,font,color,xpos,ypos,width,text):
        w0 = 0
        n = len(text)
        if (n==0):
            return
        for c in text:
            w0 += self.measure_txt_ex(font, c)
        if (n==1):
            dx = 0
            x = xpos + (width - w0)
        else:
            dx = (width - w0)/(n-1)
            x = xpos
        
        for c in text:
            draw.text((x,ypos), c, font=font,fill=color)
            w = self.measure_txt_ex(font, c)
            x+=dx+w
            
        



    def measure_txt_ex(self,font, text ):
        fleft, ftop, fright, fbottom = font.getbbox(text)
        width  = fright - fleft
        #line_width, _ = font.getsize(line)        
        return width
    


    def measure_txt(self,image, font, sentence  ):
        font_size = font.size
        max_width = int(image.width * 0.9)
        wrapped_text = self.wrap_txt(sentence, max_width, font)
        line_spacing = self.LINE_SPACING 
        y=0
        for line in wrapped_text:
            line_width  = self.measure_txt_ex(font, line )
            y += int(font_size * line_spacing)
            
        return y
        
        
        
    def print_day(self,image, day, font, centerx, centery,color):
        font = self.FONT_BIG
        img = ImageDraw.Draw(image)   
        daystr = str(day)
        if (len(daystr)==1):
            img.text((centerx, centery), daystr, font=font, anchor="mm",fill=color)
            w = self.measure_txt_ex(font, daystr )            
            xr = centerx - w//2
            xl = centerx + w//2

            return (xr,xl)
            
        else:
            oneshift = 0
            if (daystr[0]=='1'):
                oneshift += 10
            if (daystr[1]=='1'):                
                oneshift += 5                
            img.text((centerx+oneshift, centery), daystr[0], font=font, anchor="rm",fill=color)
            img.text((centerx-oneshift, centery), daystr[1], font=font, anchor="lm",fill=color)
            w1 = self.measure_txt_ex(font, daystr[0] )            
            w2 = self.measure_txt_ex(font, daystr[1] )            
            return (centerx+oneshift-w1,centerx-oneshift+w2)
            


    def draw_date(self,tmp,year,mon,day):
        seplinewidth = 3  
        seplinemargin = 2

        edate = datetime.date(year, mon, day)
        dow = edate.weekday()
        dowtext = self.dowstr[dow]
        montext = self.monstr[mon-1]
    
        color = 0
        if (dow==6):
            color = 1
            
        topmargin = 0
        einkwidth, einkheight = tmp.size

       
        date_ypos =topmargin+seplinewidth+ (einkheight-topmargin-seplinewidth)//2
        
        img1 = ImageDraw.Draw(tmp)   
        img1.rectangle([(seplinemargin , topmargin+1), (einkwidth-seplinemargin, topmargin+seplinewidth-1)] , fill = 0) 
        (xl,xr) = self.print_day(tmp,day,self.FONT_BIG,einkwidth /2, date_ypos,color)
        
        
        TEXTSPACE = 45
        TEXTMARGIN = 2
        textwidth = (einkwidth -TEXTSPACE)//2 - TEXTMARGIN
        self.print_wide(img1,self.FONT_MID,color,seplinemargin,topmargin+seplinewidth+1,textwidth,montext)
        self.print_wide(img1,self.FONT_MID,color,textwidth + TEXTSPACE,topmargin+seplinewidth+1,textwidth,dowtext)

        return (xl,xr)
        
        
        
    def make_picture(self,e,enhance_mode):
        assert( e!=None )

        
        tmp = CreateImageTemplate(self.cfg.EINK_WIDTH,self.cfg.EINK_TOP)
        htxt = self.measure_txt(tmp,self.FONT_SML,e.text)

        bmp = self.make_bmp(e,enhance_mode,self.cfg.EINK_TOP-htxt)
        if bmp==None:
            return None

        wbmp,hbmp = bmp.size
        xbmp = (self.cfg.EINK_WIDTH - wbmp) // 2
        ybmp = (self.cfg.EINK_TOP-htxt - hbmp) // 2

        self.draw_img(tmp,bmp,xbmp ,ybmp)

        picbottom = ybmp+hbmp
        texttop = self.cfg.EINK_TOP - htxt
        
        dy = (texttop-picbottom)//2

        self.draw_txt(tmp,self.FONT_SML,e.text,texttop-dy)
        
        return tmp        
        
        
        
        
    def make_day(self,year,mon,day):
        astro = AstroData(self.cfg)
        tmpheight = self.cfg.EINK_HEIGHT - self.cfg.EINK_TOP
        tmp =   CreateImageTemplate(self.cfg.EINK_WIDTH,tmpheight)
        
        (xl1,xr1) = self.draw_date(tmp,year,mon,day)
        astro_width = 93
        (xl2,xr2) = (astro_width,self.cfg.EINK_WIDTH-astro_width)
        xl = min(xl1,xl2)
        xr = max(xr1,xr2)
        
        astro_offset = 40
        astro.SetPos(xl,xr, astro_offset,self.cfg.EINK_WIDTH,tmpheight)
        astro.SetDay(year,mon,day)
        astro.draw(tmp)
       
        return tmp        
        
  
        
