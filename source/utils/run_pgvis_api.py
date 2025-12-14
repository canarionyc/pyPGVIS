import os
import json
import time
import requests
import pandas as pd
import csv

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Define directories
project_root = r'C:\dev\pyPVGIS'
input_folder = os.path.join(project_root,  'input')
output_folder = os.path.join(project_root, 'output')

# Ensure directories exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# PVGIS API Base URL
URL_CALC = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"

# Fixed API parameters for PVcalc
PVGIS_PARAMS = {
	'peakpower': 1,
	'loss': 14,
	'mounting': 'fixed',
	'angle': 45,
	'outputformat': 'json',
	'usehorizon': 1,
}


# ==========================================
# 2. MAIN EXECUTION
# ==========================================

# Define the specific input file
input_csv_path = os.path.join(input_folder, "test_sites_LL.csv")

if not os.path.exists(input_csv_path):
	print(f"Error: Input file not found at {input_csv_path}")
else:
	print(f"Processing: {input_csv_path}")

	# Load the CSV
	df_csv = pd.read_csv(input_csv_path)

	# --- API Loop ---
	for idx, row in df_csv.iterrows():
		run_flag = str(row.get('run', '')).lower()
		if run_flag not in ['1', 'true', 'yes']:
			continue

		lat = row['latitude']
		lon = row['longitude']
		city = row['city']
		country = row['country']
		azimuth_val = 180  # Hardcode to South-facing

		print(f"Processing {city}, {country} for South-facing panels (180 deg)...")

		request_params = PVGIS_PARAMS.copy()
		request_params.update({'lat': lat, 'lon': lon, 'azimuth': azimuth_val})

		try:
			response = requests.get(URL_CALC, params=request_params)
			if response.status_code == 200:
				data = response.json()
				
				# --- 1. Save Full JSON Output ---
				json_filename = f"{city.replace(' ', '_')}_{country.replace(' ', '_')}.json"
				json_path = os.path.join(output_folder, json_filename)
				with open(json_path, 'w') as f:
					json.dump(data, f, indent=4)
				print(f"Saved full JSON results to {json_path}")

				# --- 2. Save Monthly Time Series CSV ---
				monthly_data = data.get('outputs', {}).get('monthly', {}).get('fixed', [])
				if monthly_data:
					csv_filename = f"{city.replace(' ', '_')}_{country.replace(' ', '_')}_monthly.csv"
					csv_path = os.path.join(output_folder, csv_filename)
					
					with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
						writer = csv.writer(csvfile)
						# Write header from the keys of the first month's dictionary
						writer.writerow(monthly_data[0].keys())
						# Write data rows
						for month in monthly_data:
							writer.writerow(month.values())
					print(f"Saved monthly CSV to {csv_path}")

			else:
				print(f"API Error {response.status_code} for {city}: {response.text}")
		
		except Exception as e:
			print(f"Script Error on {city}: {e}")
		
		time.sleep(0.2)

	print("Finished processing all runnable sites.")
