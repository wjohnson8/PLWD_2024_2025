#Code snippet 6: Libraries, Global Variables, and UART Configuration for Main.py
import struct # Used to adjust the size of variables to be integrated with the packet format
import Functions # Importing the Functions.py file
from machine import UART, Pin # Uart and GPIO libraries for communication


mode=0 # Mode select input from Raspberry PI 4. Defaults to sleep mode
readingData=[] # This is an empty array to store the output of topDataCollection


# Setting up communication from Raspberry pi 4 to Raspberry pi Pico via UART
# Configure UART on GPIO 0 (TX) and GPIO 1 (RX)
uart = UART(1, baudrate=9600, parity=UART.ODD, stop=2, bits=7, tx=Pin(1), rx=Pin(2))


#Code snippet 7: Global Variables for Loading Packets
# Prepare packets
packetArr=[] # array full of packets. Each element of the array is one packet (with 2 readings)
dataType=0x00 # 8-bit data type, assume 0 for science data.
readingNumber=0x0000 # 16-bit reading number.
readingNumberTemp=0 # Temporary integer which will be packed into readingNumber
reading1=0x0000_0000_0000_0000 # 64-bit first reading.
reading2=0x0000_0000_0000_0000 # 64-bit second reading.



#Code snippet 8: Prepare Data Function for Main.py
# Packing the current data into packetArr[]
def prepareData():
    if (readingData and readingData.length()==252): # Assure readingData exists and properly received from Functions.py
        for i in range(len(readingData)):# For each of the 252 readings (100 for each LED + 40 for no LED + 12 for temp sensors)
            if i%2 ==0:#at each even reading


                # readingNumber is 16 bits of the integer i.
                readingNumberTemp = i
                readingNumber = struct.pack(">H", readingNumberTemp)


                # 2 Readings per packet
                reading1=readingData[i]
                reading2=readingData[i+1]


                # Create Packet and pack the data into a binary format: B=8 bits, H=16 bits, I=32 bits
                packet = struct.pack(">BHII", dataType, readingNumber, reading1, reading2) #Will throw a compile error when these sizes are incorrect.
                checksum = sum(packet) % 256 # Calculate the checksum
                packet_with_checksum = packet + struct.pack(">B", checksum) # Add the checksum to the packet
                packetArr.append(packet_with_checksum) # Add each packet to packetArr
    else: print("readingData Invalid. readingData.length()=" + str(len(readingData)))
    return



#Code snippet 9: Continuous Polling Main Loop for Main.py
# Main program
while True:


    #Input from Pi 4
    if uart.any():  # Check if there's data available in the UART buffer
        mode = uart.read(4)  # Read 4 byte and discard the incoming data
    print("Received:", readingData.decode('utf-8'))  # Decode and print the received data
    time.sleep(0.1)  # Add a small delay to prevent excessive CPU usage


    #Mode control
    if mode == 0: # sleep
        Functions.sleepMode() # Calls sleepMode() function from Functions.py


    elif mode == 1: # collect readingData
        readingData = Functions.topDataCollection() # Calls topDataCollection()_ from Functions.py to obtain the array of readings
        prepareData() # repopulate packetArr with current data


    elif mode == 2: # send readingData
        # Send packets one by one
        if (packetArr.length()==126): # Assure packetArr contains the correct number of packets
            for i in range(len(packetArr)):
                uart.write(packetArr[i])  # Send each packet, one at a time (2 data readings at a time)
        else : print("packetArr invalid. packetArr.length()=" + str(len(packetArr)))


    else:
        Functions.sleepMode()
        print("Invalid mode selected. Please choose: 'sleep', 'data_collection', or 'send_data'.")







