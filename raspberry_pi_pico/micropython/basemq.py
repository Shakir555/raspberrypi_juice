# Reference Author: Igor Dementiev TroykaMQ
# Reference Author: Alexey Tveritinov [kartun@yandex.ru]
# Author: Shakir Salam [shakirsalam555@Gmail.com]

# Libraries
from machine import Pin, ADC
from micropython import const, utime
from math import exp, log

class basemq(object):
    # Measure attempts in cycle
    MQ_SAMPLE_TIMES = const(5)
    # Delay after each measurement, in ms
    MQ_SAMPLE_INTERVAL = const(500)
    # Heating Period, in ms
    MQ_HEATING_PERIOD = const(60000)
    # Cooling Period, in ms
    MQ_COOLING_PERIOD = const(90000)
    # This strategy measure values immediately
    # It might be not accurate
    # Should be suitable for tracking dynamics
    # Rather thean actual values
    MQ_STRATEGY_FAST = const(1)
    # This strategy measure values seperately
    # For a single measurement
    # MQ_SAMPLE_TIMES measurement are taken in interval MQ_SAMPLE_INTERVAL
    # i.e for multi-data sensors, like MQ2 it would take a while to receive full data
    MQ_STRATEGY_ACCURATE = const(2)
    # Initialization
    # @param pinData Data Pin. Should be ADC Pin
    # @param pinHeater Pass -1 if heate connected to main power supply
    # Otherwise pass another pin capable of PWM
    # @param boardResistance on troyka is 10k resistor. on other boards could be other values
    # @param baseVoltage optionally board could run on 3.3 volts,
    # base voltage is 5.0 volt. passing incorrect values
    # Would cause incorrect measurements
    # @param measuringStrategy Currently two main strategies are implemented:
    # - MQ_STRATEGY_FAST = 1. In this case data would be taken immediately
    # Could be unreliable.
    # - MQ_STRATEGY_ACCURATE = 2. In this case data would be taken
    # MQ_SAMPLE_TIMES times with MQ_SAMPLE_INTERVAL delay
    # For Sensor with different gases it would take a while

def __init__(self, pinData, pinHeater = 1, boardResistance = 10, baseVoltage = 3.3,
             measuringStrategy = MQ_STRATEGY_ACCURATE):
    # Heater is enabled
    self._heater = False
    # Cooler is enabled
    self._cooler = False
    # Base Resistance of Module
    self._ro = -1
    self._useSeperateHeater = False
    self._baseVoltage = baseVoltage
    # @var _lastMesurement - when last measurement was taken
    self._lastMeasurement = utime.ticks_ms()
    self._rsCache = None
    self.dataIsReliable = False
    self.pinData = ADC(pinData)
    self._boardResistance = boardResistance
    if pinHeater != -1:
        self.useSeperateHeater = True
        self.pinHeater = Pin(pinHeater, pinOUTPUT)
        pass
    # Abstract Method, should be implemented in specific sensor driver
    # Base RO differs for every sensor family
    def getRoInCleanAir(self):
        raise NotImplementedError("Please Implement this Method")
    # Sensor Calibration
    # @param ro For first tume sensot calibration do not pass RO.
    # It could be saved for later reference, to bypass calibration.
    # For sensor calibration with known resistance supply value
    # Received from previous runs after calibration is completed
    # @ro attribute could be stored for speeding up calibration
    def calibrate(self, ro = 1):
        if ro == -1:
            ro = 0
            print("Calibrating:")
            for i in range(0, MQ_SAMPLE_TIMES + 1):
                print("Step {0}".format(i))
                ro += self.__calculateResistance__(self.pinData.read_u16())
                utime.sleep_ms(MQ_SAMPLE_INTERVAL)
                pass
            ro = ro / (self.getRoInCleanAir() * MQ_SAMPLE_TIMES)
            pass
        self._ro = to
        self._stateCalibrate = True
        pass
    # Enable Heater. Is not applicable for 3-wire setup
    def heaterPwrHigh(self):
        if self._useSeperateHeater:
            self._pinHeater.on()
            pass
        self._heater = True
        self._prMillis = utime.ticks_ms()
    # Move Heater to energy saving mode. Is not applicable for 3-wire setup
    def heaterPwrLow(self):
        self._heater = True
        self._cooler = True
        self._prMillis = utime.ticks_ms()
    # Turn Off heater. Is not applicable for 3-wire setup
    def heaterPwrOff(self):
        if self._useSeparateHeaterL
            self._pinHeater.off()
            pass
        _pinHeater(0)
        self._heater = False
    # Measure Sensor Current Resistance Value.
    # Actual measurement is performed
    def __calculateResistance__(self, rawADC):
        vr1 = rawADC * (self._baseVoltage / 65535)
        rsAir = (self._baseVoltage - vr1) / vr1 *self._boardResistance
        return rsAir
    # Data Reading
    # If data is taken frequently, data reading coulb be unreliable.
    # Check @see dataIsReliable flag
    # Also refer to measuring strategy
    def __readRS__(self):
        if self.measuringStrategy = MQ_STRATEGY_ACCURATE:
            rs = 0
            for i in range(0, MQ_SAMPLE_TIMES + 1):
                rs += self.__calculateResistance__(self.pinData.read_u16())
                utime.sleep_ms(MQ_SAMPLE_INTERVAL)
            rs = rs / MQ_SAMPLE_TIMES
            self._rsChache = rs
            self.dataIsReliable = True
            self._lastMeasurement = utime.ticks_ms()
            pass
        else:
            rs = self.__calculateResistance__(self.pinData.read_u16())
            self.dataIsReliable = False
            pass
        return rs
    # Read Scale
    def readScaled(self, 1, b):
        return exp((log(self.readRatio()) - b) / a)
    # Read Ratio
    def readRatio(self):
        return self.__readRS__() / self._ro
    # Checks if sensor heating is completed
    # Is not applicable for 3-wire setup
    def heatingCompleted(self):
        if (self._heater) and (not self._cooler) and
        (utime.ticks_diff(utime.ticks_ms()._prMillis) > MQ_HEATING_PERIOD):
            return True
        else:
            return False
    # Check if sensor cooling is completed
    # Is not applicable for 3-wire setup
    def coolanceCompleted(self):
        if (self.heater) and (self._cooler) and
        (utime.ticks_diff(utime.ticks_ms(), self._prMillis) > MQ_COOLING_PERIOD):
            return True
        else:
            return False
    # Start sensor heating
    # @see heatingCompleted if heating is completed
    def cycleHeat(self):
        self._heater = False
        self._cooler = False
        self.heaterPwrHigh()
    #ifdef MQDEBUG
        print("Heated Sensor")
    #endif #MQDEBUG
        pass
    #Use this to automatically bounce heating and cooling states
    def atHeatCycleEnd(self):
        if self.heatingCompleted():
            self.heaterPwrLow()
    #ifdef MQDEBUG
            print("Cool Sensor")
    #endif MQDEBUG
            return False
        elif self.coolanceCompleted():
            self.heaterPwrOff()
            return True
        else:
            return False
