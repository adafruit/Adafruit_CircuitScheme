import adafruit_si7021

def make_si7021(i2c_bus):
    return adafruit_si7021.SI7021(i2c_bus)

def si7021_relative_humidity(device):
    return device.relative_humidity

def si7021_temperature(device):
    return device.temperature

global_env.storage.update({
    'make-si7021':make_si7021,
    'si7021-relative-humidity':si7021_relative_humidity,
    'si7021-temperature':si7021_temperature
    })
