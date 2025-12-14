import requests
import time
import csv


def get_location_data(city_name):
	"""
	Retrieves Latitude, Longitude, and Elevation using Open-Meteo (No API Key required).
	"""
	try:
		# 1. Geocoding: Convert City Name -> Lat/Lon
		# Documentation: https://open-meteo.com/en/docs/geocoding-api
		geo_url = "https://geocoding-api.open-meteo.com/v1/search"
		geo_params = {
			"name": city_name,
			"count": 1,  # Just get the top result
			"language": "en",  # Prefer English names
			"format": "json"
		}

		geo_response = requests.get(geo_url, params=geo_params)
		geo_data = geo_response.json()

		# Check if any city was found
		if "results" not in geo_data:
			print(f"Error: City '{city_name}' not found.")
			return None

		# Extract basic info
		result = geo_data["results"][0]
		lat = result["latitude"]
		lon = result["longitude"]
		country = result.get("country", "Unknown")
		name = result["name"]

		# 2. Elevation: Get Altitude from Lat/Lon
		# Documentation: https://open-meteo.com/en/docs/elevation-api
		elev_url = "https://api.open-meteo.com/v1/elevation"
		elev_params = {
			"latitude": lat,
			"longitude": lon
		}

		elev_response = requests.get(elev_url, params=elev_params)
		elev_data = elev_response.json()

		# The API returns a list of elevations (we sent 1 coordinate, so we get 1 height)
		elevation = elev_data["elevation"][0]

		return {
			"city": name,
			"country": country,
			"latitude": lat,
			"longitude": lon,
			"elevation": elevation
		}

	except Exception as e:
		print(f"Error processing {city_name}: {e}")
		return None


# --- Main Execution ---
if __name__ == "__main__":
	cities = ["Teruel", "Zermatt", "Paris", "Madrid", "Innsbruck", "Lisbon"]
	output_filename = "C:/dev/pyPGVIS/input/test_sites_LL.csv"
	headers = ["city", "country", "latitude", "longitude", "elevation", "azimuth_cw", "azimuth_aw"]

	print(f"Writing location data to {output_filename}...")

	with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(headers)

		for city in cities:
			data = get_location_data(city)
			if data:
				row = [
					data['city'],
					data['country'],
					f"{data['latitude']:.4f}",
					f"{data['longitude']:.4f}",
					data['elevation'],
					0,    # azimuth_cw
					180   # azimuth_aw
				]
				writer.writerow(row)

			# Good practice: slight pause to be polite to the server
			time.sleep(0.2)
	
	print("Done.")
