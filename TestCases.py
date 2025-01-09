import Functions
import time



#Code snippet 13: Function for Printing Data
def print_data(slave_data_test):
    timestamp = time.localtime() # Generate a filename with a timestamp for exel file
    exeltime = str(timestamp) # Convert timestamp to a string format to be incorporated into the csv


    # Open a new file to write to.
    file = open("sample2024_11_15.csv", "w") # This file can later be automated to automatically be renamed to today's date with a timestamp.

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



#Code snippet 12: Collect Data Test Case
# Collect data test case
print("beginning data collection")
slave_data_test = []
# Channel integer to select between device A0, A1, A2, or A3 on the ADS1115
slave_data_test = Functions.collectData(channel=3)
print_data(slave_data_test)
print("data collection complete")




#Code snippet 14: Motor Rotation Test Case
#Motor rotation 180 degree test case
try:
    # Parameters for motor rotation
    angle = 180           # Rotate 180 degrees
    step_angle = 0.018      # Step angle of the motor (in degrees)
    delay_per_step = 0.0005/2  # Delay between steps (for 5 second rotation)
    direction = 0        # 1 for clockwise, 0 for counterclockwise
    m1, m2, m3 = 0, 0, 0  # Set stepping factor to full step because of minimum step angle


    print(f"Rotating {angle} degrees clockwise with 1/16 microstepping...")
    Functions.motorRotation(angle, step_angle, delay_per_step, direction, m1, m2, m3)
    print("Rotation complete.")


except KeyboardInterrupt:
    print("Exiting program...")
    Functions.enable_pin.value(1)  # Disable the motor driver


