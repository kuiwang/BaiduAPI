# -*- coding: utf-8 -*-

# Baidu Geocoder

# Service Provider: Baidu, Inc.
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft provided instructions
# License: Academic use only
# Requirement: Python 3.x

import urllib.request, json, codecs, os, sys, MapProjection
from datetime import datetime

# Utils function
def DownloadPage(url, path):
    try:
        print(url)
        conn = urllib.request.urlopen(url)
        fw = open(path, 'wb')
        fw.write(conn.read())
        fw.close()
    except:
        print("Page not found")
        return

def Geocode(apikey, city, address):
    url = str.format("http://api.map.baidu.com/geocoder/v2/?ak={0}&output=json&city={1}&address={2}", apikey, urllib.parse.quote(city), urllib.parse.quote(address))
    DownloadPage(url, "temp.txt")
    f = codecs.open("temp.txt", "r", encoding = "utf-8")
    data = json.loads(f.read())
    f.close()  
        
    lat_bd09 = lon_bd09 = lat_wgs84 = lon_wgs84 = precise = confidence = level = ''
    
    if 'result' in data:
        r = data['result']
        
        if 'location' in r:                
            lat_bd09 = r['location']['lat']            
            lon_bd09 = r['location']['lng']
            
            # BD09 to WGS04 conversion
            gcj02 = MapProjection.BD09ToGCJ02(lat_bd09, lon_bd09)
            wgs84 = MapProjection.GCJ02ToWGS84_Exact(gcj02['lat'], gcj02['lon'])
            lat_wgs84 = wgs84['lat']
            lon_wgs84 = wgs84['lon']
            
        if 'precise' in r:
            precise = r['precise']
            
        if 'confidence' in r:
            confidence = r['confidence']
            
        if 'level' in r:
            level = r['level']

    return str.format("{0},{1},{2},{3},{4},{5},{6}", lat_bd09, lon_bd09, lat_wgs84, lon_wgs84, precise, confidence, level)

def Process(apikey, city):
    start = datetime.now()
    print(str.format("Geocoding address in {0} ({1})", city, start))

    f_in = codecs.open("Input/Address.csv", "r", encoding = "utf-8-sig")
    f_out = codecs.open("Output/Geocoded Address.csv", "w", encoding = "utf-8-sig")
    f_out.write("OBJECTID,Address,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84,Precise,Confidence,Level\n")

    f_err = codecs.open("Output/Geocoding Error.csv", "w", encoding = "utf-8-sig")
    f_err.write("OBJECTID,ADDRESS\n")

    err = 0
    for f in f_in.readlines()[1:]:
        try:
            [oid, address] = f.strip().split(',')            
            geocode = Geocode(apikey, city, address)
            f_out.write(str.format("{0},{1},{2}\n", oid, address, geocode))
        except:
            f_err.write(f)
            err += 1
            continue

    f_in.close()            
    f_out.close()
    f_err.close()
    
    if os.path.exists("temp.txt"):
        os.remove("temp.txt")
    if err == 0:
        os.remove("Output/Geocoding Error.csv")

    end = datetime.now()
    print(str.format("Completed ({0})", end))
    print(str.format("Error: {0}", err))
    print(str.format("Duration: {0}", end - start))    

if __name__ == '__main__':
    # Configuration
    print("========== Configuration ==========")
    
    f_key = codecs.open("Config/API Key.csv", "r", encoding = "utf-8-sig")
    apikey = f_key.readlines()[1].strip().split(',')[1]
    f_key.close()

    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&from=1&to=5&coords=113,23", apikey)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    if data['status'] != 0:
        print("Invalid API key.")
        sys.exit(1)

    cities = []
    f_city = codecs.open("Config/City.csv", "r", encoding = "utf-8-sig")
    for f in f_city.readlines()[1:]:
        r = f.strip().split(',')
        cities.append(r[1])
    
    city = input("City: ")
    if city not in cities:
        print("Error: Invalid city.")
        sys.exit(1)    

    # Geocode address
    print("========== Process ==========")
    Process(apikey, city)
