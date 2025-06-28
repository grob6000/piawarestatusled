import requests
import time
#from rpi_ws281x import PixelStrip, Color
from pi5neo import Pi5Neo
import sys
import signal

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

# consts
url = "http://127.0.0.1/status.json"

#colormap = { "green":Color(0,255,0), "amber":Color(164,104,0), "red":Color(255,0,0), "blue":Color(0,0,255), "off":Color(0,0,0) }
colormap = { "green":     (0,255,0), "amber":     (164,104,0), "red":     (255,0,0), "blue":(0,0,255), "off":(0,0,0) }

pin = 10
bright = 255
pollinterval = 5
loginterval = 12

if __name__ == "__main__":

  #strip = PixelStrip(4, pin, 800000, 10, False, bright, 0)
  #strip.begin()
  neo = Pi5Neo('/dev/spidev0.0', 5, 800)

  eprint("ws281x initialized", "pin:", pin, "bright:", bright, "pollinterval:", pollinterval)
  
  # test / init
  for c in colormap.values():
    neo.fill_strip(c[0], c[1], c[2])
    #for px in range(0,4):
      #strip.setPixelColor(px, colormap[c])
    #strip.show()
    neo.update_strip()
    time.sleep(1)
  
  i = 0
  badrequests = 0

  shuffleoffthismortalcoil = KillMe()

  while not shuffleoffthismortalcoil.kill_now:

    requestok = True
    dataok = False
    s_radio = "off"
    s_piaware = "off"
    s_flightaware = "off"
    s_mlat = "off"

    try:
      response = requests.get(url)
      status = response.json()
    except:
      requestok = False
    
    if requestok:
      # get data from request
      dataok = ("radio" in status and "piaware" in status and "adept" in status and "mlat" in status)

    if requestok and dataok:
      # parse json
      s_radio = str(status["radio"]["status"])
      s_piaware = str(status["piaware"]["status"])
      s_flightaware = str(status["adept"]["status"])
      s_gps = str(status["gps"]["status"])
      s_mlat = str(status["mlat"]["status"])
      s = (s_radio, s_piaware, s_flightaware, s_gps, s_mlat)
      # set leds
      for px in range(0,5):
        if (s[px] in colormap):
          #strip.setPixelColor(i, colormap[s_radio])
          c = colormap[s[px]]
          neo.set_led_color(px, c[0], c[1], c[2])
      #strip.show()
      neo.update_strip()
    else:
      # rolling red chaser for bad connection
      for px in range(0,5):
        if i%4==px:
          #strip.setPixelColor(px, colormap["red"])
          neo.set_led_color(px, 255, 0, 0)
        else:
          #strip.setPixelColor(px, colormap["off"]) 
          neo.set_led_color(px, 0, 0, 0)
      #strip.show()
      neo.update_strip()

    i = i+1
    if not requestok:
      badrequests = badrequests+1

    if i % loginterval == 0:
      eprint("requests:", i, "bad:", badrequests, "radio:", s_radio, "piaware:", s_piaware, "flightaware:", s_flightaware, "mlat:", s_mlat)

    #wait
    time.sleep(pollinterval)

  # death - ideally indicate not running by killing the lights
  #for px in range(0,4):
  #  strip.setPixelColor(px, colormap["off"])
  #strip.show()
  neo.fill_strip(0, 0, 0)
  eprint("this parrot is no more")
