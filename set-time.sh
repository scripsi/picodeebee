#!/bin/bash

# Uses the serial interface to the CircuitPython REPL to run the commands
# to set the time on an RTC connected to the CircuitPython device

# set up the serial port parameters
stty --file=/dev/ttyACM0 115200 cs8 -cstopb -parenb raw -echo

exec 3</dev/ttyACM0                     #REDIRECT SERIAL OUTPUT TO FD 3
cat <&3 > set-time.log &                #REDIRECT SERIAL OUTPUT TO FILE
PID=$!                                  #SAVE PID TO KILL CAT
# echo an initial something to the serial port to get past the
# "Press any key to enter REPL" prompt
echo -e "\r" > /dev/ttyACM0
while read line
do
  echo -e "$line\r" > /dev/ttyACM0
  echo -n "."
  sleep 0.5s
done <<EOF
import board
import busio
import time
import adafruit_ds3231
i2c.deinit()
i2c = busio.I2C(board.GP1,board.GP0)
ds3231 = adafruit_ds3231.DS3231(i2c)
current = ds3231.datetime
print('The RTC time is: {}-{}-{} {:02}:{:02}:{:02}'.format(current.tm_mday, current.tm_mon, current.tm_year, current.tm_hour, current.tm_min, current.tm_sec))
EOF

# The easiest way to set the time using the limited time commands in CircuitPython
# is to send the seconds since the Unix Epoch (1st Jan 1970). This will set the
# clock to UTC +00:00, so won't include any daylight savings time
seconds=$(date "+%s")

while read line
do
  echo -e "$line\r" > /dev/ttyACM0
  echo -n "."
  sleep 0.5s
done <<EOF
ds3231.datetime = time.localtime($seconds)
updated = ds3231.datetime
print('The RTC time is now: {}-{}-{} {:02}:{:02}:{:02}'.format(updated.tm_mday, updated.tm_mon, updated.tm_year, updated.tm_hour, updated.tm_min, updated.tm_sec))
EOF

kill $PID                             #KILL CAT PROCESS
wait $PID 2>/dev/null                 #SUPRESS "Terminated" output

exec 3<&-                               #FREE FD 3
cat set-time.log                    #DUMP CAPTURED DATA
