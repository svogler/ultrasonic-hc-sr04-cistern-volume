#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import datetime
import statistics
from influxdb import InfluxDBClient


# GPIOs for the Sensor
TRIG = 24    # Trigger Signal
ECHO = 23    # Echo receive

# Length Trigger-Impulse
PULSE = 0.00001

# Number of probs for average
BURST = 25

# Schallgeschwindigkeit/2
SPEED_2 = 17015

# Sleeptime after Sensorrun (in sec)
SLEEP_TIME = 15

# Tank Specs
ZISTERNE_HIGH = 20   # Distance from Sensor when full 
ZISTERNE_LOW = 190   # Distance from Sensor when empty 
ZISTERNE_VOLUME=5000 # Volume (full)

#INFLUXDB Parameters
INFLUX_DB_HOST='localhost'
INFLUX_DB_PORT=8086
INFLUX_DB_NAME='Zisterne'
INFLUX_DB_USER='admin'
INFLUX_DB_PASSWORD='influx'


# BCM GPIO-Referenen verwenden (anstelle der Pin-Nummern)
# und GPIO-Eingang definieren
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.remove_event_detect(ECHO)
GPIO.output(TRIG, False)
time.sleep(1)                   # Setup-Zeit fuer Sensor

stopp = 0                       # Variableninit
start = 0
distance = 0

def pulse():                    # Funktion zum Starten der Messung
  global start
  global stopp
  global distance

  GPIO.output(TRIG, True)       # Triggerimpuls  erzeugen
  time.sleep(PULSE)
  GPIO.output(TRIG, False)
  stopp = 0                     # Werte auf 0 setzen
  start = 0
  distance = 0                  # und Event starten


def measure(x):                 # Callback-Funktion fuer ECHO
  global start
  global stopp
  global distance
  if GPIO.input(ECHO) == 1:     # steigende Flanke, Startzeit speichern
    start = time.time()
  else:                         # fallende Flanke, Endezeit speichern
    stopp = time.time()
    delta = stopp - start       # Zeitdifferenz und Entfernung berechnen
    distance = delta * SPEED_2

def calc_volume(dist):             # Calculates the volume based on distance
  return int((ZISTERNE_LOW - dist) / (ZISTERNE_LOW - ZISTERNE_HIGH) * ZISTERNE_VOLUME)


def measure_range():            # Measures and returns Median
  values = []
  for i in range(0, BURST):
    pulse()                     # Start measure
    time.sleep(0.040)           # Wait until complete
    values.append(distance)     # store value
    print("Distance: %1.1f" % distance) # Kontrollausgabe
    time.sleep(0.05)
  return statistics.median(values);             # Return Median

def write_to_db(dist, volume, percent):
    client = InfluxDBClient(INFLUX_DB_HOST, INFLUX_DB_PORT, INFLUX_DB_USER, INFLUX_DB_PASSWORD, INFLUX_DB_NAME)
    now = datetime.datetime.now()
    json_body = [
        {
            "measurement": "zisterne_fuellstand",
            "tags": {
                "host": "Haus",
                "region": "Germany"
            },
            "time": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "fields": { "fuellstand" : dist,
                        "volumen" : volume,
                        "percent" : percent}
        }
    ]
    print("Write Points to Influx dist = %1.1f, volume = %1.1f, percent = %1.1f" % (dist, volume, percent))
    client.write_points(json_body)

# main loop
try:
  GPIO.add_event_detect(ECHO, GPIO.BOTH, callback=measure)
  while True:
    dist = round(measure_range(), 1)
    volume = calc_volume(dist)
    percent = int(volume / ZISTERNE_VOLUME * 100)
    print("Range = %1.1f cm" % dist)
    write_to_db(ZISTERNE_LOW - dist, volume, percent)
    time.sleep(SLEEP_TIME)

# reset GPIO settings if user pressed Ctrl+C
except KeyboardInterrupt:
  print("Bye!")
  GPIO.cleanup()
