import serial
import serial.tools.list_ports
import time
import pandas as pd
from NetFT import Sensor

mcu_name = 'XIAO'
sensor_ip = '' # put your ATI Mini45 Sensor IP here
dataset_name = '' # put your dataset name IP here

def getGripperData():
    gripper_msg = serial_port.readline().decode('ascii')
    gripper_msg = gripper_msg.replace('\r\n', '')
    gripper_data = list(gripper_msg.split(","))

    return gripper_data

def getPorts():
    return serial.tools.list_ports.comports()

def findMCU(ports, mcu_name):
    
    usb_port = 'None'
    
    for i in range(0,len(ports)):
        port = ports[i]
        str_port = str(port)
        
        if mcu_name in str_port: 
            split_port = str_port.split(' ')
            usb_port = (split_port[0])

    return usb_port

sensor = Sensor(sensor_ip)

used_ports = getPorts()        
mcu_port = findMCU(used_ports, mcu_name)

if mcu_port != 'None':
    serial_port = serial.Serial(mcu_port, baudrate=9600, timeout=1)
    print('Connected to ' + mcu_port)
else:
    print('Connection ERROR!')

df = pd.DataFrame(columns=['RotSens1','RotSens2','PresSens1','PresSens2',
                           'CurrSens1','CurrSens2','CurrSensInit1','CurrSensInit2',
                           'ForceX', 'ForceY', 'ForceZ'])
counter = 0
while True:

    mcu_data = getGripperData()
    sensor_data = sensor.getForce()
    
    print(mcu_data + sensor_data)
    if len(mcu_data + sensor_data) == len(df.columns):
        df.loc[len(df)] = mcu_data + sensor_data
    if len(df) >= 3000:
        df.to_csv(dataset_name + '_' + str(counter) + '.csv')
        df = pd.DataFrame(columns=df.columns, index=False)
        counter += 1
