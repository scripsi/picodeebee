import time
import board
import busio
import pwmio
import math
import digitalio
import adafruit_ds3231
from analogio import AnalogIn

i2c = busio.I2C(board.GP1,board.GP0 )

rtc = adafruit_ds3231.DS3231(i2c)

log_file_name = "{0}{1:02d}{2:02d}-{3:02d}{4:02d}-{5:02d}.csv".format(rtc.datetime.tm_year,rtc.datetime.tm_mon,rtc.datetime.tm_mday,rtc.datetime.tm_hour,rtc.datetime.tm_min,rtc.datetime.tm_sec)
dbmeter = AnalogIn(board.A0)

#                                                                      _        _
# The Pimoroni Tiny2040 LEDs work in inverse - False = On; True = Off   \_(ツ)_/
led_on = False
led_off = True
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
sampling_enabled = True

print("Logging:", logging_enabled)
if logging_enabled:
  print("Log filename:", log_file_name)
  try:
    with open(log_file_name, "a") as log_file:
      log_file.write("Time,LAeq,LAFmin,LAFmax\n")
  except OSError as e:
    while True:
      red_led.value = False
      time.sleep(0.25)
      red_led.value = True
      time.sleep(0.25)

# log summary data to file every 60 seconds
log_interval = 60

# sample values from meter every 0.125 seconds = "fast" mode in sound measurements
sample_interval = 0.125

# meter outputs 0.01V per dB. The ADC value is referenced to V(supply) = 3.3V.
# This converts ADC value to dB measurement
conversion_factor = (3.3 / 65535) * 100

sample_start = time.monotonic()
samples=[]
while sampling_enabled:
  blue_led.value = led_off

  # if logging interval reached, then log summary data to file/screen and reset samples array
  if time.monotonic()-sample_start > log_interval:
    sample_start = time.monotonic()

    # **BUG https://github.com/adafruit/circuitpython/issues/4863
    # The documented math.log10() function not present in 6.3.0 - use
    # math.log(x, base) instead
    # LAFmin is the minimum dBA level during the sample period
    lafmin = math.log(min(samples),10) * 10
    # LAFmax is the maximum dBA level during the sample period
    lafmax = math.log(max(samples),10) * 10
    # LAeq is the equivalent continuous dBA level during the sample period
    laeq = math.log(sum(samples) / len(samples),10) * 10
    log_time = rtc.datetime
    log_text = "{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d},{5:.1f},{6:.1f},{7:.1f}\n".format(log_time.tm_year,log_time.tm_mon,log_time.tm_mday,log_time.tm_hour,log_time.tm_min,laeq,lafmin,lafmax)
    print(log_text)
    samples = []
    if logging_enabled:
      # show file activity by flashing blue led
      blue_led.value = led_on
      try:
        with open(log_file_name, "a") as log_file:
          log_file.write(log_text)
      except OSError as e:
        while True:
          red_led.value = led_on
          time.sleep(0.25)
          red_led.value = led_off
          time.sleep(0.25)

  sample_db = dbmeter.value * conversion_factor
  # dB is a logarithmic conversion of sound pressure level (SPL), which makes summary
  # maths like averages difficult. Converting the dB value back to SPL makes it easier
  # to do maths with later.
  sample_spl = math.pow(10,sample_db/10)
  samples.append(sample_spl)
  print(sample_db, sample_spl)

  # Set the LEDs to give an indication of the meter reading: green = low; orange = medium; red = high
  red_brightness = ((sample_db-30)/100) * red_gamma
  green_brightness = ((130-sample_db)/100) * green_gamma
  red_led.duty_cycle = int(65535 - (65535 * red_brightness))
  green_led.duty_cycle = int(65535 - (65535 * green_brightness))

  time.sleep(sample_interval)
