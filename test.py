import Keithley2001
import time

port = "GPIB0::12::INSTR"

mult = Keithley2001.Keithley2001(port)

#mult.set_mode ("VOLT:DC")
#volt = mult.get_voltage()
# print(volt)


mult.set_trigger_source("EXT")

while True:
    available = mult.is_available()
    if available:
        print("available")
        # print(mult.get_fresh())
        print(mult.get_reading_from_raw(mult.get_reading_raw()))
        time.sleep(0.1)
