from machine import Pin, I2C

# RV3028 default address.
RV3028_I2CADDR = 0x52

# RV3208 Registers
SECONDS = 0x00  # count of seconds, in 2 BCD digits. Values from 00 to 59.
MINUTES = 0x01  # count of minutes, in 2 BCD digits. Values from 00 to 59.
HOURS   = 0x02  # count of hours, in 2 BCD digits. Values from 00 to 12, or 00 to 24. 
WEEKDAY = 0x03
DATE    = 0x04
MONTH   = 0x05
YEAR    = 0x06
MINUTES_ALARM = 0x07
HOURS_ALARM   = 0x08
WEEKDAY_DATE_ALARM = 0x09
TIMER_VALUE_0 = 0x0A
TIMER_VALUE_1 = 0x0B
TIMER_STATUS_0 = 0x0C
TIMER_STATUS_1 = 0x0D
STATUS = 0x0E
CONTROL_1 = 0x0F
CONTROL_2 = 0x10
GP_BITS = 0x11
CLOCK_INT_MASK = 0x12
EVENT_CONTROL = 0x13
COUNT_TS = 0x14
SECONDS_TS = 0x15
MINUTES_TS = 0x16
HOURS_TS = 0x17
DATE_TS = 0x18
MONTH_TS = 0x19
YEAR_TS = 0x1A
UNIX_TIME_0 = 0x1B
UNIX_TIME_1 = 0x1C
UNIX_TIME_2 = 0x1D
UNIX_TIME_3 = 0x1E
USER_RAM_1 = 0x1F
USER_RAM_2 = 0x20
PASSWORD_0 = 0x21
PASSWORD_1 = 0x22
PASSWORD_2 = 0x23
PASSWORD_3 = 0x24
EE_ADDRESS = 0x25
EE_DATA = 0x26
EE_COMMAND = 0x27
ID = 0x28
RESERVED_1 = 0x29
RESERVED_2 = 0x2A
RESERVED_3 = 0x2B
RESERVED_4 = 0x2C
RESERVED_5 = 0x2D
RESERVED_6 = 0x2E
RESERVED_7 = 0x2F
EEPROM_PW_ENABLE = 0x30
EEPROM_PASSWORD_0 = 0x31
EEPROM_PASSWORD_1 = 0x32
EEPROM_PASSWORD_2 = 0x33
EEPROM_PASSWORD_3 = 0x34
EEPROM_CLKOUT = 0x35
EEPROM_OFFSET = 0x36
EEPROM_BACKUP = 0x37
RESERVED_8 = 0x38
RESERVED_9 = 0x39
RESERVED_A = 0x3B
RESERVED_C = 0x3C
RESERVED_D = 0x3D
RESERVED_E = 0x3E
RESERVED_F = 0x3F

# 0x02 HOURS BIT FUNCTIONS
HRS_AM_PM = 0b00100000

# 0x10 CONTROL_2 BIT FUNCTIONS
TSE       = 0b10000000
CLKIE     = 0b01000000
UIE       = 0b00100000
TIE       = 0b00010000
AIE       = 0b00001000
EIE       = 0b00000100
HR_12_24  = 0b00000010
RESET     = 0b00000001

# 0x37 EEPROM BACKUP BSM MODES
RTC_BSM_DEF = 0b00000000
RTC_BSM_DSM = 0b00000100
RTC_BSM_OFF = 0b00001000
RTC_BSM_LSM = 0b00001100

months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

months_long = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

weekday_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

weekday_long = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

date_ordinal = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
                "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
                "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", "30th",
                "31st"]

weekday_values = {"mon": 0,
                  "tue": 1,
                  "wed": 2,
                  "thu": 3,
                  "fri": 4,
                  "sat": 5,
                  "sun": 6
                  }

