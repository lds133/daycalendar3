# DayCalendar 

This is a e-ink day calendar that provides a visual overview of the current day. It combines date, astronomical and calendar information with a randomly selected image to create a simple, ever-changing daily display. The device is designed to operate autonomously for extended periods without an internet connection or requiring any user interaction.

The calendar automatically generates an image containing:

-  Current day, month, and year
-  Day of the week
-  Sunrise and sunset times
-  Day length
-  Week number
-  Number of days elapsed and remaining in the current year
-  Current moon phase 
-  Moon rise and set times
-  A random daily image accompanied by its description

The displayed image is automatically updated three times per day.

[A monument to the thing that is gone.](history/readme.md)

## Hardware

The project is built around a Raspberry Pi Pico 2 and a three-color e-ink display. The electronics are assembled on a universal prototype soldering board and mounted inside a 25 cm photo frame, which serves as the project's case.

![Front](hardware/doc/front.png)

See [hardware](hardware/readme.md)

## SD card

The device requires a prepared SD card containing the images used by the calendar. The SD card can be prepared manually or generated automatically using the Python scripts included in this repository.

![Front](hardware/doc/sdcard.png)

See [SD card](sdcard.md)