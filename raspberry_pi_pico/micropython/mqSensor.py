# Reference Author: Igor Dementiev TroykaMQ
# Reference Author: Alexey Tveritinov [kartun@yandex.ru]
# Author: Shakir Salam [shakirsalam555@Gmail.com]

# Libraries
from mq2Sensor import MQ2SENSOR
import utime

pin = 26
sensor = MQ2(pinData = pin, baseVoltage = 3.3)

print("Calibrating")
sensor.calibrate()
print("Calibration Completed")
print("Base Resistance:{0}".format(sensor._ro))
      
while True:
	print("Smoke: {:.1f}".format(sensor.readSmoke())+" - ", end="")
	print("LPG: {:.1f}".format(sensor.readLPG())+" - ", end="")
	print("Methane: {:.1f}".format(sensor.readMethane())+" - ", end="")
	print("Hydrogen: {:.1f}".format(sensor.readHydrogen()))
	utime.sleep(0.5)
