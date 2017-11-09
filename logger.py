import sys
import glob
import serial
import csv
import datetime
import time
import requests

prtg_host = '10.228.0.10'
prtg_host_port = '5050'
prtg_sensor_token = 'D92C6864-F658-4870-805C-5F71866B5178'

interval = 1

def getPort():
    """ Looks for the arduino on all available com ports

    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    for port in result:
        ser = serial.Serial(port, baudrate = 9600, timeout=1)
        if ser.isOpen() == False:
            break

        ser.write(b'hello')
        response = ser.readline().decode('ascii')

        response = response.strip()

        if response == (b'temp-hum-sensor').decode('ascii'):
            return ser

    return None

def temp_hum_to_json(sensor_data):
    """ Converts sensor data to json
        data is a str array
        [0] = humidity
        [1] = temperature

    """
    json_response = {
            "prtg": {
                "result": [
                    {
                        "channel": "temperature",
                        "float": 1,
                        "value": float(data[1])
                    },
                    {
                        "channel": "humidity",
                        "float": 1,
                        "value": float(data[0])
                    }
                ]
            }
        }
    return json_response

def send_json(data_json):
    try:
        json_string = str(data_json)
        json_string = str.replace(json_string, '\'', '\"')

        prtg_request_URL = 'http://' + prtg_host + ':' + prtg_host_port + '/' + prtg_sensor_token + '?content=' + json_string

        print(prtg_request_URL)

        request = requests.get(prtg_request_URL)

    except:
        pass

if __name__ == '__main__':
    ser = getPort()

    if ser == None:
        print('Logger not found on any serial port')
        exit

    while True:
        today = datetime.date.today()

        while today == datetime.date.today():

            filename = today.strftime('%d-%m-%Y') + '.csv'

            with open(filename, 'a+') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='|',lineterminator='\n')
            
                while today == datetime.date.today():
                    ser.write(b'next')
                    response = ser.readline().decode('ascii').strip()            

                    data = response.split()

                    today = datetime.date.today().strftime('%d-%m-%y')
                    timeNow = datetime.datetime.now().strftime('%H:%M:%S')

                    writer.writerow([today, timeNow, data[0], data[1]])

                    send_json(temp_hum_to_json(data))                
                    
                    time.sleep(interval)
        

