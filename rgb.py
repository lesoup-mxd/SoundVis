# ************************************************************************************************
#
#    A Python script to connect to an Arduino via serial port and send RGB color values to it

import serial
import serial.tools.list_ports


# Default state for the while loop that connects to the Arduino COM port
arduinoConnected = False

# List the available COM ports will be added to
comPorts = [], []

# Color codes for the 4 predefined colors in the gui
red    = "ff0000"
green  = "00ff00"
blue   = "0000ff"
purple = "9e0083"

# Turns the RGB LED pins off
white = "ffffff"
off    = "000000"


# Function to send the color value as decimal via serial port to the Arduino
def requestColor(color) -> None:
    rgbSelectValue = str(int(color, 16)) # puts the color hex value as decimal in a string
    ser.write(("#" + rgbSelectValue).encode())

def requestColorCorrected(color, r_correction=1, g_correction=0.9, b_correction=0.8) -> None:
    color_red = hex(int(color[2]*r_correction))[2:]
    color_green = hex(int(color[1]*g_correction))[2:]
    color_blue = hex(int(color[0]*b_correction))[2:]
    if len(color_red) == 1:
        color_red = "0" + color_red
    if len(color_green) == 1:
        color_green = "0" + color_green
    if len(color_blue) == 1:
        color_blue = "0" + color_blue
    color = color_red + color_green + color_blue
    requestColor(color)


# Function to return available hardware serial ports and (if possible) detect current Arduino COM port
def getSerialPorts() -> list:
    ports = serial.tools.list_ports.comports(include_links=False)
    for i, e in enumerate(ports):
        # Trying to automatically detect Arduino COM port by looking for "Arduino" string in information of all available hardware serial ports
        if "Arduino" in e[1]:
            comPort = e[0]
        comPorts[0].append(e[0])
        comPorts[1].append(e[1])
    print("Available COM ports: ", comPorts[0])
    return comPorts, comPort


# Sets the COM port the Arduino is connected to automatically or requests manual COM port input from user if not working
def connect(comPort="/dev/ttyACM0") -> list:
    global arduinoConnected, ser
    arduinoConnected = False
    while not arduinoConnected:
        try:
            #comPorts, comPort = getSerialPorts()
            ser = serial.Serial(comPort, 9600)
            arduinoConnected = True
        except:
            try:
                ser = serial.Serial(comPort, 9600)
                arduinoConnected = True
            except serial.SerialException as e:
                # Manual input of the COM port failed so giving the user the possibility to try again or leave
                return False, e
    return True

def closeSerial() -> bool:
    ser.close()
    return True









if __name__ == "__main__":
    import main

    #color correction
    r_correction = 1
    g_correction = 1
    b_correction = 1#0.5
    print("Trying to connect to Arduino...")
    connect()
    print("Connected to Arduino.")
    print("Analyzing screen colors...")
    colors = main.fetch_dominant_colors(1)
    color = colors[0]
    #test color
    color = [255, 255, 255]
    color_red = hex(int(color[2]*r_correction))[2:]
    color_green = hex(int(color[1]*g_correction))[2:]
    color_blue = hex(int(color[0]*b_correction))[2:]
    print("Color: ", color_red, color_green, color_blue)
    if len(color_red) == 1:
        color_red = "0" + color_red
    if len(color_green) == 1:
        color_green = "0" + color_green
    if len(color_blue) == 1:
        color_blue = "0" + color_blue
    color = color_red + color_green + color_blue
    print("Color: ", color)
    import time
    time.sleep(2)
    requestColor(color)
    print("Closing serial port...")
    time.sleep(2)
    closeSerial()
