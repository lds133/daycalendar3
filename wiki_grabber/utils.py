import os
import requests



def MakeTMP(cfg,filename:str)->str:
    return os.path.join(cfg.TMP_FOLDER,filename)


def ReadHTML(cfg,url:str,filename:str=None)->str:
    if os.path.exists(MakeTMP(cfg,filename)):
       return ReadHTMLFromFile(cfg,filename)
    return ReadHTMLFromURL(cfg,url,filename)


def ReadHTMLFromURL(cfg,url:str,filename:str=None)->str:
    html_text = None
    with requests.Session() as s:
        print("Reading: "+url)
        r = s.get(url, headers=cfg.READ_HTML_HEADERS)
        html_text = r.text
        if (filename!=None):
            if not os.path.exists(cfg.TMP_FOLDER):
                os.makedirs(cfg.TMP_FOLDER)
            filename = MakeTMP(cfg,filename)
            print("Writing HTML: "+filename)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_text)

    return html_text


def ReadHTMLFromFile(cfg,filename:str)->str:
    print("Reading HTML: "+filename)
    html_text = None
    with open(MakeTMP(cfg,filename),encoding='utf-8') as fp:
        html_text = fp.read()
    return html_text