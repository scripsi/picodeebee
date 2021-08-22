import time
import board
import busio
import pwmio
import digitalio
from adafruit_bus_device.i2c_device import I2CDevice
from analogio import AnalogIn

i2c = busio.I2C(board.GP1,board.GP0 )
# address for RV3028 Real Time Clock
i2caddress = 0x52
# RV3208 Registers
SECONDS = 0x00  # count of seconds, in 2 BCD digits. Values from 00 to 59.
MINUTES = 0x01  # count of minutes, in 2 BCD digits. Values from 00 to 59.
HOURS   = 0x02  # count of hours, in 2 BCD digits. Values from 00 to 12, or 00 to 24. 
WEEKDAY = 0x03
DATE    = 0x04
MONTH   = 0x05
YEAR    = 0x06
rtc = I2CDevice(i2c,i2caddress)

def decode_rtc(value):
  upper = ((int.from_bytes(value, "big") & 0xF0) >> 4) * 10
  lower = (int.from_bytes(value, "big") & 0x0F)
  return(upper + lower)

def get_rtc(register):
  with rtc:
    rtc.write(bytes([register]))
    result = bytearray(1)
    rtc.readinto(result)
    return decode_rtc(result)


log_file_name = "{0}{1:02d}{2:02d}-{3:02d}{4:02d}-{5:02d}.csv".format(get_rtc(YEAR)+2000,get_rtc(MONTH),get_rtc(DATE),get_rtc(HOURS),get_rtc(MINUTES),get_rtc(SECONDS))
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
        log_file.write("{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d},{5:.1f},{6:.1f},{7:.1f}\n".format(get_rtc(YEAR)+2000,get_rtc(MONTH),get_rtc(DATE),get_rtc(HOURS),get_rtc(MINUTES),smean,smin,smax))
        print("{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d},{5:.1f},{6:.1f},{7:.1f}\n".format(get_rtc(YEAR)+2000,get_rtc(MONTH),get_rtc(DATE),get_rtc(HOURS),get_rtc(MINUTES),smean,smin,smax))
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