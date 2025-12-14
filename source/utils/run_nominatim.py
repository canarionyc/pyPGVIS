import requests
from geopy.geocoders import Nominatim


def get_city_data(city_name):
	"""
    Retreives Latitude, Longitude, and Elevation for a given city.
    """
	# 1. Setup the Geolocator (Nominatim requires a unique user_agent)
	geolocator = Nominatim(user_agent="geo_elevation_script_v1")

	try:
		# 2. Get Coordinates (Lat/Lon)
		location = geolocator.geocode(city_name)

		if not location:
			print(f"Error: Could not find city '{city_name}'. Please check the spelling.")
			return None

		lat = location.latitude
		lon = location.longitude

		# 3. Get Elevation using Open-Elevation API
		# We send a GET request to the public API with the coordinates
		api_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
		response = requests.get(api_url)

		if response.status_code == 200:
			data = response.json()
			# The API returns a list of results, we take the first one
			elevation = data['results'][0]['elevation']
		else:
			print("Error: Could not retrieve elevation data from API.")
			elevation = "N/A"

		return {
			"city": city_name,
			"full_address": location.address,
			"latitude": lat,
			"longitude": lon,
			"elevation_meters": elevation
		}

	except Exception as e:
		print(f"An unexpected error occurred: {e}")
		return None


# --- Example Usage ---
if __name__ == "__main__":
	# You can change this list to any European cities you like
	cities_to_check = ["Zermatt", "Paris", "Madrid"]

	print(f"{'City':<15} | {'Lat':<10} | {'Lon':<10} | {'Elev (m)':<10}")
	print("-" * 55)

	for city in cities_to_check:
		data = get_city_data(city)
		if data:
			print(
				f"{data['city']:<15} | {data['latitude']:<10.4f} | {data['longitude']:<10.4f} | {data['elevation_meters']:<10}")