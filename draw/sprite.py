import os

from PIL import Image




def sprite_path(cfg,sprite_name):
    return os.path.join(cfg.SPRITE_DIR,sprite_name+cfg.SPRITE_EXT)

def sprite_put(cfg,image,sprite_name,xpos,ypos):
    s = Image.open(sprite_path(cfg,sprite_name)) 
    w,h = s.size
    px = s.load()
    for x in range(w):
        for y in range(h):
            c = px[x, y]
           
            if (c==255):
                c=2
            
            pos = (int(x+xpos),int(y+ypos))
            #print(">>",x,y,c,pos)
            image.putpixel( pos,  c)
