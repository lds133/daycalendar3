

import time
import urtc
from machine import I2C, Pin

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


i2c = I2C(0, scl=Pin(21), sda=Pin(20))
rtc = urtc.DS3231(i2c)

# Set the current time using a specified time tuple
# Time tuple: (year, month, day, day of week, hour, minute, seconds, milliseconds)
#initial_time = (2025, 1, 30, 1, 12, 30, 0, 0)

#initial_time_tuple = time.localtime()  # tuple (microPython)
#initial_time_seconds = time.mktime(initial_time_tuple)  # local time in seconds
#initial_time = urtc.seconds2tuple(initial_time_seconds)
#rtc.datetime(initial_time)



while True:
    current_datetime = rtc.datetime()
    temperature = rtc.get_temperature()
    
    # Display time details
    print('Current date and time:')
    print('Year:', current_datetime.year)
    print('Month:', current_datetime.month)
    print('Day:', current_datetime.day)
    print('Hour:', current_datetime.hour)
    print('Minute:', current_datetime.minute)
    print('Second:', current_datetime.second)
    print('Day of the Week:', days_of_week[current_datetime.weekday])
    print(f"Current temperature: {temperature}°C")    
    # Format the date and time
    formatted_datetime = (
        f"{days_of_week[current_datetime.weekday]}, "
        f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d} "
        f"{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d} "
    )
    print(f"Current date and time: {formatted_datetime}")
    
    print(" \n");
    time.sleep(1)