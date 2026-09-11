# DayCalendar 3.0


## Create the SDCard 

Creates and fill '''sdcard''' directory.


### STAGE 0. Create environment


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


### STAGE 1. Fill images list from wikipedia "picture of the day"

Tested on Python 3.9.0  
    
https://en.wikipedia.org/wiki/Template:POTD/2023-01-01

https://uk.wikipedia.org/wiki/Вікіпедія:Зображення_дня

https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day

https://uk.wikipedia.org/wiki/Шаблон:Potd/2019-01


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


### STAGE 4. Convert downloaded color images to red-black-white BMPs to be used as calendar top part



### STAGE 5. Create red-black-white BMPs with day information for the calendar bottom part


### STAGE 6. Copy everything from 'sdcard' directory to a micro-sd-card.










## Hardware
























https://github.com/antgon/pico-ds3231/blob/main/lib/ds3231.c


https://github.com/alpertng02/pico-ds3231


https://kamami.pl/moduly-rtc/1184328-modds3231-modul-zegara-czasu--5906623483334.html


SDA GP16
SCL GP17

SQW GP22




https://wiki.kamamilabs.com/index.php?title=KAmodMicroSD_(PL)

https://kamami.pl/czytniki-kart-pamieci/587139-kamodmicrosd-5906623433377.html

https://github.com/elehobica/pico_fatfs

SD card module

5V
3.3V
GND
CS    CS     GP5
DI    MOSI   GP3   
CLK   SCK    GP2
DO    MISO   GP4
CD   



