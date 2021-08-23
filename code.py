import time
import board
import busio
import pwmio
import digitalio
import adafruit_ds3231
from analogio import AnalogIn

i2c = busio.I2C(board.GP1,board.GP0 )

rtc = adafruit_ds3231.DS3231(i2c)

log_file_name = "{0}{1:02d}{2:02d}-{3:02d}{4:02d}-{5:02d}.csv".format(rtc.datetime.tm_year,rtc.datetime.tm_mon,rtc.datetime.tm_mday,rtc.datetime.tm_hour,rtc.datetime.tm_min,rtc.datetime.tm_sec)
dbmeter = AnalogIn(board.A0)

blue_led = digitalio.DigitalInOut(board.LED_B)
blue_led.direction = digitalio.Direction.OUTPUT
red_led = pwmio.PWMOut(board.LED_R, frequency=1000, duty_cycle=0)
red_gamma = 0.6
green_led = pwmio.PWMOut(board.LED_G, frequency=1000, duty_cycle=0)
green_gamma = 0.1

logging_switch = digitalio.DigitalInOut(board.GP7)
logging_switch.direction = digitalio.Direction.INPUT
logging_switch.pull = digitalio.Pull.UP

logging_enabled = logging_switch.value
print("Logging:", logging_enabled)
if logging_enabled:
  print("Log filename:", log_file_name)
  try:
    with open(log_file_name, "a") as log_file:
      log_file.write("Time,Mean,Min,Max\n")
  except OSError as e:
    while True:
      blue_led.value = False
      time.sleep(0.25)
      blue_led.value = True
      time.sleep(0.25)

conversion_factor = (3.3 / 65535) * 100
sample_start = time.monotonic()
samples=[]
while logging_enabled:
  blue_led.value = True
  if time.monotonic()-sample_start > 60:
    blue_led.value = False
    smin = min(samples)
    smax = max(samples)
    smean = sum(samples) / len(samples)
    sample_start = time.monotonic()
    samples=[]
    try:
      with open(log_file_name, "a") as log_file:
        log_file.write("{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d},{5:.1f},{6:.1f},{7:.1f}\n".format(rtc.datetime.tm_year,rtc.datetime.tm_mon,rtc.datetime.tm_mday,rtc.datetime.tm_hour,rtc.datetime.tm_min,rtc.datetime.tm_sec,smean,smin,smax))
        print("{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d},{5:.1f},{6:.1f},{7:.1f}\n".format(rtc.datetime.tm_year,rtc.datetime.tm_mon,rtc.datetime.tm_mday,rtc.datetime.tm_hour,rtc.datetime.tm_min,rtc.datetime.tm_sec,smean,smin,smax))
    except OSError as e:
      while True:
        blue_led.value = False
        time.sleep(0.25)
        blue_led.value = True
        time.sleep(0.25)

  sample=dbmeter.value * conversion_factor
  red_brightness = ((sample-30)/100) * red_gamma
  green_brightness = ((130-sample)/100) * green_gamma
  red_led.duty_cycle = int(65535 - (65535 * red_brightness))
  green_led.duty_cycle = int(65535 - (65535 * green_brightness))
  samples.append(sample)
  print(sample)
  time.sleep(0.5)

blue_led.value = False
time.sleep(2)
blue_led.value = True