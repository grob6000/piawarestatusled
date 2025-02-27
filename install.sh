#!/bin/bash
echo INSTALLING PIAWARE STATUS LED DAEMON
sudo python3 -m pip install requests rpi_ws281x
sudo mkdir /home/pi/piawarestatusled
sudo cp ./piawarestatusled.py /home/pi/piawarestatusled/piawarestatusled.py
sudo cp ./piawarestatusled.service /etc/systemd/system/piawarestatusled.service
sudo chmod +x /etc/systemd/system/piawarestatusled.service
sudo systemctl daemon-reload
sudo systemctl enable piawarestatusled.service
sudo systemctl restart piawarestatusled.service
sudo systemctl status piawarestatusled.service
echo DONE!