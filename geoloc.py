import geoip2.database

def get_country_from_ip(ip_address):
    try:
        # Replace with the path to your GeoLite2-City.mmdb file
        reader = geoip2.database.Reader('/path/to/GeoLite2-City.mmdb')
        response = reader.city(ip_address)
        country_code = response.country.iso_code
        reader.close()
        return country_code
    except Exception as e:
        print(f"Error determining country from IP: {e}")
        return 'US'  # Default to US if there's an error