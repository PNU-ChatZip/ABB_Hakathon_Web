from geopy.geocoders import Nominatim

def geocoding_reverse(lat_lng_str): 
    geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
    address = str(geolocoder.reverse(lat_lng_str))
    address = ''.join(map(str, address.split(',')[::-1]))
    return address