# PiAware Status LED #
Python script daemon to operate a WS281X led strip as a status indicator for PiAware
## Setup ##
- Use 4x WS281X leds, or a strip of 4 (at least).
- Connect pins (as per any tutorial for neopixels with RPi) to GPIO18, GND and 5V on the GPIO header
## Installation ##
- Clone this repo onto the piaware device (you will need to enable ssh)
- Install using included `install.sh` script
## Use ##
You should see a cycle of colours when the script begins (daemon should be enabled to start on boot)
Colours of 4x LEDs will then be updated every 5 seconds, matching the main page of piaware status (radio status, piaware status, flightaware status, mlat status)
A slow cycling red led means the script is not successful in connecting to piaware - it is probably not running!
## Customisation ##
You can edit the python script, most of the adjustable stuff is up the front. Have at it.
