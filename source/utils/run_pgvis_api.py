import os
import glob
import json
import time
import requests
import pandas as pd
import numpy as np


# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Define directories
project_root = r'C:\dev\pyPGVIS'
input_folder = os.path.join(project_root,  'input')
output_folder = os.path.join(project_root, 'output')

# Ensure directories exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# PVGIS API Base
URL_BASE = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"

# Fixed API parameters
PVGIS_PARAMS = {
	'peakpower': 1,
	'loss': 14,
	'vertical_axis': 1,  # Fixed mounting
	'angle': 90,  # Tilt (90 = vertical wall)
	'outputformat': 'json',
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

	# Prepare columns for results
	df_csv['E_Y_cw'] = np.nan
	df_csv['E_Y_aw'] = np.nan

	# --- API Loop ---
	for idx, row in df_csv.iterrows():
		# Directly use latitude and longitude from the file
		lat = row['latitude']
		lon = row['longitude']
		id_val = row['city'] # Use city as the identifier

		# Define the two sides (Clockwise and Anti-Clockwise)
		sides = {
			'cw': row['azimuth_cw'],
			'aw': row['azimuth_aw']
		}

		for key, azimuth_val in sides.items():
			# Construct Parameters
			request_params = PVGIS_PARAMS.copy()
			request_params['lat'] = lat
			request_params['lon'] = lon
			request_params['azimuth'] = azimuth_val  # PVGIS expects 'azimuth' param

			try:
				# Make Request
				response = requests.get(URL_base, params=request_params)

				if response.status_code == 200:
					data = response.json()
					# Get the yearly solar radiation value
					e_y = data['outputs']['totals']['fixed']['E_y']
					print(f"ID: {id_val} | Side: {key} | Az: {azimuth_val} | Radiation: {e_y}")
				else:
					print(f"API Error {response.status_code} for ID {id_val}: {response.text}")
					e_y = -9999

			except Exception as e:
				print(f"Script Error on ID {id_val}: {e}")
				e_y = -9999

			# Update DataFrame
			df_csv.at[idx, f"E_Y_{key}"] = e_y

			# Sleep to be polite to the API (avoid rate limiting)
			time.sleep(0.1)

		# --- Save Partial Results (Every 50 rows) ---
		if idx > 0 and idx % 50 == 0:
			print('--- Saving Checkpoint ---')
			filename = os.path.basename(input_csv_path)
			df_csv.to_csv(os.path.join(output_folder, f"processed_{filename}"), index=False)

	# --- Final Save ---
	filename = os.path.basename(input_csv_path)
	final_path = os.path.join(output_folder, f"final_{filename}")
	df_csv.to_csv(final_path, index=False)
	print(f"Finished. Saved to {final_path}")