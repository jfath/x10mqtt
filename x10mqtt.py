#
# MQTT to X10 bridge
# Supports: ACT TI103-RS232 
#
#Copyright (c) 2018 Jerry Fath
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this
#software and associated documentation files (the "Software"), to deal in the Software
#without restriction, including without limitation the rights to use, copy, modify,
#merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be included in all copies
#or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
#OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.#
#

#pip install paho-mqtt, pyserial

import paho.mqtt.client as mqtt #import the client1
import serial, time, datetime, sys

#---------------------------------------------------------------
# Edit these for your environment
#---------------------------------------------------------------

# x10 powerline bridge 
x10_dev = 'TI103'
#x10_dev = 'CM11A'

# Name of serial device
#serial_dev = '/dev/ttyAMA0'
serial_dev = '/dev/ttyUSB0'

# MQTT broker address
broker_address="192.168.222.71"

# X10 lights MQTT topic
x10lights_topic="home/lights/x10mqtt/+"


#---------------------------------------------------------------
# X10 ti103 specific
#---------------------------------------------------------------

# 1 byte checksum on string returned as uppercase hex string
def ti103_checksum256(s):
    return '%02X' % ((sum(ord(c) for c in s) % 256) & 0xFF)

# Send a command to the ti103
def ti103_send(x10dev, x10cmd):
    cmdstr = '$>28001' + x10dev + x10dev + ' ' + x10cmd + x10cmd
    cmdstrcc = cmdstr + ti103_checksum256(cmdstr) + '#'
    #Can raise SerialTimeoutException
    try:
       write_val = ser.write(cmdstrcc.encode('utf_8', 'ignore'))
    except Exception as e:
       print("Timeout writing serial port: " + str(e))
    #Read the return status
    time.sleep(2)
    read_val = ser.read(size=64)
    print('ti103 cmd: %s    status: %s' % (cmdstrcc, read_val))
    return 0

# Turn x10 device on or off
# ti103 commands look like:
# '$>28001' + x10dev + x10dev + ' ' + x10cmd + x10cmd + checksum256 + '#'
# All B code devices on [['B01', 'BALN']]
# All B code devices off [['B01', 'BALF']]
# D01 on, D02 on, D03 on [['D01', 'DON'], ['D02', 'DON'], ['D03', 'DON']]
# D01 off, D02 off, D03 off [['D01', 'DOFF'], ['D02', 'DOFF'], ['D03', 'DOFF']]
def ti103_command(x10dev, act):
    #Open the serial port
    try: 
        ser.open()
        if ser.isOpen():
            #Flush serial buffers
            ser.flushInput()
            ser.flushOutput()
        else:
            print("cannot open serial port ")
            return -1
    except Exception as e:
        print("error opening serial port: " + str(e))
        return -2

    x10devu = x10dev.upper()
    actu = act.upper()
    house_code = x10devu[:1]
    unit_num = x10devu[-2:]
    # unit number 00 is invalid, so we use it to mean all units
    if (unit_num == '00'):
        x10devu = house_code + '01'
        if (actu == 'ON'):
            cmd = house_code + 'ALN'
        elif (actu == 'OFF'):
            cmd = house_code + 'ALF'
        else:
            print("Unimplemented x10 command")
            return -3
    else:
        if (actu == 'ON'):
            cmd = house_code + 'ON'
        elif (actu == 'OFF'):
            cmd = house_code + 'OFF'
        else:
            print("Unimplemented x10 command")
            return -3

    print("Send to ti103: " + x10devu + " " + cmd)
    ti103_send(x10devu, cmd)

    ser.close()
    return 0

# Open for ti103 - sets up serial port
def ti103_open():
    # Seup the serial port
    ser.port = serial_dev
    ser.baudrate = 9600
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #possible timeout values:
    #    None: wait forever, block call
    #    0: non-blocking mode, return immediately
    #    x, x is bigger than 0, float allowed, timeout block call
    ser.timeout = 1        # timeout block read
    ser.xonxoff = False    #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
    ser.writeTimeout = 2   #timeout for write
    return 0

# Close for ti103 - nothing needed
def ti103_close():
    return 0

#---------------------------------------------------------------
# X10 cm11a specific
#---------------------------------------------------------------

# todo!!! Send command to cm11a
def cm11a_command(x10dev, act):
    return -1

# Open for cm11a - sets up serial port
def cm11a_open():
    # Seup the serial port
    ser.port = serial_dev
    ser.baudrate = 4800
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #possible timeout values:
    #    None: wait forever, block call
    #    0: non-blocking mode, return immediately
    #    x, x is bigger than 0, float allowed, timeout block call
    ser.timeout = 1        # timeout block read
    ser.xonxoff = False    #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
    ser.writeTimeout = 2   #timeout for write
    return 0

# Close for cm11a - nothing needed
def cm11a_close():
    return 0

#---------------------------------------------------------------
# x10 code
# Note: Only supports ti103 at the moment
#---------------------------------------------------------------

def x10_command(x10dev, act):
    if (x10_dev == 'TI103'):
        return ti103_command(x10dev, act)
    if (x10_dev == 'CM11A'):
        return cm11a_command(x10dev, act)
    else:
        print("Unimplemented x10 powerline bridge")
        return -1

def x10_open():
    if (x10_dev == 'TI103'):
        return ti103_open()
    if (x10_dev == 'CM11A'):
        return cm11a_open()
    else:
        print("Unimplemented x10 powerline bridge")
        return -1

def x10_close():
    if (x10_dev == 'TI103'):
        return ti103_close()
    if (x10_dev == 'CM11A'):
        return cm11a_close()
    else:
        print("Unimplemented x10 powerline bridge")
        return -1


#---------------------------------------------------------------
# MQTT code
#---------------------------------------------------------------

# MQTT callback when the client receives a CONNACK response
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(x10lights_topic)

# MQTT callback when the client receives a message
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    x10_command(message.topic[-3:], str(message.payload.decode("utf-8")))

# MQTT callback when the client disconnects
def on_disconnect(client, userdata, rc):
    print("Disonnected with result code " + str(rc))


#---------------------------------------------------------------
# main
#---------------------------------------------------------------

# Creating here so we can use a global serial object
ser = serial.Serial()

# Init the x10 powerline bridge
x10_open()

#create new MQTT client instance
print("creating new instance")
client = mqtt.Client("x10mqtt") 
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

#connect to broker
print("connecting to broker")
client.connect(broker_address, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
print("Press Ctrl-C to quit")
client.loop_forever()

# We never get here with loop_forever()
# Close and cleanup the x10 powerline bridge
x10_close()
