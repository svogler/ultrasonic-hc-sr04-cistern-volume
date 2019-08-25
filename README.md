# Measure fill-level of oil tank / water-cistern with Raspberry Pi and Ultrasonic Sensor HC-SR04

Measure fill-level with Raspberry Pi and Ultrasonic Sensor HC-SR04, log data into InfluxDB.
Fill-level and historic trend data are displayed via a Grafana Dashboard, Grafana pulling the information from InfluxDB.

![Grafana Dashboard](docs/grafana-dashboard.jpg)

## Hardware required
* Raspberry Pi (Pi Zero works as well)
* HC-SR-04 Ultrasonic Module
* Waterproof case for HC-SR-04
* Cable to connect HC-SR04 and RPi (4-wire)

## Wiring
Following picture shows the circuit how to connect Pi with HC-SR04 ultrasonic sensor. 
In my environment the distance between Pi and HC-SR-04 is 6m, works without any problem.

You need the resistors (voltage divider) in order to drop the voltage going to the GPIO pins down to 3.3v from 5v. 

![Circuit Raspberry Pi and HC-SR04](docs/circuit-pi-hcsr04.jpg)


## Software components needed
* Python
* InfluxDB
* Grafana


## Configuration
(1) Create Influx DB
- `influx -precision rfc3339`
- `CREATE DATABASE Zisterne`

(2) Adjust Parameters in the phyton code to your local config (InfluxDB) and tank (volume, height)

(3) Do a test-run the Phyton script 
- run ![volume.py](volume.py) in a terminal to test, check the output.
- You should see log output of the distance measured

(4) Setup Grafana - InfluxDB Connection

(5) Setup Grafana Dashboard
- Use ![Dashboard.json](Dashboard.json) as example, you can modify based on your own needs

(6) Autostart of the program

- Add to /etc/rc.local following line to autostart the python program (run as pi, change path according to local environment)
- `(sleep 60; sudo -H -u pi /usr/bin/python3 /home/pi/<path>/volume.py >> /home/pi/<path>/output.log) &`

