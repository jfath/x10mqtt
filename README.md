# x10mqtt  
x10mqtt.py is used to connect to an MQTT broker and control x10 lights based on messages published to a subscribed set of topics.  
  
Jerry Fath jerryfath at gmail dot com  
  
 **Features**  
Works with Home Assistant (https://home-assistant.io/) to control x10 devices using MQTT  
  
 **Installation:**  
Edit the initial variable block of x10mqtt.py to match your environment  
  
 **Requires:**  
  python 2.7+ or 3.x  
  pyserial, paho-mqtt
  
 **Usage:**  
To use with Home Assistant, configure mqtt lights:  
  
light:  
  \- platform: mqtt  
    name: x10_inside
    #Unit ID of 00 means all lights on a house code  
    command_topic: "home/lights/x10mqtt/D00"  
    command\_on\_template: "on"  
    command\_off\_template: "off"  
  \- platform: mqtt  
    name: x10_lampfront  
    command_topic: "home/lights/x10mqtt/D01"  
    command\_on\_template: "on"  
    command\_off\_template: "off"  
  

**Notes:**  
only the ACT TI103 x10 bridge is currently supported  
only on and off messages are currently implemented  
  
#Release notes  
  
Created 2018/1/19 jfath  

