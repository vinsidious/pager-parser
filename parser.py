import sys
from pymongo import MongoClient
import datetime
import time
import arrow
import geocoder
import mods

def parse_disp(dispatch):
    
    # Conserves the original page by assigning it to the variable "raw_page" before any modifications are performed
    raw_page = dispatch
    
    # Returns the page without ' - From ' suffix OR returns '0' if not a legitimate VC page or if just a message page     
    page = mods.from_vc(dispatch)
    
    # Gets rid of 'message only' pages
    if not page:
        return None
    
    # Fixes the three letter city codes in the VC pages
    page = mods.fix_cities(page, mods.replace_dict)
    
    # Returns the call type
    type = mods.get_type(page)
    aid_calls = ['AID', 'ACC', 'SHOT', 'STAB', 'CPR', 'DOA', 'OBV', 'DROWN', 'MEDIC', 'ODF', 'ODMDF', 'RESCUE', 'SERVIC']
    if any(x in type for x in aid_calls):
        cat = 'Aid'
    else:
        cat = 'Fire'    
    # Returns the address, place name (if any), and apt/ste number (if any)
    address_whole = mods.get_address(page)
    place = address_whole['Place']
    unit_num = address_whole['Unit']
    address = address_whole['Address']
    
    # Maintain the raw address for dispatching purposes as 'raw_add'
    comma = address.find(', ')
    raw_add = address[:comma]
    
    # Returns the units
    units = mods.get_units(page)
    units = mods.fix_units(units)
    
    # Returns the department
    dept = mods.get_dept(page)
    nh = ['E18', 'E19', 'E191', 'A18']
    if set(nh) & set(units):
        dept = 'Highline'
    
    # Get latitude and longitude
    g = geocoder.google(address + ', WA')
    latlng = [g.lat, g.lng]
    postal = g.postal
    city = g.city
    
    # Append the zip code to the address, but only if geocoder is confident of the results
    
    # Assign the current date/time to the variable 'timestamp'
    isotime = str(arrow.now('US/Pacific'))
    i = str(arrow.now('US/Pacific').format('HH:mm'))
    hourago = str(arrow.now('US/Pacific').replace(hours=-1))

    client = MongoClient()
    db = client.mydb
    collection = db.dispatch

    collection.find_and_modify(query={'Address': address,'TimestampISO': {'$gte': hourago,'$lte': isotime}},update={'$addToSet': {'Units': {'$each': units}},'$set': {'Address': address,'Type': type,'Category': cat,'Department': dept,'Coordinates': latlng,'Timestamp': i,'TimestampISO': isotime,'raw_add': raw_add,'place_name': place,'unit_num': unit_num}}, upsert=True)

parse_disp(sys.argv[1])