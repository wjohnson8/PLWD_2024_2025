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
LED_NUM_READINGS = 400
# Global variable for number of readings to take for no LED
NO_LED_NUM_READINGS = 40
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
channel=0

# Define pins for the Motor
DIR_PIN = 5   # Motor direction pin 7 (GPIO 5)
STEP_PIN = 6  # Step size pin 9 (GPIO 6)
ENABLE_PIN = 12  # Motor enable pin 16 (GPIO 12)
RESET_PIN = 8 # Motor reset pin 11 (GPIO 8)
SLEEP_PIN = 7 # Motor sleep pin 10 (GPIO 7)
RESOLUTION_MS1 = 11 # Motor resolution 1 pin 15 (GPIO 11)
RESOLUTION_MS2 = 10 # Motor resolution 2 pin 14 (GPIO 10)
RESOLUTION_MS3 = 9  # Motor resolution 3 pin 12 (GPIO 9)


# Define pins for LED
LED_1550_PIN = 14 # 1550nm LED enable pin 19 (GPIO 14)
LED_1200_PIN = 15 # 1200nm LED enable pin 20 (GPIO 15)



# Initialize GPIO pins (all outputs, controlled by Raspberry Pi Pico)
dir_pin = Pin(DIR_PIN, Pin.OUT)
step_pin = Pin(STEP_PIN, Pin.OUT)
enable_pin = Pin(ENABLE_PIN, Pin.OUT)
reset_pin = Pin(RESET_PIN, Pin.OUT)
sleep_pin = Pin(SLEEP_PIN, Pin.OUT)
resolution_ms1_pin = Pin(RESOLUTION_MS1, Pin.OUT)
resolution_ms2_pin = Pin(RESOLUTION_MS2, Pin.OUT)
resolution_ms3_pin = Pin(RESOLUTION_MS3, Pin.OUT)
led_1550 = Pin (LED_1550_PIN, Pin.OUT)
led_1200 = Pin (LED_1200_PIN, Pin.OUT)
led_1550.value(0)
led_1200.value(0)


#I2C setup and driver functions
dev = I2C(1, freq=100000, scl=Pin(3), sda=Pin(2))
devices = dev.scan()
for device in devices: print(device)
address = 72


#spi setup for temperature control
# Define individual CS pins as constants
CS_1200NM = Pin(22, Pin.OUT)  # Chip select for 1200nm
CS_1550NM = Pin(17, Pin.OUT)  # Chip select for 1550nm
CS_PHOTODIODE_TEMP = Pin(20, Pin.OUT)  # Chip select for photodiode temp IC

CS_1200NM.value(1)
CS_1550NM.value(1)
CS_PHOTODIODE_TEMP.value(1)


#temp read constants
beta = 3435   #thermistor constant in kelvin
r0 = 10000    #thermistor resistance constant
rext = 6800   #resistor value for temp IC's

#initiallize SPI using the SPI import
spi = SPI(0,baudrate=100000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))  # Software SPI



#I2C Communication with ADS1115 ADC
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


