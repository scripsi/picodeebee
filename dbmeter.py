import machine
import utime

dbmeter = machine.ADC(26)
conversion_factor = (3.3 / 65535) * 100

while True:
    print(dbmeter.read_u16() * conversion_factor)
    utime.sleep(0.1)