class RV3028:

    def __init__(self,
                 address = RV3028_I2CADDR,
                 i2c = None,
                 rtc_bsm=None,
                 **kwargs):
        """
        Args:
        address : Physical I2C address of device
        i2c:      An i2c object for the chosen I2C bus
        rtc_bsm:  Backup Switchover Mode
        """

        self.address = address
        if i2c is None:
            raise ValueError('An I2C object is required.')
        if rtc_bsm is None:
            raise ValueError('Backup Switchover Mode is required (DEF/DSM/OFF/LSM).')
        self.i2c = i2c
        self.rtc_bsm =rtc_bsm
        
        # Set Backup Switching Mode
        if rtc_bsm == "DEF":
            rtc_bsm_mode = RTC_BSM_DEF
        elif rtc_bsm == "DSM":
            rtc_bsm_mode = RTC_BSM_DSM
        elif rtc_bsm == "OFF":
            rtc_bsm_mode = RTC_BSM_OFF
        elif rtc_bsm == "LSM":
            rtc_bsm_mode = RTC_BSM_LSM
        else:
            raise ValueError('Backup Switchover Mode value is invalid (DEF/DSM/OFF/LSM).')
            
        _ = self._get(self.i2c, EEPROM_BACKUP, 1)
        rtc_eeprom_backup = (int.from_bytes(_, "big") | rtc_bsm_mode).to_bytes(1, "big")
        self._set(self.i2c, EEPROM_BACKUP, rtc_eeprom_backup)
        _ = self._get(self.i2c, EEPROM_BACKUP, 1)
        # print("EEPROM BACKUP {:b}".format(int.from_bytes(_, "big")))

    def get_year(self):
        return self._decode(self._get(self.i2c, YEAR, 1)) + 2000


    def get_month(self, month_type=False):
        if month_type == "long":
            return months_long[self._decode(self._get(self.i2c, MONTH, 1)) - 1]
        elif month_type == "short":
            return months_short[self._decode(self._get(self.i2c, MONTH, 1)) - 1]
        else:
            return self._decode(self._get(self.i2c, MONTH, 1))
            
    def get_date(self, date_type=False):
        if date_type == "ordinal":
            return date_ordinal[self._decode(self._get(self.i2c, DATE, 1)) - 1]
        else:
            return self._decode(self._get(self.i2c, DATE, 1))


    def get_weekday(self, day_type=False):
        if day_type == "long":
            return weekday_long[self._decode(self._get(self.i2c, WEEKDAY, 1))]
        elif day_type == "short":
            return weekday_short[self._decode(self._get(self.i2c, WEEKDAY, 1))]
        else:
            return self._decode(self._get(self.i2c, WEEKDAY, 1))
        

    def get_12_hr_clk(self):
        _ = self._get(self.i2c, CONTROL_2, 1)
        if int.from_bytes(_, "big") & HR_12_24:
            return(True)
        else:
            return(False)
    
    def get_am(self):
        _ = self._get(self.i2c, HOURS, 1)
        if int.from_bytes(_, "big") & HRS_AM_PM:
            return True
        else:
            return False

    def get_hours(self):
        if self.get_12_hr_clk():
            _ = self._get(self.i2c, HOURS, 1)
            upper = ((int.from_bytes(_, "big") & 0xD0) >> 4) * 10
            lower = (int.from_bytes(_, "big") & 0x0F)
            return(upper + lower)
        else:
            return self._decode(self._get(self.i2c, HOURS, 1))

    def get_minutes(self):
        return self._decode(self._get(self.i2c, MINUTES, 1))


    def get_seconds(self):
        return self._decode(self._get(self.i2c, SECONDS, 1))


    def get_rtc_time(self):
        hours = self.get_hours()
        minutes = self.get_minutes()
        seconds = self.get_seconds()
        return (hours, minutes, seconds)


    def get_rtc_date(self, day_type=False, date_type=False, month_type=False):
        weekday = self.get_weekday(day_type)
        date = self.get_date(date_type)
        month = self.get_month(month_type)
        year = self.get_year()
        return (weekday, date, month, year)


    def get_rtc_date_time(self, day_type=False, date_type=False, month_type=False):
        hours = self.get_hours()
        minutes = self.get_minutes()
        seconds = self.get_seconds()
        weekday = self.get_weekday(day_type)
        date = self.get_date(date_type)
        month = self.get_month(month_type)
        year = self.get_year()
        if self.get_12_hr_clk():
            if self.get_am():
                am_pm = "am"
            else:
                am_pm = "pm"
        else:
            am_pm = None

        return (year, month, date, weekday, hours, minutes, seconds, am_pm)
        
    def set_12_hr_clk(self, status=False):
        _ = self._get(self.i2c, CONTROL_2, 1)
        if status is True:
            rtc_control_2 = (int.from_bytes(_, "big") | HR_12_24).to_bytes(1, "big")
        else:
            rtc_control_2 = (int.from_bytes(_, "big") & ~HR_12_24).to_bytes(1, "big")
        self._set(self.i2c, CONTROL_2, rtc_control_2)
        _ = self._get(self.i2c, CONTROL_2, 1)
    
    def set_weekday(self, weekday):
        if weekday == "mon" or weekday == "tue" or weekday == "wed" or weekday == "thu" or weekday == "fri" or weekday == "sat" or weekday == "sun":
            self._set(self.i2c, WEEKDAY, (weekday_values[weekday]).to_bytes(1, "big"))
        else:
            raise ValueError('Weekday value can only be one of mon, tue, wed, thu, fri, sat, sun')

    def set_date(self, date):
        if date >= 1 and date <= 31:
            self._set(self.i2c, DATE, self._encode(date))
        else:
            raise ValueError('Date value must be between 1 and 31')

    def set_month(self, month):
        if month >= 1 and month <= 12:
            self._set(self.i2c, MONTH, self._encode(month))
        else:
            raise ValueError('Month value must be between 1 and 12')

    def set_year(self, year):
        if year >= 2000 and year <= 2099:
            self._set(self.i2c, YEAR, self._encode(year - 2000))
        else:
            raise ValueError('Year value must be between 2000 and 2099')

    def set_hours(self, hours, hr_12_24=None, am_pm=None):
        if hr_12_24 is None or hr_12_24 == 24:
            self.set_12_hr_clk(False)
            if hours >= 0 and hours <= 23:
                self._set(self.i2c, HOURS, self._encode(hours))
            else:
                raise ValueError('Hours must be between 0 and 23 for 24hr clock')
        elif hr_12_24 == 12:
            self.set_12_hr_clk(True)
            if hours < 1 or hours > 12:
                raise ValueError('Hours must be between 1 and 12 for 12hr clock')
            elif am_pm == "am":
                self._set(self.i2c, HOURS, self._encode_12hr(hours, True))
            elif am_pm == "pm":
                self._set(self.i2c, HOURS, self._encode_12hr(hours, False))
            else:
                raise ValueError('am_pm must be set to either am or pm for 12hr clock')
        else:
            raise ValueError('type value must be None, 12 or 24')

    def set_minutes(self, minutes):
        if minutes >= 0 and minutes <= 59:
            self._set(self.i2c, MINUTES, self._encode(minutes))
        else:
            raise ValueError('Minutes value must be between 0 and 59')

    def set_seconds(self, seconds):
        if seconds >= 0 and seconds <= 59:
            self._set(self.i2c, SECONDS, self._encode(seconds))
        else:
            raise ValueError('Seconds value must be between 0 and 59')

    def set_rtc_date(self, current_date):  # current_date is a tuple (four-digit year, two-digit month, two-digit day, "weekday")
        if len(current_date) == 4:
            year, month, date, weekday = current_date
            if weekday == "mon" or weekday == "tue" or weekday == "wed" or weekday == "thu" or weekday == "fri" or weekday == "sat" or weekday == "sun":
                self.set_weekday(weekday)
            else:
                raise ValueError('Weekday value can only be one of None, mon, tue, wed, thu, fri, sat, sun')
        elif len(current_date) == 3:
            year, month, date = current_date
        else:
            raise ValueError('current_date must be a tuple with 3 or 4 values')
        
        self.set_year(year)
        self.set_month(month)
        self.set_date(date)

    def set_rtc_time(self, current_time): # time is a tuple (hours, minutes, seconds, 24/12, "am"/"pm")
        if len(current_time) == 3:
            hours, minutes, seconds = current_time
            hr_12_24 = None
            am_pm = None
        elif len(current_time) == 5:
            hours, minutes, seconds, hr_12_24, am_pm = current_time
        else:
            raise ValueError('Current_time is a tuple and must have 3 or 5 values')
        
        self.set_hours(hours, hr_12_24, am_pm)
        self.set_minutes(minutes)
        self.set_seconds(seconds)

    def set_rtc_date_time(self, current_date_time):
        # current_date_time is a tuple with 6, 7 or 9 values
        # (four-digit year, two-digit month, two-digit day, hours, minutes, seconds)
        # (four-digit year, two-digit month, two-digit day, hours, minutes, seconds, "weekday")
        # (four-digit year, two-digit month, two-digit day, hours, minutes, seconds, "weekday", 24/12, "am"/"pm")
        weekday = None
        hr_12_24 = None
        am_pm = None
        if len(current_date_time) == 6:
            year, month, date, hours, minutes, seconds = current_date_time
        elif len(current_date_time) == 7:
            year, month, date, hours, minutes, seconds, weekday = current_date_time
        elif len(current_date_time) == 9:
            year, month, date, hours, minutes, seconds, weekday, hr_12_24, am_pm = current_date_time
        else:
            raise ValueError('Current_date_time is a tuple and must have 6, 7 or 9 values')

        if weekday is not None:
            self.set_weekday(weekday)

        self.set_year(year)
        self.set_month(month)
        self.set_date(date)
        self.set_hours(hours, hr_12_24, am_pm)
        self.set_minutes(minutes)
        self.set_seconds(seconds)

    def _set(self, i2c, register, byte_value):
        self.i2c.writeto_mem(self.address, register, byte_value)

    def _get(self, i2c, register, byte_length):
        return i2c.readfrom_mem(self.address, register, byte_length)
            
    def _decode(self, value):
        upper = ((int.from_bytes(value, "big") & 0xF0) >> 4) * 10
        lower = (int.from_bytes(value, "big") & 0x0F)
        return(upper + lower)
    
    def _encode(self, value):
        upper = (int(value / 10)) << 4
        lower = value % 10
        return (upper | lower).to_bytes(1, "big")

    def _encode_12hr(self, value, am):
        upper = (int(value / 10)) << 4
        lower = value % 10
        if am:
            return (upper | lower | HRS_AM_PM).to_bytes(1, "big")
        else:
            return (upper | lower & ~HRS_AM_PM).to_bytes(1, "big")

def rtc_test():
    i2c = machine.I2C(1, scl=Pin(27), sda=Pin(26), freq=100000)
    rtc = RV3028(0x52, i2c)
    print("{:02d}:{:02d}:{:02d} {} {} {} {}".format(rtc.get_hours(), rtc.get_minutes(), rtc.get_seconds(), rtc.get_weekday("long"), rtc.get_date("ordinal"), rtc.get_month("long"), rtc.get_year()))

    hours, minutes, seconds = rtc.get_rtc_time()
    print("{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))

    weekday, date, month, year = rtc.get_rtc_date()
    print("{:02d}/{:02d}/{:04d}".format(date, month, year))

    weekday, date, month, year, hours, minutes, seconds = rtc.get_rtc_date_time(day_type="long")
    print("{:02d}:{:02d}:{:02d} {} {:02d}/{:02d}/{:04d}".format(hours, minutes, seconds, weekday, date, month, year))
    
if __name__ == "__main__":
    rtc_test()