#Code snippet 3: Motor Rotation Function in Functions.py (part 1)
def motorRotation(angle, step_angle, delay_per_step, direction, m1, m2, m3):
    """
    Rotate the motor based on the specified angle, microstepping, and direction.

    :param angle: Angle to rotate in degrees
    :param step_angle: Step angle of the motor (e.g., 1.8 degrees)
    :param delay_per_step: Delay between steps in seconds (affects speed)
    :param direction: Direction of rotation (1 for clockwise, 0 for counterclockwise)
    :param m1: State for MS1 pin (0 or 1)
    :param m2: State for MS2 pin (0 or 1)
    :param m3: State for MS3 pin (0 or 1)
    """
    reset_pin.value(1)
    sleep_pin.value(1)
    enable_pin.value(0)

    # Set direction
    dir_pin.value(direction)

    #Code snippet 4: Motor Rotation Function in Functions.py (part 2)
    # Configure microstepping
    resolution_ms1_pin.value(m1)
    resolution_ms2_pin.value(m2)
    resolution_ms3_pin.value(m3)


    # Calculate the number of steps for the specified angle
    microstepping_factor = 1
    if (m1, m2, m3) == (0, 0, 0):  # Full-step
        microstepping_factor = 1
    elif (m1, m2, m3) == (1, 0, 0):  # Half-step
        microstepping_factor = 2
    elif (m1, m2, m3) == (1, 1, 0):  # Quarter-step
        microstepping_factor = 4
    elif (m1, m2, m3) == (1, 1, 1):  # 1/16 step
        microstepping_factor = 16


    #This is how many steps will be made for 360 degrees
    steps_per_revolution = int(360 / step_angle) * microstepping_factor
    print(steps_per_revolution)


    #(steps/360) *180 for required steps
    steps_to_move = int((angle / 360) * steps_per_revolution)
    print(steps_to_move)


    # Generate step pulses
    for i in range(steps_to_move):
        step_pin.value(1)
        utime.sleep(delay_per_step)
        step_pin.value(0)
        utime.sleep(delay_per_step)
    return

#Code snippet 5: Collect Data Function in Functions.py
#Data collection sequence for reading the 1550nm photodiode
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







def readTemp():
    '''
    returns the temperature reading from temp IC1(3400nm LED), temp IC2 (1500nm LED), or temp IC3 (photodiode)
    :param spi: SPI object initialized earlier.
    :param cs: chip select for temperature IC
    :return: digital temperature of selected sensor as a 32 bit float
    '''
    
    
    #print("Received Data:", ' '.join(f"0x{byte:02X}" for byte in temp_data))
    CS_PHOTODIODE_TEMP.value(0)  # Select device
    #time.sleep_us(1)  # Small delay

    #spi.write(bytearray([0x00]))  # Some ICs require a read command first
    temp_data = spi.read(2)  # Read 2 bytes
    print("Received Data:", ' '.join(f"0x{byte:02X}" for byte in temp_data))
    print(f"Byte 1: 0x{temp_data[0]:02X}, Byte 2: 0x{temp_data[1]:02X}")

    CS_PHOTODIODE_TEMP.value(1)  # Deselect device
    
    
    temp_data_16bits=((temp_data[0] << 3)  | (temp_data[1] >> 5))
    

    # Convert bytes to 16-bit value
    #temp_data_16bits = (temp_data[0] << 8) | temp_data[1]
    #temp_data_16bits = temp_data_16bits >> 5  # Adjust bit alignment

    # Sign bit extension
    if temp_data_16bits & (1 << 9):
        temp_data_16bits -= 1 << 10

    # Convert to temperature
    normalized_voltage = ((temp_data_16bits * 0.010404)/8) + 0.174387
    print(normalized_voltage)
#     
    rtherm = ((1-normalized_voltage) * rext) / (normalized_voltage)
    tempK = 1 / ((1/298.15) +  (math.log(rtherm / r0)/beta ))
    tempC = tempK - 273.15
    
    #tempK=beta/((beta/298.15)+math.log(((1-normalized_voltage)*rext)/((normalized_voltage)*r0)))
    

    return tempC
    #return tempK-273.15






#Code snippet 5: Collect Data Function in Functions.py
#Data collection sequence for reading the 1550nm photodiode
def collectDataWithLED(channel):
    print("running")

    # Create an empty list to store voltage values
    slaveData = []

    # Turn off the LED with ID '1550'
    LED_control('1550', False)
    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):


        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)

        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))


        #add voltage to array
        utime.sleep(0.5)
        slaveData.append(voltage)
        utime.sleep(0.5)

    print("Now turning on the LED")
    # Turn on the LED with ID '1550'
    LED_control('1550', True)
    # Take readings and store them in the list
    for i in range(LED_NUM_READINGS):


        #Fetch voltage value
        val = read_value(channel)
        voltage = val_to_voltage(val)


        #print voltage value
        print("ADC Value:", val, "Voltage: {:.3f} V".format(voltage))


        #add voltage to array
        utime.sleep(0.5)
        slaveData.append(voltage)
        utime.sleep(0.5)


    # Turn off the LED with ID '1550'
    LED_control('1550', False)

    # Print the collected data
    print("1550 nm Data, LED on:", slaveData,"V")

    return slaveData





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









