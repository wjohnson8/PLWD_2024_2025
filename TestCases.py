import Functions
import time



#Code snippet 13: Function for Printing Data
def print_data(slave_data_test):
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

    # Construct the filename manually
    filename = "sample{:04d}_{:02d}_{:02d}_{:02d}{:02d}.csv".format(year, month, day, hour, minute)


    # Open a new file to write to.
    file = open(filename, "w") # This file can later be automated to automatically be renamed to today's date with a timestamp.

    file.write(exeltime) # Write the timestamp on the first row of the csv file.
    file.write("\n") # Next row.
    file.write("reading,voltage") # Label 2 columns on the second row of the csv file.
    file.write("\n") # Next row.
    file.flush() # Flushes file. This effectively saves the file without closing it.


    for i in range(len(slave_data_test)): # For each reading in the reading array...
        value = str(slave_data_test[i]) # Convert the voltage reading to a string.
        reading = str(i) # Convert the reading number to a string.
        # Write the reading number and corresponding reading voltage row by row.
        file.write(reading+","+value)
        file.write("\n")
    file.flush() # Flushes file


    return


"""
#Code snippet 12: Collect Data Test Case
# Collect data test case
print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
freq=100*1000
slave_data_test = Functions.collectData(channel=2,freq)
print_data(slave_data_test)
print("data collection complete")
"""


#PETER--> Update test case here.
temperature_data = []    # Holds the temperature values
#read temp
print("Measuring temperature")
t = readTemp(spi,CS_PINS)                        # Store temperature measurement here
temperature_data.append(("breadboard_test", t))  # Add reading to array




'''
#Code snippet 12: Collect Data Test Case
# Collect data test case
print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
slave_data_test = Functions.collectDataWithLED(channel=2)
print_data(slave_data_test)
print("data collection complete")
'''


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


"""
#Code snippet 14: Motor Rotation Test Case
#Motor rotation 180 degree test case
try:
    # Parameters for motor rotation
    angle = 30           # Rotate 180 degrees
    step_angle = 0.018      # Step angle of the motor (in degrees)
    delay_per_step = 0.001 # Delay between steps (for 5 second rotation)
    direction = 0        # 1 for counterclockwise, 0 for clockwise-->from top
    m1, m2, m3 = 0, 0, 0  # Set stepping factor to full step because of minimum step angle


    print(f"Rotating {angle/2} degrees clockwise with 1/16 microstepping...")
    Functions.motorRotation(angle, step_angle, delay_per_step, direction, m1, m2, m3)
    print("Rotation complete.")
except KeyboardInterrupt:
    print("Exiting program...")
    Functions.enable_pin.value(1)  # Disable the motor driver




print("beginning data collection")
# Initialize an empty result list
result = []
# Call the function 24 times and concatenate the results
for _ in range(24):  # Loop 24 times
    # Parameters for motor rotation
    angle = 0.25           # Rotate 180 degrees
    step_angle = 0.018      # Step angle of the motor (in degrees)
    delay_per_step = 0.001 # Delay between steps (for 5 second rotation)
    direction = 0        # 1 for counterclockwise, 0 for clockwise-->from top
    m1, m2, m3 = 0, 0, 0  # Set stepping factor to full step because of minimum step angle

    Functions.motorRotation(angle, step_angle, delay_per_step, direction, m1, m2, m3)
    current_array = Functions.collectData(channel=3)  # Get the 5-element array from the function
    result.extend(current_array)  # Append the elements to the result list
print_data(result)
print("data collection complete")
"""



