import pyvisa as visa
import time
import re

inst = None


class Keithley2001:
    inst = None

    measurementFunction = ['VOLT:AC', 'VOLT:DC', 'RES', 'FRES', 'CURR:AC', 'CURR:DC', 'FREQ', 'TEMP']
    triggerSources = ['HOLD', 'IMM','TIM', 'MAN', 'BUS', 'TLIN', 'EXT']

    # general

    def __init__(self, port, resource_manager=visa.ResourceManager()):
        self.inst = resource_manager.open_resource(port)
        self.inst.write_termination = "\n"
        self.inst.read_termination = "\n"
        self.inst.write("*cls")


    def get_ID(self):
        print(self.inst.query("*IDN?"))

    def set_mode(self, mode):
        cmd = ":sens:func '{}'".format(mode)
        self.inst.write(cmd)

    # Triggering

    def set_trigger_source(self, source ):
        """

        :param source:
        :return: None
        """
        if source not in self.triggerSources:
            print("Error, trigger source is not valid")
        else:
            cmd = ":TRIG:SOUR {}".format(source)
            # cmd = ":trig:sour ext\n"
            self.inst.write(cmd)

    def set_measurement_function(self, function):
        if function not in self.measurementFunction:
            print("Error, measurement funciton is not valid")
        else:
            cmd = f":func '{function}'"
            self.inst.write(cmd)

    def set_reference(self, function, enabled , value = None ):
        """
        enables or disables the reference function.
        Attention: Does not change or measure the reference value. This needs to be done manually
        :param function:
        :param enabled:
        :param value: Value or MIN , DEF (=0 ) or MAX , range depending on function, see in manual 4.19.9
        :return:
        """
        cmd = f":{function}:ref:stat {int(enabled)}"
        self.inst.write(cmd)
        if value is not None:
            cmd = f":{function}:ref {value}"
            self.inst.write(cmd)



    def trigger_measurement(self):
        #TODO might be wrong implemented
        cmd = ":INIT:IMM"
        self.inst.write(cmd)

    def trigger_measurement_continously(self, state):
        cmd = ":INIT:CONT {}".format(int(state))
        self.inst.write(":CONT")
        self.inst.write(cmd)
        time.sleep(1)

    # get readings
    def get_reading(self):
        return self.get_reading_from_raw(self.get_reading_raw())

    def get_fresh(self):
        """
        See Operator manual 4.19.4
        :return:
        """
        cmd = ":data:fresh?"
        return self.inst.query(cmd)

    def is_available(self):
        """
        reads the status register of the Multimeter.
        Returns True if a new reading is available.
        After readout the value of the register is set to false
        :return: True or False
        """
        return (int(self.inst.query(":stat:meas:event?")) & (1 << 5))


    def get_reading_from_raw(self, text):
        exp = "([+-]?[0-9]+[.]*[0-9]*E[+-][0-9]*)"
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

    # gpio interface

    def gpio_read_input(self):
        cmd = ":sens2:ttl:data?"
        return self.inst.query(cmd)

    def gpio_write_output(self, output, state):
        cmd = ":SOUR:TTL{} {}".format(int(output), int(state))
        self.inst.write(cmd)

    # misc

    def displaytext(self, text, row):
        self.inst.write(":DISP:WIND{}:TEXT:DATA '{}'".format(str(row), text))
        self.inst.write(":DISP:WIND{}:TEXT:State 1".format(str(row), text))
