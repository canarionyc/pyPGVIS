import os
import csv
import time
import requests
import shutil

def get_location_data(city_name):
	"""
	Retrieves Latitude, Longitude, and Elevation using Open-Meteo (No API Key required).
	"""
	try:
		# 1. Geocoding: Convert City Name -> Lat/Lon
		geo_url = "https://geocoding-api.open-meteo.com/v1/search"
		geo_params = {
			"name": city_name,
			"count": 1,
			"language": "en",
			"format": "json"
		}
		geo_response = requests.get(geo_url, params=geo_params)
		geo_data = geo_response.json()

		if "results" not in geo_data:
			print(f"Error: City '{city_name}' not found.")
			return None

		result = geo_data["results"][0]
		lat = result["latitude"]
		lon = result["longitude"]
		country = result.get("country", "Unknown")
		name = result["name"]

		# 2. Elevation: Get Altitude from Lat/Lon
		elev_url = "https://api.open-meteo.com/v1/elevation"
		elev_params = {"latitude": lat, "longitude": lon}
		elev_response = requests.get(elev_url, params=elev_params)
		elev_data = elev_response.json()
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
	input_filename = "C:/dev/pyPVGIS/input/test_sites_LL.csv"
	temp_filename = input_filename + ".tmp"

	try:
		with open(input_filename, 'r', newline='', encoding='utf-8') as infile:
			reader = csv.DictReader(infile)
			
			original_headers = reader.fieldnames or ["city", "country", "latitude", "longitude", "elevation", "azimuth_cw", "azimuth_aw"]
			output_headers = list(original_headers)
			if 'run' not in output_headers:
				output_headers.append('run')

			with open(temp_filename, 'w', newline='', encoding='utf-8') as outfile:
				writer = csv.DictWriter(outfile, fieldnames=output_headers, extrasaction='ignore')
				writer.writeheader()

				for row in reader:
					city = row.get('city', '').strip()
					if not city:
						continue

					needs_update = not (row.get('latitude') and row.get('longitude') and row.get('elevation'))

					if needs_update:
						print(f"Fetching missing data for {city}...")
						location_data = get_location_data(city)
						
						if location_data:
							row.update({
								'city': location_data['city'],
								'country': location_data['country'],
								'latitude': f"{location_data['latitude']:.4f}",
								'longitude': f"{location_data['longitude']:.4f}",
								'elevation': location_data['elevation'],
								'run': 'yes'
							})
							if not row.get('azimuth_cw'): row['azimuth_cw'] = 0
							if not row.get('azimuth_aw'): row['azimuth_aw'] = 180
							time.sleep(0.2)
					
					writer.writerow(row)

		shutil.move(temp_filename, input_filename)
		print(f"Successfully updated {input_filename}")

	except FileNotFoundError:
		print(f"Error: Input file not found at {input_filename}")
	except Exception as e:
		print(f"An unexpected error occurred: {e}")
		if os.path.exists(temp_filename):
			os.remove(temp_filename)