"""
def selfCalibrate(led_id, initial_guess_deg,sweep_range=5):
    '''
    Sweep around an estimate diffraction angle to find the best alignment angle for one LED which been selected by system)
    
    :param led_id: A string to defind which LED is calibrating now "1550" or "1200"
    :param initial_guess_deg: The starting angle
    :param sweep_range: the pre defends range for the led +/-5 degree
    :return: the best angle found
    '''
    #Turn on the LED
    LED_control(led_id,1)
    
    #Place to storing the best angle and best photodiode reading
    best_angle_deg = initial_guess_deg
    max_reading = -999
    # If your motor_angle or get_position() is in encoder ticks, you need
    # to convert between degrees and encoder ticks. For simplicity here,
    # we assume your motor_rotation() call uses degrees directly.

    # Move the motor to the initial guess angle
    #notes: motor_rotation(angle, step_angle, delay_per_step, direction, m1, m2, m3)
    #       If you need a specific microstepping, set m1, m2, m3 accordingly.
    motor_rotation(
        angle=abs(initial_guess_deg),
        step_angle=1.8,
        delay_per_step=0.1,
        direction=1 if initial_guess_deg>=0 else 0,
        m1 = 0,
        m2 = 0,
        m3 = 0
    )
    # Range for the angles to be measured
    start_angle = initial_guess_deg - sweep_range
    end_angle = initial_guess_deg + sweep_range + 1
    
    for angle_test in range(start_angle,end_angle):
        #Figure out how much degrees need to move by now angle
        delta_deg = angle_test - get_position()
        
        motor_rotation(
            angle = abs(delta_deg),
            step_angle=1.8,
            delay_per_step=0.1
            direction=1 if initial_guess_deg>=0 else 0,
            m1 = 0,
            m2 = 0,
            m3 = 0
        )
    # Check the photodiode reading
    sample_sum = 0
    num_samples = 5
    for _ in range (num_samples):
        raw_val = read_value(0)
        sample_sum = raw_val+raw_val
        utime.sleep(0.05)
    avg_val = sample_sum/ num_samples
    
    #Try to find the maximun value
    if avg_val > max_reading:
        max_reading = avg_val
        best_angle_deg = angle_test
    # Rotate to the best angle
    final_angle = best_angle_deg - get_position()
    motor_rotation(
        angle = abs(final_angle),
        step_angle=1.8,
        delay_per_step=0.1
        direction=1 if initial_guess_deg>=0 else 0,
        m1 = 0,
        m2 = 0,
        m3 = 0
        )
    #Turn off the LED
    LED_control (led_id,0)
    
    return best_angle_deg
        
def top_data_collection():
    '''
    1) Turns off LEDs
    2) Collects dat with no LED
    3) Reads temperature
    4) Self-calibrates for 1550nm LED
    5) Collects data (1550nm)
    6) Reads temperature
    7) Self-calibrates for 1200nm LED
    8) Collects data (1200nm)
    9) Reads temperature
    10) Returns dictionary of data arrays
    '''
    
    #Containers for results
    backgroud_data = []
    led_data_1550 = []
    led_data_1200 = []
    temperature_record = []
    
    # Turn off the LEDs
    LED_control('1550',0)
    LED_control('1200',0)
    
    #Collect data with no LED
    print("Recording No LED data")
    for _ in range(NO_LED_NUM_READINGS):
        reading = read_value(0)
        backgroud_data.append(reading)
        utime.sleep(0.2)
        
    # Read temperature
    print("Measuring temperature with no LED on")
    t_1200 = readTemp(spi,CS_PINS[0])
    t_1550 = readTemp(spi, CS_PINS[1])
    t_pd = readTemp(spi, CS_PINS[2])
    temperature_record.append(("NO LED", t_1200,t_1550,t_pd))
    
    #Self-calibrate for 1550nm
    print("Self-calibrating for 1550nm LED")
    best_angle_1550 = selfCalibrate('1550', initial_guess_deg=45, sweep_range=5)
    
    #Collect Data for 1550nm
    LED_control('1550',1)
    print("Collection data from 1550nm LED")
    for _ in range(LED_NUM_READINGS):
        reading = read_value(0)
        led_data_1550.append(reading)
        utime.sleep(0.2)
    
    # Turn off 1550nm LED
    LED_control('1550',0)
    
    # Read temperature
    print("Measuring temperature after measuring the 1550nm")
    t_1200 = readTemp(spi,CS_PINS[0])
    t_1550 = readTemp(spi, CS_PINS[1])
    t_pd = readTemp(spi, CS_PINS[2])
    temperature_record.append(("NO LED", t_1200,t_1550,t_pd))
    
    #Self-calibrate for 1200nm
    print("Self-calibrating for 1200nm LED")
    best_angle_1200 = selfCalibrate('1200', initial_guess_deg=45, sweep_range=5)
    
    #Collect Data for 1200nm
    LED_control('1200',1)
    print("Collection data from 1200nm LED")
    for _ in range(LED_NUM_READINGS):
        reading = read_value(0)
        led_data_1200.append(reading)
        utime.sleep(0.2)
    
    # Turn off 1200nm LED
    LED_control('1200',0)
    
    # Read temperature
    print("Measuring temperature after measuring the 1200nm")
    t_1200 = readTemp(spi,CS_PINS[0])
    t_1550 = readTemp(spi, CS_PINS[1])
    t_pd = readTemp(spi, CS_PINS[2])
    temperature_record.append(("NO LED", t_1200,t_1550,t_pd))
    
    #Return all data
    return {
        'backgroud_data' : backgroud_data,
        'led_data_1550' : led_data_1550,
        'led_data_1200' : led_data_1200,
        'temperature_record' : temperature_record,
        'best_angle_1550' : best_angle_1550,
        'best_angle_1200': best_angle_1200,
    }
    
def readTemp(spi, cs):
    '''
    returns the temperature reading from temp IC1(1200nm LED), temp IC2 (1500nm LED), or temp IC3 (photodiode)
    :param spi: SPI object initialized earlier.
    :param cs: chip select for temperature IC
    :return: digital temperature of selected sensor as a 32 bit float
    '''
#notes:
# do we need to change the bit length of the data? it is currently at 2 bytes when reading from the sensor.
#


    # data read
    cs.value(0)             #drive chip select pin low to allow spi communication
    temp_data = spi.read(2) #read 2 bytes of data from selected IC
    cs.value(1)             #free the miso spi line by driving select pin to high

    # temperature conversion
    temp_data_16bits = (temp_data[0] << 8) | (temp_data[1])  #combine the 2 bytes into a 16 bit integer
    temp_data_16bits = temp_data_16bits >> 5                 #shift the useful data bits right to represent the correct value in 16 bit form

    if temp_data_16bits & (1 << 10):      #check sign bit of the digital temp data
       temp_data_16bits -= 1 << 11        #if sign bit is negative we sign extend the result

    #convert digital value to decimal temperature
    normalized_voltage = ((temp_data_16bits * 0.010404)/8) + 0.174387   #normalized voltage = vrext/vr+
    rtherm = (normalized_voltage * rext)/(1 - normalized_voltage)       #thermistor resistance equivalence
    tempK = beta/(log(rtherm/r0))                                       #decimal temperature data in kelvin
    tempC = tempK - 273                                                 #convert kelvin to celcius

    return tempC


"""






