
import os
import time
import datetime
import json
from PIL import Image

from http.server import HTTPServer, BaseHTTPRequestHandler


import socket

from wiki_grabber.database import DB,DBEntry





NOID = '*'
db = None



def TrySplit(text):
    try:
        r = text.split('/')
        if (len(r)<5):
            return (r[1],None)
        else:
            if (r[2] == NOID):
                r[2] = None
            e = DBEntry.New(db,r[2],int(r[3]),int(r[4]))
            if (len(r)>=6):
                e.enhance = int(r[5])
            if (len(r)>=7):
                e.rank = int(r[6])
                
            return (r[1],e)
    except:
        pass
    return (None,None)





class DayCalendarServer(BaseHTTPRequestHandler):


    def do_GET_sendfile(self,filepath:str,mimo:str):
        try:
            f = open(filepath, "rb") 
            databytes =  f.read()               
            f.close()  
        except Exception as e:
            databytes = None
            print("File read error '%s' :%s" % (filepath,str(e)))
            
        if (databytes!=None):
            self.send_response(200)
            self.send_header("Content-type", mimo)
        else:
            self.send_response(404)
       
        self.end_headers()
        if (databytes!=None):
            self.wfile.write(databytes)  
    

    def do_GET(self):
        
        if self.path == '/':
           self.path = '/tab/*/1/1'
           
        print("GET:",self.path)

        #if (self.path.startswith('/'+FAVICON)):
        #    self.do_GET_sendfile(FAVICON,"image/ico")
        #    return

           
           
           
        (prefix,e) = TrySplit(self.path)
        
        if (e==None):
            print("Wrong format :",self.path)
            self.send_response(403)
            return




        if (prefix=='bmp'):
            file_name = e.BmpCacheFilePath(e.enhance)
            self.do_GET_sendfile(file_name ,"image/bmp")
            return
                
           
        if (prefix=='tab') or (prefix=='lst'):
           self.send_response(200)
           self.end_headers()
           self.wfile.write( bytes(self.IndexHtml(prefix,e), 'utf-8'))
           return

        if (prefix=='dat'):
           daydata = db.GetAllDay(e.mon,e.day)
           if (daydata==None):
                #self.send_response(404)
                #return
                daydata = []
           self.send_response(200)
           self.send_header("Content-type", 'application/json')
           self.end_headers()
           self.wfile.write( bytes( json.dumps(daydata) , 'utf-8'))
           return
           
        if (prefix=='set'):
           e.Update() 
           result = "ok"
           self.send_response(200)
           self.end_headers()
           self.wfile.write( bytes(result, 'utf-8'))
           return           
            
        print("Wrong prefix:",self.path)
        self.send_response(403)




    def IndexHtml(self, prefix,e):
    
       
        maindivid = "maindiv"
        scriptexe = 'main("'+str(e.id)+'",'+str(e.mon)+','+str(e.day)+',"'+maindivid+'","'+prefix+'");'

        with open('viewer/index.js') as f:
            scriptcontents = f.read()
            
        return """
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
                <meta charset="utf-8">
                <title>Day Calendar</title>
              </head>
              <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>              
              <script src="https://code.jquery.com/jquery-3.7.1.min.js"  integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
              <script>""" + scriptcontents + """</script>
              <body> <div id = '""" + maindivid + """'></div></body>
              <script>""" + scriptexe + """</script>
            </html>"""

        
    
#todo: implement support for multiple network interfaces
def get_my_ips():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80)) 
        yield s.getsockname()[0]  
    finally:
        s.close()

    
def run_server(cfg):    
    global db
    db = DB(cfg)
    httpd = HTTPServer((cfg.SERV_IPADDR,cfg.SERV_PORT),DayCalendarServer)
    for ip in get_my_ips():
        print(r"Serving at http://%s:%i/" % (ip,cfg.SERV_PORT))
    httpd.serve_forever() 


