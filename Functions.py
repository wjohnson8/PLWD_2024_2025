#Code snippet 1: Micropython Imports for Functions.py
from machine import I2C, Pin, SPI # I2C is used for communication via the ADS1115 ADC.Pin allows control of GPIO pins for input/output operations. SPI is used for communication with SPI-based temperature IC
import time # Time library is used for the time.sleep() function to generate delays when sending data
#from ads1x15 import ADS1115  # Import the ADS1115 driver library
import sys # Library used for command line arguments
import struct
import math
import rp2


#Code snippet 2: Global Variables and Pin Declerations in Functions.py
# Global variable for number of readings to take for 1550nm and 1200nm LED
LED_NUM_READINGS = 50
# Global variable for number of readings to take for no LED
NO_LED_NUM_READINGS = 20
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
channel=0
# Frequency for data collection (400kHz for fast mode I2C)
freq=400000
# temp read constants
beta = 3435   #thermistor constant in kelvin
r0 = 10000    #thermistor resistance constant
rext = 6800   #resistor value for temp IC's

# Define pins for LED
LED_1550_PIN = 14 # 1550nm LED enable pin 19 (GPIO 14)
LED_1200_PIN = 15 # 1200nm LED enable pin 20 (GPIO 15)

# spi setup for temperature control
# Define individual CS pins as constants
CS_1200NM = Pin(22, Pin.OUT)  # Chip select for 1200nm
CS_1550NM = Pin(17, Pin.OUT)  # Chip select for 1550nm
CS_PHOTODIODE_TEMP = Pin(20, Pin.OUT)  # Chip select for photodiode temp IC

# Define pins for the Motor
# DIR_PIN = 5   # Motor direction pin 7 (GPIO 5)
# STEP_PIN = 6  # Step size pin 9 (GPIO 6)
# ENABLE_PIN = 12  # Motor enable pin 16 (GPIO 12)
# RESET_PIN = 8 # Motor reset pin 11 (GPIO 8)
# SLEEP_PIN = 7 # Motor sleep pin 10 (GPIO 7)
# RESOLUTION_MS1 = 11 # Motor resolution 1 pin 15 (GPIO 11)
# RESOLUTION_MS2 = 10 # Motor resolution 2 pin 14 (GPIO 10)
# RESOLUTION_MS3 = 9  # Motor resolution 3 pin 12 (GPIO 9)

# Initialize GPIO pins (all outputs, controlled by Raspberry Pi Pico)
led_1550 = Pin (LED_1550_PIN, Pin.OUT)
led_1200 = Pin (LED_1200_PIN, Pin.OUT)
led_1550.value(0)
led_1200.value(0)
# Initialize SPI chip selects to high
CS_1200NM.value(1)
CS_1550NM.value(1)
CS_PHOTODIODE_TEMP.value(1)
# dir_pin = Pin(DIR_PIN, Pin.OUT)
# step_pin = Pin(STEP_PIN, Pin.OUT)
# enable_pin = Pin(ENABLE_PIN, Pin.OUT)
# reset_pin = Pin(RESET_PIN, Pin.OUT)
# sleep_pin = Pin(SLEEP_PIN, Pin.OUT)
# resolution_ms1_pin = Pin(RESOLUTION_MS1, Pin.OUT)
# resolution_ms2_pin = Pin(RESOLUTION_MS2, Pin.OUT)
# resolution_ms3_pin = Pin(RESOLUTION_MS3, Pin.OUT)



# Code snippet 3: Communication Protocol Setup for Functions.py
#I2C setup and driver functions
dev = I2C(1, freq=100000, scl=Pin(3), sda=Pin(2))
devices = dev.scan()
for device in devices: print(device)
address = 72
#initiallize SPI using the SPI import
spi = SPI(0,baudrate=100000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))  # Software SPI


# Code snippet 4: I2C Communication with ADS1115 ADC
def read_config():
    dev.writeto(address, bytearray([1]))
    result = dev.readfrom(address, 2)
    return result[0] << 8 | result[1]
