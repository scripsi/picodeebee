import board
import digitalio
import storage

logging_switch = digitalio.DigitalInOut(board.GP7)
logging_switch.direction = digitalio.Direction.INPUT
logging_switch.pull = digitalio.Pull.UP
print("logging:",logging_switch.value)

usb_readonly = not logging_switch.value

storage.remount("/", usb_readonly)
