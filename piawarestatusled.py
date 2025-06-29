import requests
import time
from rpi_ws281x import PixelStrip, Color
from pi5neo import Pi5Neo
import sys
import signal
from configparser import ConfigParser


class KillMe:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True

# stderr print
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

# color map (R,G,B)
colormap   = { "green":(0,255,0), "amber":(164,104,0), "red":(255,0,0), "blue":(0,0,255), "off":(0,0,0) }

# default config
url = "http://127.0.0.1/status.json"
pin = 10
bright = 255
pollinterval = 10 # seconds, approx
loginterval = 600 # seconds, approx - try to be divisible by pollinterval
frequency = 800 # khz
indicators = {"radio":0, "piaware":1, "adept":2, "gps":3, "mlat":4}

# globals
neo = None
strip = None
stripsize = 0

def detect_model() -> str:
    with open('/proc/device-tree/model') as f:
        model = f.read()
        eprint("Detected model:", model)
    return model

def do_set_led(ledindex, colortuple):
  global neo, strip, brightness
  if neo:
    neo.set_led_color(ledindex, int(colortuple[0]*brightness/255), int(colortuple[1]*brightness/255), int(colortuple[2]*brightness/255))
    #eprint("set led:", ledindex, int(colortuple[0]*brightness/255), int(colortuple[1]*brightness/255), int(colortuple[2]*brightness/255))
  if strip:
    strip.setPixelColorRGB(ledindex, colortuple[0], colortuple[1], colortuple[2])

def do_set_strip(colortuple):
  global neo, strip, brightness, stripsize
  if neo:
    neo.fill_strip(int(colortuple[0]*brightness/255), int(colortuple[1]*brightness/255), int(colortuple[2]*brightness/255))
  if strip:
    for ledindex in range(0, stripsize):
      strip.setPixelColorRGB(ledindex, colortuple[0], colortuple[1], colortuple[2])  

def do_update_strip():
  global neo, strip
  if neo:
    neo.update_strip()
  if strip:
    strip.show()

if __name__ == "__main__":
  
  # load config
  config = ConfigParser()
  config.read("./piawarestatusled.ini")
  if "source" in config:
    if "url" in config["source"]:
      url = config["source"]["url"]
  if "strip" in config:
    if "frequency" in config["strip"]:
      frequency = int(config["strip"]["frequency"])
    if "pollinterval" in config["strip"]:
      pollinterval = int(config["strip"]["pollinterval"])
    if "brightness" in config["strip"]:
      brightness = int(config["strip"]["brightness"])
    if "pin" in config["strip"]:
      pin = int(config["strip"]["pin"])
  if "indicators" in config:
    indicators = {}
    for v in config["indicators"]:
      indicators[v] = int(config["indicators"][v])

  # automatically select required strip size 
  stripsize = 1
  for k, v in indicators.items():
    if v+1 > stripsize:
      stripsize = v+1

  strip = None
  neo = None

  if "Raspberry Pi 5" in detect_model():
    neo = Pi5Neo('/dev/spidev0.0', stripsize, 800)
    eprint("pi5neo initialized", "pin:", "10 (SPI MOSI)", "bright", brightness, "size:", stripsize)
  else:
    strip = PixelStrip(stripsize, pin, frequency*1000, 10, False, bright, 0)
    strip.begin()
    eprint("ws281x initialized", "pin:", pin, "bright:", bright, "size:", stripsize)
  
  # test pattern on start
  for c in colormap.values():
    do_set_strip(c)
    do_update_strip()
    time.sleep(1)
  
  # process values
  i = 0
  badrequests = 0
  shuffleoffthismortalcoil = KillMe()
  datalog = {}

  while not shuffleoffthismortalcoil.kill_now:

    # get data
    requestok = True
    displaychanged = False
    
    try:
      response = requests.get(url)
      status = response.json()
    except:
      requestok = False
    
    if requestok:
      # parse json for configured indicators
      for indicatorname, ledindex in indicators.items():
        do_set_led(ledindex, colormap["off"]) # default is off
        if k in status:
          if "status" in status[indicatorname]:
            colorname = status[indicatorname]["status"]
            if colorname in colormap:
              do_set_led(ledindex, colormap[colorname])
              if not (indicatorname in datalog and datalog[indicatorname] == colorname):
                displaychanged = True
              datalog[indicatorname] = colorname

      do_update_strip()
    else:
      # rolling red chaser for bad connection
      do_set_strip(colormap["off"])
      do_set_led(i%stripsize, colormap["red"])
      do_update_strip()

    i = i+1
    if not requestok:
      badrequests = badrequests+1

    # logging
    if displaychanged or (loginterval > 0 and i%(int(loginterval/pollinterval)) == 0): 
      logstring = "requests={0} bad={1}".format(i, badrequests)
      for iname, cname in datalog.items():
        logstring = logstring + " {0}={1}".format(iname, cname)
      eprint(logstring)

    # wait
    time.sleep(pollinterval)

  # death - ideally indicate not running by killing the lights
  do_set_strip(colormap["off"])
  do_update_strip()
  eprint("this parrot is no more")
