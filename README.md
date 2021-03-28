# Temprature Logger

This application logs data from a series of DHT22 sensors.

Installation:

    cd /tmp
    wget https://github.com/davemacrae/temp_logger/archive/master.zip
    unzip master.zip
    sudo mv temp_logger-master/logger.py /usr/local/bin
    sudo systemctl logging restart

First time install:

	cd /opt
	sudo wget https://github.com/prometheus/node_exporter/releases/download/v1.1.2/node_exporter-1.1.2.linux-armv6.tar.gz
	sudo tar zxvf node_exporter-1.1.2.linux-armv6.tar.gz
	sudo rm node_exporter-1.1.2.linux-armv6.tar.gz
	sudo mv node_exporter* node_exporter

	cd /tmp
	sudo apt install -y git pigpiod

	pip3 install pigpio_dht

	wget https://github.com/davemacrae/temp_logger/archive/master.zip
	unzip master.zip
	sudo mv temp_logger-master/logger.py /usr/local/bin
	sudo mv temp_logger-master/logging.service /etc/systemd/system
	sudo mv temp_logger-master/node_exporter.service /etc/systemd/system

	sudo systemctl daemon-reload
	sudo systemctl enable logging
	sudo systemctl start logging
	sudo systemctl enable node_exporter
	sudo systemctl start node_exporter

	sudo systemctl disable hciuart 

	git clone https://github.com/JemRF/rf_tools.git

	sudo apt-get install -y python-serial python-numpy python3-serial python3-numpy 

	sudo service hciuart stop
	sudo systemctl disable hciuart.service


Still a work in progress.

