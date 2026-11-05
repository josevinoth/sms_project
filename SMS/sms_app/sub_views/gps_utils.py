import math
import re
import urllib.parse
import urllib.request
import json
import xml.etree.ElementTree as ET
import requests
import urllib3
from django.core.cache import cache
from django.db.models import Q
from ..models import LocationMaster, Places, TripdetailInfo, EnquirynoteInfo

# Pre-defined coordinates for frequent logistics hubs (speeds up matching & offline resilience)
# Keys are formatted either as "place, city" or "place"
KNOWN_HUBS = {
    # Bengaluru Hubs
    'cwc eipl, bengaluru': (13.1521, 77.7131, "CWC EIPL, Bengaluru"),
    'cwc eipl': (13.1521, 77.7131, "CWC EIPL, Bengaluru"),
    'cwc wharehouse, bengaluru': (13.1521, 77.7131, "CWC Warehouse, Bengaluru"),
    'cwc wharehouse': (13.1521, 77.7131, "CWC Warehouse, Bengaluru"),
    'cwc warehouse, bengaluru': (13.1521, 77.7131, "CWC Warehouse, Bengaluru"),
    'cwc warehouse': (13.1521, 77.7131, "CWC Warehouse, Bengaluru"),
    'cwc bangalore, bengaluru': (13.1521, 77.7131, "CWC Bengaluru"),
    'cwc bangalore': (13.1521, 77.7131, "CWC Bengaluru"),
    'cwc cfs whitefield, bengaluru': (12.9850, 77.7450, "CWC CFS Whitefield"),
    'cwc cfs whitefield': (12.9850, 77.7450, "CWC CFS Whitefield"),
    'doddajala bvm, bengaluru': (13.1815, 77.6350, "Doddajala BVM, Bengaluru"),
    'doddajala bvm': (13.1815, 77.6350, "Doddajala BVM, Bengaluru"),
    'doddajala, bengaluru': (13.1815, 77.6350, "Doddajala, Bengaluru"),
    'doddajala': (13.1815, 77.6350, "Doddajala, Bengaluru"),
    'krishnagiri, bengaluru': (12.5266, 78.2144, "Krishnagiri"),
    'krishnagiri': (12.5266, 78.2144, "Krishnagiri"),
    'dabaspet, bengaluru': (13.2341, 77.2411, "Dabaspet"),
    'dabaspet': (13.2341, 77.2411, "Dabaspet"),
    'dobbaspet, bengaluru': (13.2341, 77.2411, "Dabaspet"),
    'dobbaspet': (13.2341, 77.2411, "Dabaspet"),
    'doddaballapura, bengaluru': (13.2930, 77.5431, "Doddaballapura"),
    'doddaballapura': (13.2930, 77.5431, "Doddaballapura"),
    'airport blr, bengaluru': (13.1986, 77.7066, "Kempegowda Int Airport (BLR)"),
    'airport blr': (13.1986, 77.7066, "Kempegowda Int Airport (BLR)"),
    'kempegowda international airport bengaluru (blr), bengaluru': (13.1986, 77.7066, "Kempegowda Int Airport (BLR)"),
    'devanahalli, bengaluru': (13.2483, 77.7126, "Devanahalli"),
    'devanahalli': (13.2483, 77.7126, "Devanahalli"),
    'bidadi, bengaluru': (12.7989, 77.3870, "Bidadi"),
    'bidadi': (12.7989, 77.3870, "Bidadi"),
    'nelamangala, bengaluru': (13.0953, 77.3964, "Nelamangala"),
    'nelamangala': (13.0953, 77.3964, "Nelamangala"),
    'electronic city, bengaluru': (12.8452, 77.6602, "Electronic City, Bengaluru"),
    'electronic city': (12.8452, 77.6602, "Electronic City, Bengaluru"),
    'whitefield, bengaluru': (12.9698, 77.7500, "Whitefield, Bengaluru"),
    'whitefield': (12.9698, 77.7500, "Whitefield, Bengaluru"),
    'peenya, bengaluru': (13.0285, 77.5197, "Peenya, Bengaluru"),
    'peenya': (13.0285, 77.5197, "Peenya, Bengaluru"),
    'hosur': (12.7409, 77.8253, "Hosur"),
    'yelahanka, bengaluru': (13.1007, 77.5963, "Yelahanka, Bengaluru"),
    'yelahanka': (13.1007, 77.5963, "Yelahanka, Bengaluru"),

    # Chennai Hubs
    'nagalkeni bvm, chennai': (12.9602, 80.1384, "Nagalkeni BVM, Chennai"),
    'nagalkeni bvm': (12.9602, 80.1384, "Nagalkeni BVM, Chennai"),
    'nagalkeni, chennai': (12.9602, 80.1384, "Nagalkeni, Chennai"),
    'nagalkeni': (12.9602, 80.1384, "Nagalkeni, Chennai"),
    'triway cfs, chennai': (13.2084, 80.2982, "Triway CFS, Chennai"),
    'triway cfs': (13.2084, 80.2982, "Triway CFS, Chennai"),
    'triway, chennai': (13.2084, 80.2982, "Triway CFS, Chennai"),
    'all cfs, chennai': (13.2084, 80.2982, "Chennai CFS Hub"),
    'all cfs': (13.2084, 80.2982, "Chennai CFS Hub"),
    'all cargo cfs, chennai': (13.2012, 80.2856, "Allcargo CFS, Chennai"),
    'all cargo cfs': (13.2012, 80.2856, "Allcargo CFS, Chennai"),
    'allcargo cfs, chennai': (13.2012, 80.2856, "Allcargo CFS, Chennai"),
    'allcargo cfs': (13.2012, 80.2856, "Allcargo CFS, Chennai"),
    'airport, chennai': (12.9856, 80.1636, "Chennai Airport (MAA)"),
    'chennai airport, chennai': (12.9856, 80.1636, "Chennai Airport (MAA)"),
    'chennai airport': (12.9856, 80.1636, "Chennai Airport (MAA)"),
    'airport maa, chennai': (12.9856, 80.1636, "Chennai Airport (MAA)"),
    'airport maa': (12.9856, 80.1636, "Chennai Airport (MAA)"),
    'pammal, chennai': (12.9658, 80.1320, "Pammal, Chennai"),
    'pammal': (12.9658, 80.1320, "Pammal, Chennai"),
    'chennai, chennai': (13.0827, 80.2707, "Chennai"),
    'chennai': (13.0827, 80.2707, "Chennai"),
    'ambattur, chennai': (13.0983, 80.1613, "Ambattur, Chennai"),
    'ambattur': (13.0983, 80.1613, "Ambattur, Chennai"),
    'sriperumbudur, chennai': (12.9675, 79.9430, "Sriperumbudur"),
    'sriperumbudur': (12.9675, 79.9430, "Sriperumbudur"),
    'guindy, chennai': (13.0067, 80.2025, "Guindy, Chennai"),
    'guindy': (13.0067, 80.2025, "Guindy, Chennai"),
    'chromepet, chennai': (12.9516, 80.1462, "Chromepet, Chennai"),
    'chromepet': (12.9516, 80.1462, "Chromepet, Chennai"),
    'pallavaram, chennai': (12.9680, 80.1491, "Pallavaram, Chennai"),
    'pallavaram': (12.9680, 80.1491, "Pallavaram, Chennai"),
    'tambaram, chennai': (12.9249, 80.1000, "Tambaram, Chennai"),
    'tambaram': (12.9249, 80.1000, "Tambaram, Chennai"),
    'ennore, chennai': (13.2167, 80.3236, "Ennore"),
    'ennore': (13.2167, 80.3236, "Ennore"),
    'thiruvallur': (13.1438, 79.9079, "Thiruvallur"),

    # Other Regional Hubs
    'vizag, chennai': (17.6868, 83.2185, "Visakhapatnam"),
    'vizag, visakhapatnam': (17.6868, 83.2185, "Visakhapatnam"),
    'vizag': (17.6868, 83.2185, "Visakhapatnam"),
    'visakhapatnam': (17.6868, 83.2185, "Visakhapatnam"),
    'hyderabad airport, hyderabad': (17.2403, 78.4294, "Hyderabad Airport (RGIA)"),
    'hyderabad, hyderabad': (17.3850, 78.4867, "Hyderabad"),
    'hyderabad': (17.3850, 78.4867, "Hyderabad"),
    'coimbatore, coimbatore': (11.0168, 76.9558, "Coimbatore"),
    'coimbatore': (11.0168, 76.9558, "Coimbatore"),
    'puducherry, puducherry': (11.9416, 79.8083, "Puducherry"),
    'puducherry': (11.9416, 79.8083, "Puducherry"),
    'pondicherry': (11.9416, 79.8083, "Puducherry"),
}


