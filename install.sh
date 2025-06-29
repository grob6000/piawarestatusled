#!/bin/bash
echo INSTALLING PIAWARE STATUS LED DAEMON
echo copying files...
sudo mkdir /usr/bin/piawarestatusled
sudo cp ./piawarestatusled.py /usr/bin/piawarestatusled/piawarestatusled.py
sudo cp ./piawarestatusled.ini /usr/bin/piawarestatusled/piawarestatusled.ini
sudo cp ./piawarestatusled.service /etc/systemd/system/piawarestatusled.service
sudo chmod +x /etc/systemd/system/piawarestatusled.service
echo setting up python venv...
sudo python3 -m venv /usr/bin/piawarestatusled/venv
sudo /usr/bin/piawarestatusled/venv/bin/pip install requests rpi_ws281x pi5neo
sudo systemctl daemon-reload
sudo systemctl enable piawarestatusled.service
sudo systemctl restart piawarestatusled.service
sudo dtparam spi=on
echo done. IF USING SPI: Please enable SPI raspi-config / 3. interfaces / 4. spi / ON and reboot