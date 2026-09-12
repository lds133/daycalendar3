# test_clock.py
# Quick manual test for clock.py on the Pico 2 + DS3231.

from clock import Clock

clk = Clock()

# 1. Set a known time.
#clk.settime(2026, 9, 12, 20, 55)


print("Time after settime:", clk.gettime())

# 2. Read it back.
y, mo, d, h, mi = clk.gettime()
print(f"Current time -> {y:04}-{mo:02}-{d:02} {h:02}:{mi:02}")

# 3. Wait until 1 minute from now (board will lightsleep until the
#    DS3231 alarm fires). Adjust target as needed for your test.
target_min = (mi + 1) % 60
target_hour = h if target_min != 0 else (h + 1) % 24
print(f"Sleeping until {target_hour:02}:{target_min:02} ...")

clk.waittill_active(y, mo, d, target_hour, target_min)
#clk.waittill(y, mo, d, target_hour, target_min)

print("Woke up! Time now:", clk.gettime())