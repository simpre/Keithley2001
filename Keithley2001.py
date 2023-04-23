import pyvisa as visa
import time
import re

inst = None


class Keithley2001:
    inst = None

    measurementModes = ['VOLT:AC', 'VOLT:DC', 'RES', 'FRES', 'CURR:AC', 'CURR:DC', 'FREQ', 'TEMP']

    def __init__(self, port, resource_manager=visa.ResourceManager()):
        self.inst = resource_manager.open_resource(port)
        self.inst.write("*cls")
        self.inst.write_termination = "\n"
        self.inst.read_termination = "\n"

    def get_ID(self):
        print(self.inst.query("*IDN?"))

    def set_mode(self, mode):
        cmd = ":sens:func '{}'".format(mode)
        self.inst.write(cmd)

    def trigger_measurement(self):
        cmd = ":INIT:IMM"
        self.inst.write(cmd)

    def trigger_measurement_continously(self, state):
        cmd = ":INIT:CONT {}".format(int(state))
        self.inst.write(cmd)
        time.sleep(1)

    def get_reading_from_raw(self, text):
        exp = "([0-9]*[.]*[0-9]*E[+-][0-9]*)"
        match = re.search(exp, text)
        # If a match is found, extract the captured group
        if match:
            return (float(match.group(1)))
        else:
            print("Invalid values" + text)

    def get_reading_raw(self):
        cmd = ":data?"
        return self.inst.query(cmd)

    def get_voltage(self, ac=False, channel=0):
        if channel != 0:
            # TODO Instead of open all, check whether the correct channel is already selected.
            self.inst.write(":ROUTE:OPEN ALL", )
            # time.sleep(0.5)
            self.inst.write(":ROUTE:CLOSE (@{})".format(str(channel)))
            # time.sleep(0.5)
        time.sleep(8)
        return self.get_reading_from_raw(self.get_reading_raw())

    def displaytext(self, text, row):
        self.inst.write(":DISP:WIND{}:TEXT:DATA '{}'".format(str(row), text))
        self.inst.write(":DISP:WIND{}:TEXT:State 1".format(str(row), text))
