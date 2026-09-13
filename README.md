# DayCalendar 3.0


## Prepare hardware

![Front](hardware/doc/front.png)

See [hardware](hardware/readme.md)



## Prepare the SDCard 

![Front](hardware/doc/sdcard.png)


### STAGE 0. Create environment

Tested on Python 3.13

windows 

```
C:\TOOLS\python313\python.exe -m venv  .venv
.venv\Scripts\activate
pip install -r requirements.txt
```


linux
```
python3 -m venv  .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Check settings.py for directory names and other staff






### STAGE 1. Fill images list from wikipedia ["picture of the day"](https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day)

[English Potd](https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day/Archive)

[Ukrainian Potd](https://uk.wikipedia.org/wiki/Шаблон:Potd/2019-01) 
  
```
python run_grab_wiki.py
```
Fills **db** dirctory with json files







### STAGE 2. Load color images from the wikipedia site
```
python run_download_images.py
```
Fills **cache** folder with images







### STAGE 3. Edit the collected database

#### 3.1 Create cache bmp images in **bmpcache** folder with different enhance mode applyed to be reviewed later.
```
python run_make_bmps.py
```

#### 3.2 Update **rank** and **enhance** parameters for all images
```
python run_viewer.py
```

See the web server [UI description](viewer/readme.md)







### STAGE 4. Copy created red-black-white BMPs to be used as calendar top part

```
python run_make_tops.py
```
Fills **bmp** folder with the converted images. 

See [MIN_RANK](settings.py) parameter



### STAGE 5. Create red-black-white BMPs with day information for the calendar bottom part

```
python run_make_bottoms.py
```
Fills **days** folder with the day images. 


See [CALENDAR_YEARS_COUNT](settings.py) parameter



### STAGE 6. Copy calendar data from 'sdcard' directory to a sd card.

The next artefacts are essential **bmp** and **days** folers, **readme.txt** and **readme.bmp** files.

The SD card must be FAT32 formatted.





