def read_value(channel):
    # Input multiplexer configuration for single-ended channels
    mux = {
        0: 0b100,  # AINP = A0 (P), AINN = GND
        1: 0b101,  # AINP = A1 (P), AINN = GND
        2: 0b110,  # AINP = A2 (P), AINN = GND
        3: 0b111,  # AINP = A3 (P), AINN = GND
    }
    if channel not in mux:
        raise ValueError("Invalid channel. Must be 0, 1, 2, or 3.")
    dev.writeto(address, bytearray([0]))
    result = dev.readfrom(address, 2)
    config = read_config()
    config &= ~(7 << 12) & ~(7 << 9)
    config |= (mux[channel] << 12) | (1 << 9) | (1 << 15)
    config = [int(config >> i & 0xff) for i in (8, 0)]
    dev.writeto(address, bytearray([1] + config))
    return result[0] << 8 | result[1]
def val_to_voltage(val, max_val=26100, voltage_ref=3.3):
    return val / max_val * voltage_ref




#Code snippet 5: Collect Data Function in Functions.py
#Data collection test sequence for reading the 1550nm photodiode
def collectData(freq,channel):
    print("running")

    print("Flushing ADC registers...")
    time.sleep(1)  # Small delay to stabilize readings


    # Flush the ADC by taking a few dummy readings
    for _ in range(5):  # Take 5 dummy readings
        _ = read_value(channel)  # Read and discard
        time.sleep(0.01)  # Small delay to stabilize readings

    print("ADC registers flushed. Starting actual data collection...")

    # Create an empty list to store voltage values
    slaveData = []

    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):

        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)

        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))

        if i>3:
            #add voltage to array
            time.sleep(1/freq)
            slaveData.append(voltage)

    # Print the collected data
    print("1550 nm Data:", slaveData,"V")
    slaveDataAverage=sum(slaveData)/len(slaveData)

    return slaveData, slaveDataAverage





# Code snippet 6: Read Temperature Function for Functions.py
def readTemp(CS):
    '''
    returns the temperature reading from temp IC1(3400nm LED), temp IC2 (1500nm LED), or temp IC3 (photodiode)
    :param spi: SPI object initialized earlier.
    :param cs: chip select for temperature IC
    :return: digital temperature of selected sensor as a 32 bit float
    '''

    time.sleep_us(1)  # Small delay
    #print("Received Data:", ' '.join(f"0x{byte:02X}" for byte in temp_data))
    CS.value(0)  # Select device

    #spi.write(bytearray([0x00]))  # Some ICs require a read command first
    temp_data = spi.read(2)  # Read 2 bytes
    #print("Received Data:", ' '.join(f"0x{byte:02X}" for byte in temp_data))
    #print(f"Byte 1: 0x{temp_data[0]:02X}, Byte 2: 0x{temp_data[1]:02X}")

    CS.value(1)  # Deselect device

    # Convert bytes to 16-bit value
    temp_data_16bits = (temp_data[0] << 8) | temp_data[1]
    temp_data_16bits = temp_data_16bits >> 5  # Adjust bit alignment

    # Sign bit extension
    if temp_data_16bits & (1 << 9):
        temp_data_16bits -= 1 << 10

    # Convert to temperature
    normalized_voltage = ((temp_data_16bits * 0.010404)/8) + 0.174387
    #print(normalized_voltage)

    rtherm = ((1-normalized_voltage) * rext) / (normalized_voltage)
    tempK = 1 / ((1/298.15) +  (math.log(rtherm / r0)/beta ))
    tempC = tempK - 273.15


    return tempC



# Code Snippet 7: LED_control Function for Functions.py
def LED_control(led_id, on_off):
    '''
    Controls the on and off states of the 1550 and 1200 LEDs

    :param led_id: Defining the two different LEDs and 1550 and 1200
    :param on_off: On for true to ture on the LED and off for false to turn off the LED
    '''

    #Make the on_off as a bool
    state = bool(on_off)

    #Check which LED is going to be controlled
    if led_id == '1550':
        led_1550.value(state)
    elif led_id == '1200':
        led_1200.value(state)
    else:
        print("Undefined LED, use '1550' or either '1200'")



