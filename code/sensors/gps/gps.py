import os
import math
from gps3 import gps3


def deg2rad(deg):
    return deg * (math.pi / 180)


def getDistanceFromLatLonInMeter(lat1, lon1, lat2, lon2):
    EARTH_RADIUS_KM = 6371
    dLat = deg2rad(lat2 - lat1)  # deg2rad below
    dLon = deg2rad(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) \
        + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) \
        * math.sin(dLon / 2) * math.sin(dLon / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = (EARTH_RADIUS_KM * c) * 1000  # Distance in km
    return d


gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()

latlon_values = []

for new_data in gps_socket:
    if new_data:
        os.system('clear')
        data_stream.unpack(new_data)

        latlon_values.append({
            'lat': data_stream.TPV.get('lat'),
            'lon': data_stream.TPV.get('lon')
        })

        if(len(latlon_values) > 2):
            lat1 = latlon_values[-1].get('lat')
            lon1 = latlon_values[-1].get('lon')
            lat2 = latlon_values[-2].get('lat')
            lon2 = latlon_values[-2].get('lon')

            if(lat1 != 'n/a' and lon1 != 'n/a' and lat2 != 'n/a' and lon2 != 'n/a'):
                lat1 = float(lat1)
                lon1 = float(lon1)
                lat2 = float(lat2)
                lon2 = float(lon2)
                distance = getDistanceFromLatLonInMeter(lat1, lon1, lat2, lon2)

                print('distance walked: %s' % distance)

        print('device = ', data_stream.TPV.get('device'))
        print('status = ', data_stream.TPV.get('status'))
        print('mode = ', data_stream.TPV.get('mode'))
        print('time = ', data_stream.TPV.get('time'))
        print('ept = ', data_stream.TPV.get('ept'))
        print('lat = ', data_stream.TPV.get('lat'))
        print('lon = ', data_stream.TPV.get('lon'))
        print('alt = ', data_stream.TPV.get('alt'))
        print('epx = ', data_stream.TPV.get('epx'))
        print('epy = ', data_stream.TPV.get('epy'))
        print('epv = ', data_stream.TPV.get('epv'))
        print('track = ', data_stream.TPV.get('track'))
        print('speed = ', data_stream.TPV.get('speed'))
        print('epd = ', data_stream.TPV.get('epd'))
        print('eps = ', data_stream.TPV.get('eps'))
        print('epc = ', data_stream.TPV.get('epc'))
        print('-------------------------------')
        print('time = ', data_stream.SKY.get('time'))
        print('xdop = ', data_stream.SKY.get('xdop'))
        print('ydop = ', data_stream.SKY.get('ydop'))
        print('vdop = ', data_stream.SKY.get('vdop'))
        print('tdop = ', data_stream.SKY.get('tdop'))
        print('hdop = ', data_stream.SKY.get('hdop'))
        print('gdop = ', data_stream.SKY.get('gdop'))
        print('satellites = ', data_stream.SKY.get('satellites'))
        print('# satellites = ', len(data_stream.SKY.get('satellites')))


