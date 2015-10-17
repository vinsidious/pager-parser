import sys
from collections import OrderedDict
from pymongo import MongoClient
import re

# Determines whether or not a page is actually from Valley Com as opposed to random spam, etc.
def from_vc(dispatch):
    required = " - From "
    also_required = "DISPATCH:"
    if required not in dispatch:
        return None
    elif also_required not in dispatch:
        return None
    else:
        cutoff = dispatch.find(required)
        return dispatch[:cutoff]

def fix_cities(text, replace_dict):
    
    # Perform replacement and return original with replacements
    for key in replace_dict:
        text = text.replace(key, replace_dict[key])
    return text
                    
def get_type(page):
    colon = page.find(':')
    colon += 1
    comma = page.find(',')
    return page[colon:comma]
    
def get_units(page):
    find_me = page.rfind(':')
    find_me += 1
    units = page[find_me:]
    units = units.split(', ')
    return units
    
def get_address(page):
    page = str(page)
    separated = page.split(', ')
    if 'btwn' in page:
        if '#' in separated[2]:
            hashtag = separated[2].find(' #')
            separated[2] = separated[2][:hashtag]
        physical = str(separated[2] + ', ' + separated[3])
    elif ' <' in page:
        physical = str(separated[2] + ', ' + separated[3])
    elif ', at' not in page:
        if 'btwn' not in page:
            if '<' not in page:
                physical = str(separated[2] + ', ' + separated[3])
    elif ', at ' and not ' <' in page:
        if '#' in separated[4]:
            hashtag = separated[4].find(' #')
            separated[4] = separated[4][:hashtag]
        physical = str(separated[4][3:] + ', ' + separated[5])
        
    if '<' in page:
        place = None
    elif 'btwn' in page:
        place = None
    elif ', at' not in page:
        if 'btwn' not in page:
            if '<' not in page:
                place = None
    elif ', at ' and not ('<' and "#") in page:
        place = str(separated[2])
    elif ', at ' and '#' in page:
        hashtag = separated[2].find(' #')
        pl_name = separated[2]
        place = str(pl_name[:hashtag])
    else:
        place = None
        
    if '#' in page:
        hashtag = page.find('#')
        hereon = page[hashtag:]
        comma = hereon.find(',')
        unit = str(hereon[:comma])
    else:
        unit = None
        
    return {'Place' : place, 'Unit' : unit, 'Address' : physical}

def get_dept(page):
    sliced = page[:27]
    if ', RF' in sliced:
        dept = "Renton"
    elif ', WF' in sliced:
        dept = "South King"
    elif ', MF' in sliced:
        dept = "Maple Valley"
    elif ', KF' in sliced:
        dept = "Kent"
    elif ', YF' in sliced:
        dept = "Vashon"
    elif ', SF' in sliced:
        dept = "Skyway"
    elif ', TF' in sliced:
        dept = "Tukwila"
    elif ', VF' in sliced:
        dept = "District #44"
    elif ', ZF' in sliced:
        dept = "District #47"
    elif ', AF' in sliced:
        dept = "VRFA"
    elif ', UF' in sliced:
        dept = "Burien"
    elif ', MD' in sliced:
        dept = "Medic One"
    return dept

def fix_units(units):
#    units = ' '.join(units)
    tolist = []
    for num in units:
        a = re.sub('TRI\d+', 'TRI', num)
        tolist.append(a)
    units = []
    for num in tolist:
        a = re.sub('.*(\d+)I$|.*INFO$|.*INF$', '', num)
        units.append(a)
    tolist = []
    for num in units:
        a = re.sub('AMR.*', '', num)
        tolist.append(a)
    units = filter(None, tolist)
    return units

# Dictionary for replacement
replace_dict = {
', REN,' : ', RENTON,',
', DES,' : ', DES MOINES,',
', ISS,' : ', ISSAQUAH,',
', TUK,' : ', TUKWILA,',
', KEN,' : ', KENT,',
', SEA,' : ', SEATAC,',
', STL,' : ', SEATTLE,',
', VAS,' : ', VASHON,',
', MPV,' : ', MAPLE VALLEY,',
', FED,' : ', FEDERAL WAY,',
', NDP,' : ', NORMANDY PARK,',
', COV,' : ', COVINGTON,',
', BLA,' : ', BLACK DIAMOND,',
', ENU,' : ', ENUMCLAW,',
', BUR,' : ', BURIEN,',
', RAV,' : ', RAVENSDALE,',
', AUB,' : ', AUBURN,',
', PAC,' : ', PACIFIC,',
', ALG,' : ', ALGONA,',
'/' : ' & '
}