def normalize_reg(reg):
    """Normalizes vehicle number by removing spaces, hyphens, and converting to uppercase."""
    if not reg:
        return ""
    return re.sub(r'[\s\-]', '', str(reg)).upper()


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 1)
    except (ValueError, TypeError):
        return None


def clean_short_address(addr):
    """Cleans and shortens GPS address for compact display in UI badges and dropdowns."""
    if not addr:
        return ""
    addr = addr.strip()
    if 'BVM' in addr.upper():
        return addr
    # Remove country suffix and postal codes (e.g. Ka-560092, 560092, India)
    addr = re.sub(r',?\s*(India|\b[A-Za-z]{2}-?\d{6}\b|\b\d{6}\b)', '', addr, flags=re.IGNORECASE).strip(' ,')
    parts = [p.strip() for p in addr.split(',') if p.strip()]
    if len(parts) >= 2:
        return f"{parts[-2]}, {parts[-1]}"
    elif len(parts) == 1:
        return parts[0]
    return addr


def get_live_gps_devices():
    """
    Fetches real-time vehicle GPS coordinates from TrackMyVehicle API.
    Cached for 30 seconds to ensure high UI responsiveness (<10ms).
    """
    cache_key = 'bvm_live_gps_devices'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    api_url = (
        "https://track.trackmyvehicle.in/events/data.xml"
        "?account=Bvm%20Storage%20Solutions%20Pvt%20ltd"
        "&user=apilink"
        "&password=pass@123"
        "&group=all"
        "&limit=1"
    )

    devices = {}
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(api_url, verify=False, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for device in root.findall(".//Device"):
                raw_no = device.findtext("Description", "").strip()
                norm_no = normalize_reg(raw_no)
                events = device.findall("EventData")
                if not events:
                    continue
                ev = events[-1]
                lat_str = ev.findtext("GPSPoint_lat", "").strip()
                lon_str = ev.findtext("GPSPoint_lon", "").strip()
                addr_str = ev.findtext("Address", "").strip()
                speed_str = ev.findtext("Speed", "0").strip()
                status_code = ev.findtext("StatusCode", "").strip()
                timestamp = ev.findtext("Timestamp", "").strip()

                try:
                    lat = float(lat_str)
                    lon = float(lon_str)
                    speed = float(speed_str) if speed_str else 0.0
                    devices[norm_no] = {
                        'lat': lat,
                        'lon': lon,
                        'address': addr_str,
                        'short_addr': clean_short_address(addr_str),
                        'speed': speed,
                        'status': status_code,
                        'timestamp': timestamp,
                        'raw_no': raw_no
                    }
                except (ValueError, TypeError):
                    continue

            # Cache the successful device map for 30 seconds
            cache.set(cache_key, devices, timeout=30)
    except Exception as e:
        print(f"[gps_utils] Warning: Live GPS fetch failed ({e}).")

    return devices


def get_place_coordinates(place_name, city_name=""):
    """
    Resolves the (latitude, longitude) of a place or hub.
    Priority:
    1. Django Cache
    2. Known logistics hubs dictionary
    3. LocationMaster DB table
    4. Nominatim OSM geocoding API (cached permanently into LocationMaster & cache)
    """
    if not place_name:
        return None, None, None

    clean_place = re.sub(r'\s+', ' ', str(place_name)).strip()
    clean_city = re.sub(r'\s+', ' ', str(city_name)).strip() if city_name else ""
    safe_place = re.sub(r'[^a-zA-Z0-9_]', '_', clean_place.lower())
    safe_city = re.sub(r'[^a-zA-Z0-9_]', '_', clean_city.lower())
    cache_key = f"coord_{safe_place}_{safe_city}"
    cached_val = cache.get(cache_key)
    if cached_val:
        return cached_val

    # 1. Check LocationMaster DB table dynamically (Primary source of truth for all locations)
    loc_qs = LocationMaster.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    match = None

    # 1a. Exact or case-insensitive match on locationame or location_name
    if clean_city:
        match = loc_qs.filter(
            Q(location_name__icontains=clean_city) | Q(state__icontains=clean_city),
            Q(locationame__iexact=clean_place) | Q(location_name__iexact=clean_place)
        ).first()

    if not match:
        match = loc_qs.filter(
            Q(locationame__iexact=clean_place) | Q(location_name__iexact=clean_place)
        ).first()

    # 1b. Substring match
    if not match:
        if clean_city:
            match = loc_qs.filter(
                Q(location_name__icontains=clean_city) | Q(state__icontains=clean_city),
                Q(locationame__icontains=clean_place) | Q(location_name__icontains=clean_place)
            ).first()
        if not match:
            match = loc_qs.filter(
                Q(locationame__icontains=clean_place) | Q(location_name__icontains=clean_place)
            ).first()

    # 1c. Normalized string match (ignoring punctuation, spaces, case)
    if not match:
        norm_query = re.sub(r'[^a-zA-Z0-9]', '', clean_place).lower()
        if norm_query:
            for loc in loc_qs:
                lm_norm1 = re.sub(r'[^a-zA-Z0-9]', '', loc.locationame or '').lower()
                lm_norm2 = re.sub(r'[^a-zA-Z0-9]', '', loc.location_name or '').lower()
                if norm_query == lm_norm1 or norm_query == lm_norm2 or (lm_norm1 and lm_norm1 in norm_query) or (norm_query in lm_norm2):
                    match = loc
                    break

    # 1d. Core word token match (e.g. "CWC EIPL" matches "cwc bangalore" or "CWC wharehouse")
    if not match:
        stop_words = {'cfs', 'hub', 'whs', 'yard', 'depot', 'terminal', 'the', 'near', 'opp', 'road', 'street', 'area', 'blr', 'maa'}
        tokens = [t for t in re.split(r'[^a-zA-Z0-9]', clean_place.lower()) if len(t) >= 3 and t not in stop_words]
        for t in tokens:
            t_candidates = loc_qs.filter(Q(locationame__icontains=t) | Q(location_name__icontains=t))
            if clean_city:
                c_cand = t_candidates.filter(Q(location_name__icontains=clean_city) | Q(state__icontains=clean_city)).first()
                if c_cand:
                    match = c_cand
                    break
            first_cand = t_candidates.first()
            if first_cand:
                match = first_cand
                break

    if match:
        try:
            lat = float(match.latitude)
            lon = float(match.longitude)
            label = match.locationame or match.location_name or clean_place
            cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
            return lat, lon, label
        except (ValueError, TypeError):
            pass

    # 2. Check KNOWN_HUBS fast-lookup dictionary
    clean_place_lower = clean_place.lower()
    clean_city_lower = clean_city.lower()
    full_key = f"{clean_place_lower}, {clean_city_lower}".strip(', ')

    if full_key in KNOWN_HUBS:
        lat, lon, label = KNOWN_HUBS[full_key]
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label

    if clean_place_lower in KNOWN_HUBS:
        lat, lon, label = KNOWN_HUBS[clean_place_lower]
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label

    # Check with city contains
    lookup_with_city = f"{clean_place_lower} {clean_city_lower}".strip()
    for k, v in KNOWN_HUBS.items():
        if k == clean_place_lower or (clean_city_lower and k == full_key):
            lat, lon, label = v
            cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
            return lat, lon, label

    # Keyword fallback for common company hubs
    if 'cwc' in clean_place_lower and ('blr' in clean_city_lower or 'bengaluru' in clean_city_lower or 'bangalore' in clean_city_lower or not clean_city_lower):
        lat, lon, label = KNOWN_HUBS['cwc eipl']
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label
    if 'nagalkeni' in clean_place_lower:
        lat, lon, label = KNOWN_HUBS['nagalkeni bvm']
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label
    if 'doddajala' in clean_place_lower:
        lat, lon, label = KNOWN_HUBS['doddajala bvm']
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label
    if 'triway' in clean_place_lower:
        lat, lon, label = KNOWN_HUBS['triway cfs']
        cache.set(cache_key, (lat, lon, label), timeout=86400 * 30)
        return lat, lon, label

    # 3. Geocode with Nominatim (with 3-second timeout)
    try:
        query_terms = [clean_place]
        if clean_city and clean_city.lower() not in clean_place.lower():
            query_terms.append(clean_city)
        query_terms.append("India")
        query = ", ".join(query_terms)

        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            'q': query,
            'format': 'json',
            'limit': 1
        })
        req = urllib.request.Request(url, headers={'User-Agent': 'SMS_Logistics_Management/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                display_name = data[0].get('display_name', clean_place)

                # Persist to LocationMaster for future zero-latency lookups
                try:
                    LocationMaster.objects.create(
                        location_name=display_name[:255] if display_name else clean_place,
                        locationame=clean_place[:100],
                        latitude=lat,
                        longitude=lon
                    )
                except Exception:
                    pass

                cache.set(cache_key, (lat, lon, clean_place), timeout=86400 * 30)
                return lat, lon, clean_place
    except Exception as e:
        print(f"[gps_utils] Warning: Geocoding failed for '{clean_place}' ({e})")

    return None, None, None


def get_vehicle_last_known_trip_location(reg_number):
    """
    Fallback for vehicles without live GPS: looks up the last completed trip's unload destination.
    """
    if not reg_number:
        return None, None, None
    trip = TripdetailInfo.objects.filter(
        tr_vehiclenumber__iexact=str(reg_number).strip(),
        tr_reportedlocation__isnull=False
    ).select_related('tr_reportedlocation', 'tr_reportedlocation__city').order_by('-id').first()

    if trip and trip.tr_reportedlocation:
        p_name = trip.tr_reportedlocation.place_name
        c_name = trip.tr_reportedlocation.city.city_name if trip.tr_reportedlocation.city else ""
        lat, lon, label = get_place_coordinates(p_name, c_name)
        if lat and lon:
            return lat, lon, f"Last trip: {p_name}"
    return None, None, None
