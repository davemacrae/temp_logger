# Temprature Logger

This application logs data from a series of DHT22 sensors.

Installation:

    cd /tmp
    wget https://github.com/davemacrae/temp_logger/archive/master.zip
    unzip master.zip
    sudo mv temp_logger-master/logger.py /usr/local/bin
    sudo systemctl logging restart

First time install:

    wget https://github.com/davemacrae/temp_logger/archive/master.zip
    unzip master.zip
    sudo mv temp_logger-master/logger.py /usr/local/bin
    sudo mv temp_logger-master/logging.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable logging
    sudo systemctl start logging

Still a work in progress.

