import Functions
import time
import os

print("LED off")
Functions.LED_control('1550', False)
Functions.LED_control('1200', False)
time.sleep(0.25)


#Code snippet 13: Function for Printing Data
def print_data(readingData, ledTempData, photoTempData, modeLog, concentration):
    timestamp = time.localtime() # Generate a filename with a timestamp for exel file
    exeltime = str(timestamp) # Convert timestamp to a string format to be incorporated into the csv

    # Get the current date and time
    now = time.localtime()  # Returns (year, month, day, hour, min, sec, weekday, yearday)

    # Extract individual components
    year = now[0]
    month = now[1]
    day = now[2]
    hour = now[3]
    minute = now[4]
    second = now[5]

    # Construct the filename manually
    filename = "sample{:04d}_{:02d}_{:02d}_{:02d}{:02d}.csv".format(year, month, day, hour, minute, second)


    # Open a new file to write to.
    file = open(filename, "w") # This file can later be automated to automatically be renamed to today's date with a timestamp.

    #file.write(exeltime) # Write the timestamp on the first row of the csv file.
    file.write("reading,voltage,LED_temp,photo_temp,mode,concentration") # Label 3 columns on the first row of the csv file.
    file.write("\n") # Next row.
    file.flush() # Flushes file. This effectively saves the file without closing it.


    for i in range(len(readingData)): # For each reading in the reading array...
        value = str(readingData[i]) # Convert the voltage reading to a string.
        reading = str(i/Functions.freq) # Convert the reading number to a string.
        ledTemp=str(ledTempData[i])
        photoTemp=str(photoTempData[i])
        mode=modeLog[i]

        # Write the reading number and corresponding reading voltage row by row.
        file.write(reading+","+value+","+ledTemp+","+photoTemp+","+mode+","+concentration)
        file.write("\n")
    file.flush() # Flushes file



    return







#Top Level Testcase
concentration="100"
# Create an empty list to store voltage values
readingData = []
# Create an empty list to store temperature reading values for LEDs
ledTempData = []
# Create an empty list to store temperature reading values for photodiode
photoTempData = []
# Create an empty list to store data collection mode. Either 1550, 1200, or both.
modeLog = []

readingData, ledTempData, photoTempData, modeLog = Functions.topLevelDataCollection(2)
print_data(readingData, ledTempData, photoTempData, modeLog, concentration)






"""
#Individual Mode Test Cases
#1550
print("LED on")
Functions.LED_control('1550', True)
time.sleep(0.25)

print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
freq=400000
channel=2
slave_data_test, slave_data_average = Functions.collectData(freq, channel)
print_data(slave_data_test,concentration)
print("data collection complete")
print(slave_data_average)

# Turn off the LED with ID '1550'
time.sleep(0.25)
Functions.LED_control('1550', False)
print("LED off again")
"""


"""
#1200
time.sleep(0.25)
print("LED on")
Functions.LED_control('1200', True)
time.sleep(0.25)

print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
freq=400000
channel=2
slave_data_test, slave_data_average = Functions.collectData(freq, channel)
print_data(slave_data_test,concentration)
print("data collection complete")
print(slave_data_average)

# Turn off the LED with ID '1550'
time.sleep(0.25)
Functions.LED_control('1200', False)
print("LED off again")
"""


"""
#Both
time.sleep(0.25)
print("LED on")
Functions.LED_control('1200', True)
Functions.LED_control('1550', True)
time.sleep(0.25)

print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
freq=400000
channel=2
slave_data_test, slave_data_average = Functions.collectData(freq, channel)
print_data(slave_data_test,concentration)
print("data collection complete")
print(slave_data_average)

# Turn off the LED with ID '1550'
time.sleep(0.25)
Functions.LED_control('1200', False)
Functions.LED_control('1550', False)
print("LED off again")
"""







"""
#Read temperature test cases
#read temp
print("Measuring temperature")
t = Functions.readTemp(Functions.CS_PHOTODIODE_TEMP)# Store temperature measurement here
print(t)
#read temp
print("Measuring temperature")
t = Functions.readTemp(Functions.CS_1550NM)# Store temperature measurement here
print(t)
#read temp
print("Measuring temperature")
t = Functions.readTemp(Functions.CS_1200NM)# Store temperature measurement here
print(t)
"""



"""
#Code snippet 12: Collect Data Test Case
# Collect data test case
print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
slave_data_test = Functions.collectDataWithLED(channel=2)
print_data(slave_data_test)
print("data collection complete")
"""


"""
print("beginning LED on/off testcase")
Functions.LED_control('1550', False)
Functions.LED_control('1200', False)
utime.sleep(5)
Functions.LED_control('1550', True)
utime.sleep(5)
Functions.LED_control('1550', False)
utime.sleep(5)
Functions.LED_control('1200', True)
utime.sleep(5)
Functions.LED_control('1200', False)
print("ending LED on/off testcase")
"""







