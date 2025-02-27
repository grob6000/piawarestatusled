import requests
import time
from rpi_ws281x import PixelStrip, Color
import sys

# stderr print
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

# consts
url = "http://127.0.0.1/status.json"

colormap = { "green":Color(0,255,0), "amber":Color(164,104,0), "red":Color(255,0,0), "blue":Color(0,0,255), "off":Color(0,0,0) }
pin = 18
bright = 64
pollinterval = 5
loginterval = 12

if __name__ == "__main__":

  strip = PixelStrip(4, pin, 800000, 10, False, bright, 0)
  strip.begin()

  eprint("ws281x initialized", "pin:", pin, "bright:", bright, "pollinterval:", pollinterval)
  
  # test / init
  for c in colormap:
    for px in range(0,4):
      strip.setPixelColor(px, colormap[c])
    strip.show()
    time.sleep(1)
  
  i = 0
  badrequests = 0

  while (True):

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
      s_mlat = str(status["mlat"]["status"])
      #eprint("received status: ", s_radio, s_piaware, s_flightaware, s_mlat)
      # set leds
      if (s_radio in colormap):
        strip.setPixelColor(0, colormap[s_radio])
      if (s_piaware in colormap):
        strip.setPixelColor(1, colormap[s_piaware])
      if (s_flightaware in colormap):
        strip.setPixelColor(2, colormap[s_flightaware])
      if (s_mlat in colormap):
        strip.setPixelColor(3, colormap[s_mlat])
      strip.show()
    else:
      # rolling red chaser for bad connection
      for px in range(0,4):
        if i%4==px:
          strip.setPixelColor(px, colormap["red"])      
        else:
          strip.setPixelColor(px, colormap["off"]) 
      strip.show()
    
    i = i+1
    if not requestok:
      badrequests = badrequests+1

    if i % loginterval == 0:
      eprint("requests:", i, "bad:", badrequests, "radio:", s_radio, "piaware:", s_piaware, "flightaware:", s_flightaware, "mlat:", s_mlat)

    #wait
    time.sleep(pollinterval)
