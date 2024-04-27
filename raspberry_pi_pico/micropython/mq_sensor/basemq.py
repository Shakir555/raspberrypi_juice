# Reference Author: Igor Dementiev TroykaMQ
# Reference Author: Alexay Tveritinov [kartun@yandex.ru]
# Author: Shakir Salam [shakirsalam555@Gmail.com]

# Libraries
from machine import Pin, ADC
from micropython import const
import utime
from math import exp, log

# BaseMQ
class BaseMQ(object):
    # Measure attempts in cycle
    MQ_SAMPLE_TIMES = const(5)
    # Delay after each measurement, in ms
    MQ_SAMPLE_INTERVAL = const(500)
    # Heating Period, in ms
    MQ_HEATING_PERIOD = const(60000)
    # Cooling Period, in ms
    MQ_COOLING_PERIOD = const(90000)
    # This strategy measure values immediately, so it might be
    # inaccurate. Should be suitable for tracking dynamics,
    # rather than actual values
    STRATEGY_FAST = const(1)
    # This strategy measure values immediately,
    # For a single measurement
    STRATEGY_ACCURATE = const(2)
    
    # Initialization
    # @param pinData Data Pin. Should be ADC Pin
    # @param PinHeater Pass -1 if heater is connected to main power supply
    # Otherwise pass another pin capable of PWM.
    # @param boardResistance on troyka modules there is 10K resistor,
    # on other boards could be other values
    # @param baseVoltage optionally board could run on 3.3 volts,
    # Base Voltage 5.0 Volts. Passing incorrect values
    # Would cause incorrect measurements
    # @param measuringStrategy currently two main strategies are implemented:
    # STRATEGY_FAST = 1. In this case data would be taken immediately.
    # Could be unreliable.
    # STRATEGY_ACCURATE = 2. In this case data would be taken
    # MQ_SAMPLE_TIMES times with MQ_SAMPLE_INTERVAL delay
    # For sensor with different gases would be take a while
    def __init__(self, pinData, pinHeater = -1, boardResistance = 10,
                 baseVoltage = 3.3, measuringStrategy = STRATEGY_ACCURATE):
        # Heater is enabled
        self._heater = False
        # Cooler is enabled
        self._cooler = False
        # Base Resistance of module
        self._ro = -1
        self._useSeperateVoltage = False
        self._baseVoltage = baseVoltage
        # @var _lastMeasurement - when last measurement was taken
        self._lastMeasurement = utime.ticks_ms()
        self._rsCache = None
        self.dataIsRelable = False
        self.pinData = ADC(pinData)
        self.measuringStrategy = measuringStrategy
        self._boardResistance = boardResistance
        if pinHeater != -1:
            self.useSeperateHeater = True
            self.pinHeater = Pin(pinHeater, pin.OUTPUT)
            pass
        
    # Abstract method, should be implemented in specific sensor driver.
    # Base RO differs for every sensor family
    def getRoInCleanAir(self):
        raise NotImplementedError("Please Implement this method")

    # Sensor calibration
    # @param ro For first time sensor calibration do not pass RO. It could be saved for
    # later reference, to bypass calibration. For sensor calibration with known resistance supply value 
    # received from pervious runs After calibration is completed @see _ro attribute could be stored for 
    # speeding up calibration
    def calibrate(self, ro=-1):
        if ro == -1:
            ro = 0
            print("Calibrating:")
            for i in range(0,MQ_SAMPLE_TIMES + 1):        
                print("Step {0}".format(i))
                ro += self.__calculateResistance__(self.pinData.read_u16())
                utime.sleep_ms(MQ_SAMPLE_INTERVAL)
                pass            
            ro = ro/(self.getRoInCleanAir() * MQ_SAMPLE_TIMES )
            pass
        self._ro = ro
        self._stateCalibrate = True    
        pass

    # Enable heater. Is not applicable for 3-wire setup
    def heaterPwrHigh(self):
        if self._useSeparateHeater:
            self._pinHeater.on()
            pass
        self._heater = True
        self._prMillis = utime.ticks_ms()

    # Move heater to energy saving mode. Is not applicable for 3-wire setup
    def heaterPwrLow(self):
        self._heater = True
        self._cooler = True
        self._prMillis = utime.ticks_ms()

    # Turn off heater. Is not applicable for 3-wire setup
    def heaterPwrOff(self):
        if self._useSeparateHeater:
            self._pinHeater.off()
            pass
        _pinHeater(0)
        self._heater = False
        
    # Measure sensor current resistance value, ere actual measurement is performed
    def __calculateResistance__(self, rawAdc):
        vrl = rawAdc*(self._baseVoltage / 65535)
        rsAir = (self._baseVoltage - vrl)/vrl*self._boardResistance
        return rsAir
    
    # Data reading     
    # If data is taken frequently, data reading could be unreliable. Check @see dataIsReliable flag
    # Also refer to measuring strategy
    def __readRs__(self):
        if self.measuringStrategy == STRATEGY_ACCURATE :            
                rs = 0
                for i in range(0, MQ_SAMPLE_TIMES + 1): 
                    rs += self.__calculateResistance__(self.pinData.read_u16())
                    utime.sleep_ms(MQ_SAMPLE_INTERVAL)

                rs = rs/MQ_SAMPLE_TIMES
                self._rsCache = rs
                self.dataIsReliable = True
                self._lastMesurement = utime.ticks_ms()                            
                pass
        else:
            rs = self.__calculateResistance__(self.pinData.read_u16())
            self.dataIsReliable = False
            pass
        return rs

    def readScaled(self, a, b):        
        return exp((log(self.readRatio())-b)/a)

    def readRatio(self):
        return self.__readRs__()/self._ro

    # Checks if sensor heating is completed. Is not applicable for 3-wire setup
    def heatingCompleted(self):
        if (self._heater) and (not self._cooler) and (utime.ticks_diff(utime.ticks_ms(),self._prMillis) > MQ_HEATING_PERIOD):
            return True
        else:
            return False

    # Checks if sensor cooling is completed. Is not applicable for 3-wire setup 
    def coolanceCompleted(self):
        if (self._heater) and (self._cooler) and (utime.ticks_diff(utime.ticks_ms(), self._prMillis) > MQ_COOLING_PERIOD):
            return True
        else:
            return False

    # Starts sensor heating. @see heatingCompleted if heating is completed
    def cycleHeat(self):
        self._heater = False
        self._cooler = False
        self.heaterPwrHigh()
    #ifdef MQDEBUG
        print("Heated sensor")
    #endif #MQDEBUG
        pass

    # Use this to automatically bounce heating and cooling states
    def atHeatCycleEnd(self):
        if self.heatingCompleted():
            self.heaterPwrLow()
    #ifdef MQDEBUG
            print("Cool sensor")
    #endif #MQDEBUG
            return False
        elif self.coolanceCompleted():
            self.heaterPwrOff()
            return True
        else:
            return False
