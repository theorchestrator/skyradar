import math
import datetime
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from opensky_api import OpenSkyApi
from pyflightdata import FlightData


#TODO: Implement function to dynamically change location (LONG/LAT COODRDS)
#      Implement ALEXA functionality and return name and info about the closest aircraft. Possibly ask about certain aicraft?

OSAPI = OpenSkyApi()
FR24API = FlightData()
URL = "https://data-live.flightradar24.com/zones/fcgi/feed.js?bounds=58.53,40.93,-15.72,31.85&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=14400&gliders=1&stats=1"

#Set User-Agent to avoid 403 error
request = requests.get(URL, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"})


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def generate_bbox(longLatTuple):
    latMin = truncate((longLatTuple[1] - offset), 3)
    latMax = truncate((longLatTuple[1] + offset), 3)
    longMin = truncate((longLatTuple[0] - offset), 3)
    longMax = truncate((longLatTuple[0] + offset), 3)

    states = OSAPI.get_states(bbox=(latMin, latMax, longMin, longMax))
    return states


rbpos_LongLat = 9.02153492, 50.14297105
offset = 0.2 #0.012 for accuracy (above you)
today = datetime.today()
current_time = today.strftime('%Y%m%d') # format "YYYYMMDD"

# Parse FR24 JSON and remove junk
FDList = list(request.json().values())
FDList.remove(FDList[1])
FDList.remove(FDList[0])
FDList.remove(FDList[len(FDList)-1])

flightVectors = generate_bbox(rbpos_LongLat)

for state in flightVectors.states:
    callsign = state.callsign.rstrip()
    #print(callsign)

    for list in FDList:
        newList = []

        for elem in list:
            newList.append(str(elem))
        
        if callsign in newList:
            #print(list)
            realcallsign = list[13]
            realcallsign = realcallsign.lstrip()
            realcallsign = realcallsign.rstrip()

            flight = FR24API.get_flight_for_date(realcallsign, current_time)

            for dict in flight:
                if(dict["status"]["live"] == True): #only check for live flights
                    #print(dict)
                    #print(dict.keys()) 

                    dest_time = (datetime.now().hour * 100) + datetime.now().minute
                    a = dict["time"]["other"]["eta_time"]
                    b = str(dest_time)
                    time1 = datetime.strptime(a,"%H%M")
                    time2 = datetime.strptime(b,"%H%M") 
                    diff = time1 - time2
                    seconds = (diff.total_seconds())
                    h = seconds // 3600
                    m = (seconds % 3600) // 60      

                    #Outputs: LH1279 | ATH -> FRA with aircraft: Airbus A321-271NX landing in: 00:05h
                    print( realcallsign, "|", dict["airport"]["origin"]["code"]["iata"], "->", dict["airport"]["destination"]["code"]["iata"], 
                    "with aircraft:", dict["aircraft"]["model"]["text"], "landing in: " "%02d:%02d" %(h, m) + "h")