# Code Snippet 8: topLevelDataCollection for Final Deployment
def topLevelDataCollection(channel):

    # Create an empty list to store voltage values
    readingData = []
    # Create an empty list to store temperature reading values for LEDs
    ledTempData = []
    # Create an empty list to store temperature reading values for photodiode
    photoTempData = []
    # Create an empty list to store data collection mode. Either 1550, 1200, or both.
    modeLog = []

    #=============no LED Data Collection=============
    print("both LEDs off")

    print("Flushing ADC registers...")
    time.sleep(1)  # Small delay to stabilize readings
    # Flush the ADC by taking a few dummy readings
    for ii in range(5):  # Take 5 dummy readings
        ii = read_value(channel)  # Read and discard
    time.sleep(0.01)  # Small delay to stabilize readings
    print("ADC registers flushed. Starting actual data collection...")

    # Take readings and store them in the list
    for i in range(NO_LED_NUM_READINGS):
        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)
        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))

        #Add voltage to reading array
        time.sleep(1/freq)
        readingData.append(voltage)
        #Log the mode of operation in a parallel array
        modeLog.append("none")
        #Capture LED temperature reading
        ledTempData.append((readTemp(CS_1200NM)+readTemp(CS_1550NM))/2)
        #Capture photodiode temperature reading
        photoTempData.append(readTemp(CS_PHOTODIODE_TEMP))




    #=============1550 nm LED Data Collection=============
    print("1550 LED on")
    LED_control('1550', True)
    time.sleep(0.25)

    print("Flushing ADC registers...")
    time.sleep(1)  # Small delay to stabilize readings
    # Flush the ADC by taking a few dummy readings
    for ii in range(5):  # Take 5 dummy readings
        ii = read_value(channel)  # Read and discard
    time.sleep(0.01)  # Small delay to stabilize readings
    print("ADC registers flushed. Starting actual data collection...")

    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):
        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)
        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))

        #Add voltage to reading array
        time.sleep(1/freq)
        readingData.append(voltage)
        #Log the mode of operation in a parallel array
        modeLog.append("1550")
        #Capture LED temperature reading
        ledTempData.append(readTemp(CS_1550NM))
        #Capture photodiode temperature reading
        photoTempData.append(readTemp(CS_PHOTODIODE_TEMP))



    #=============1200 nm LED Data Collection=============
    print("1200 LED on")
    LED_control('1550', False)
    LED_control('1200', True)
    time.sleep(0.25)

    print("Flushing ADC registers...")
    time.sleep(1)  # Small delay to stabilize readings
    # Flush the ADC by taking a few dummy readings
    for ii in range(5):  # Take 5 dummy readings
        ii = read_value(channel)  # Read and discard
    time.sleep(0.01)  # Small delay to stabilize readings
    print("ADC registers flushed. Starting actual data collection...")

    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):
        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)
        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))

        #Add voltage to reading array
        time.sleep(1/freq)
        readingData.append(voltage)
        #Log the mode of operation in a parallel array
        modeLog.append("1200")
        #Capture temperature reading
        ledTempData.append(readTemp(CS_1200NM))
        #Capture photodiode temperature reading
        photoTempData.append(readTemp(CS_PHOTODIODE_TEMP))



    #=============Both LEDs Data Collection=============
    print("both LEDs on")
    LED_control('1200', True)
    LED_control('1550', True)
    time.sleep(0.25)

    print("Flushing ADC registers...")
    time.sleep(1)  # Small delay to stabilize readings
    # Flush the ADC by taking a few dummy readings
    for ii in range(5):  # Take 5 dummy readings
        ii = read_value(channel)  # Read and discard
    time.sleep(0.01)  # Small delay to stabilize readings
    print("ADC registers flushed. Starting actual data collection...")

    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):
        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)
        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))

        #Add voltage to reading array
        time.sleep(1/freq)
        readingData.append(voltage)
        #Log the mode of operation in a parallel array
        modeLog.append("both")
        #Capture temperature reading
        ledTempData.append((readTemp(CS_1200NM)+readTemp(CS_1550NM))/2)
        #Capture photodiode temperature reading
        photoTempData.append(readTemp(CS_PHOTODIODE_TEMP))

    # Print the collected data
    print("readingData:", readingData,"V")


    print("both LEDs off")
    LED_control('1200', False)
    LED_control('1550', False)
    time.sleep(0.25)

    return readingData, ledTempData, photoTempData, modeLog











