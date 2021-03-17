#!/usr/bin/python3
"""
Logs sensor data to Database
"""
# imports sections
import os
import time
import sys
import sqlite3
from sqlite3 import Error
# import inspect

from pigpio_dht import DHT22
import pigpio

# constants section

DHT_PIN_1 = 4                       # GPIO PIN for Sensor 1
DHT_PIN_2 = 17                      # GPIO PIN for Sensor 2

DB_FILE = "sensor_log.db"
CREATE_SENSOR = "CREATE TABLE IF NOT EXISTS sensors (" \
                "id integer PRIMARY KEY, " \
                "name text NOT NULL, " \
                "sensor_type text," \
                "dht22_pin int," \
                "UNIQUE (name)" \
                ");"

CREATE_LOG = "CREATE TABLE IF NOT EXISTS log (" \
             "id integer PRIMARY KEY, " \
             "sensor_id int, " \
             "temperature real, " \
             "humidity real, " \
             "pressure real, " \
             "date int, " \
             "time int, " \
             "FOREIGN KEY (sensor_id) REFERENCES sensors (id)" \
             ");"


def db_connect(db_file):
    """
    We need to create a connection to the database. THis will create the DB if it doesn't
    already exists
    :param db_file: The name of the database we are connection to
    :return: db_file connection or None
    """

    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as error:
        print(error)

    return conn


def db_close(connection_id):
    """
    Close the database connection
    :param connection_id: Database connection ID
    :return: None
    """
    connection_id.close()


def db_create_table(connection_id, sql):
    """
    Connect to the database (which creates it if necessary)
    CReate the tables we want in the database

    :param sql: SQL command to create table
    :param connection_id:
    :return: None
    """

    try:
        connection = connection_id.cursor()
        connection.execute(sql)
    except Error as error:
        print(error)


def db_add_sensor(connection_id, data):
    """
    Insert data into databas table sensor
    Check that the sensor doesn't already exist first
        select from sensors where name = XXX
    :param data: data to be inserted
    :param connection_id:
    :return: None
    """

    if data[1] == "DHT22":
        sql = "INSERT INTO sensors (name, sensor_type, dht22_pin) VALUES (?, ?, ?)"
    else:
        sql = "INSERT INTO sensors (name, sensor_type) VALUES (?, ?)"

    cur = connection_id.cursor()
    try:
        cur.execute(sql, data)
        connection_id.commit()
    except Error as error:
        print(error)


def capture_dht22_data(connection_id):
    """
    Capture data from sensor and save it in database
        select sensors from database
        get data based on PIN ID
    :return:
    """
    sql = "SELECT id, dht22_pin from sensors WHERE sensor_type = 'DHT22' ORDER BY id"
    cur = connection_id.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()

        pitemp = pigpio.pi('pitemp')

        sensors = []
        ids = []
        i = 0

        for row in rows:
            ids.append(row[0])
            # noinspection PyTypeChecker
            sensors.append(DHT22(row[1], timeout_secs=5, pi=pitemp))
            i = i + 1

        while True:
            cur_date = time.strftime('%Y-%m-%d')
            cur_time = time.strftime('%H:%M')

            results = []
            for sensor in range(0, len(sensors)):
                try:
                    result = sensors[sensor].sample(samples=5, max_retries=5)
                    results.append(result)
                    # as we are reading multiple sensors, introduce a little sleep between the readings.
                    # this seems to cut down on the number of timeouts and False status values.
                    time.sleep(2)
                except TimeoutError:
                    print("Timout on sensor " + str(sensor))
                    # Create some dummy values for logging purposes
                    results.append({'temp_c': 0, 'temp_f': 0, 'humidity': 0, 'valid': False})
                    log_data(connection_id, ids[sensor], 0, 0, None, cur_date, cur_time)
                else:
                    print(result)
                    log_data(connection_id, ids[sensor], result['humidity'], result['temp_c'], None, cur_date, cur_time)
                pass

            prometheus_log(results)
            time.sleep(120)
    except Error as error:
        print(error)


def prometheus_log(results):
    """
    Logs the data in Prometheus Format as per: https://opensource.com/article/21/3/iot-measure-raspberry-pi

    Relies on node_exporter catching the file at least one per minute.

    :param results: array of {'temp_c': 26.3, 'temp_f': 79.3, 'humidity': 38.9, 'valid': True}
    :return:
    """

    PROMETHEUS_LOG = "/home/pi/logs/metrics.prom"

    metrics_out = open(PROMETHEUS_LOG, 'w+')
    for i in range(0, len(results)):
        print(f'# HELP temperature{i} Temperature in Centigrade', flush=True, file=metrics_out)
        print(f'# TYPE temperature{i} gauge', flush=True, file=metrics_out)
        print(f"temperature{i} {results[i]['temp_c']}", flush=True, file=metrics_out)
        print(f'# HELP pressure{i} something', flush=True, file=metrics_out)
        print(f'# TYPE pressure{i} gauge', flush=True, file=metrics_out)
        print(f'pressure{i} 0', flush=True, file=metrics_out)
        print(f'# HELP humidity{i} Humidity in %RH', flush=True, file=metrics_out)
        print(f'# TYPE humidity{i} gauge', flush=True, file=metrics_out)
        print(f"humidity{i} {results[i]['humidity']}", flush=True, file=metrics_out)

    metrics_out.close()


def log_data(connection_id, sensor_id, humidity, temperature, pressure, cdate, ctime):
    """
    Log data received by sensor
    :param connection_id:
    :param sensor_id:
    :param humidity:
    :param temperature:
    :param pressure:
    :param cdate:
    :param ctime:
    :return:
    """

    sql = "INSERT INTO log (sensor_id, temperature, humidity, pressure, date, time) VALUES (?, ?, ?, ?, ?, ?)"
    cur = connection_id.cursor()
    try:
        cur.execute(sql, (sensor_id, temperature, humidity, pressure, cdate, ctime))
        connection_id.commit()
    except Error as error:
        print(error)


def database_setup():
    """
    Create the database and add entries for known sensors.
    :return:
    """
    # Create the database and add the tables. Has no real affect if already done.
    connection_id = db_connect(DB_FILE)
    if connection_id is not None:
        db_create_table(connection_id, CREATE_SENSOR)
        db_create_table(connection_id, CREATE_LOG)
        db_add_sensor(connection_id, ('inside', "DHT22", DHT_PIN_1))
        db_add_sensor(connection_id, ('outside', "DHT22", DHT_PIN_2))
    else:
        print("database connection seems to have failed")
    return connection_id


def main():
    """
    Main function
    :return:
    """

    connection_id = database_setup()
    if connection_id is not None:
        capture_dht22_data(connection_id)
        db_close(connection_id)


if __name__ == '__main__':
    # TODO:
    #   Switch to using native DHT22 interface rather than pigpio_dht

    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(1)
        except SystemExit:
            # noinspection PyProtectedMember
            os._exit(1)
    sys.exit(0)
