import os
import glob
import json
import time
import requests
import pandas as pd
import numpy as np
from pyproj import Transformer

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Define directories (Update these paths for your actual environment)
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
# 2. HELPER FUNCTIONS
# ==========================================

def get_transformer():
	"""
	Sets up the coordinate transformer.
	Assuming input is ETRS89-LAEA (EPSG:3035) and output is WGS84 (EPSG:4326).
	Change source_crs if your X/Y are in a different format.
	"""
	# EPSG:3035 is the standard EU LAEA projection.
	# If your data is just raw Lat/Lon already, you don't need this.
	return Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)


def create_dummy_data():
	"""Creates a dummy CSV to make this script runnable for testing."""
	data = {
		'ORIG_FID': [101, 102, 103],
		'POINT_X': [4000000, 4000500, 4001000],  # Dummy LAEA coordinates
		'POINT_Y': [3000000, 3000500, 3001000],
		'azimuth_cw': [0, -90, 45],  # Clockwise azimuths
		'azimuth_aw': [180, 90, -135]  # Anti-clockwise azimuths
	}
	df = pd.DataFrame(data)
	dummy_path = os.path.join(input_folder, "test_sites.csv")
	df.to_csv(dummy_path, index=False)
	print(f"Created dummy data at: {dummy_path}")


# ==========================================
# 3. MAIN EXECUTION
# ==========================================

# --- BLOCK: Create Dummy Data (Comment this out when using real files) ---
create_dummy_data()
# -------------------------------------------------------------------------

# Get list of CSVs
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

if not csv_files:
	print("No CSV files found!")
else:
	transformer = get_transformer()

	for csv_file in csv_files:
		print(f"Processing: {csv_file}")

		# Load the CSV
		df_csv = pd.read_csv(csv_file)

		# Prepare columns for results
		df_csv['lat'] = np.nan
		df_csv['lon'] = np.nan
		df_csv['E_Y_cw'] = np.nan
		df_csv['E_Y_aw'] = np.nan

		# --- Coordinate Conversion ---
		# Transforming LAEA (X,Y) to WGS84 (Lon, Lat)
		# Note: pyproj transform returns (lon, lat) because we set always_xy=True
		lons, lats = transformer.transform(df_csv['POINT_X'].values, df_csv['POINT_Y'].values)
		df_csv['lon'] = lons
		df_csv['lat'] = lats

		# --- API Loop ---
		for idx, row in df_csv.iterrows():
			lat = row['lat']
			lon = row['lon']
			id_val = row['ORIG_FID']

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
					response = requests.get(URL_BASE, params=request_params)

					if response.status_code == 200:
						data = response.json()
						e_y = data['outputs']['totals']['fixed']['E_y']
						print(f"ID: {id_val} | Side: {key} | Az: {azimuth_val} | Rad: {e_y}")
					else:
						print(f"API Error {response.status_code}: {response.text}")
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
				filename = os.path.basename(csv_file)
				df_csv.to_csv(os.path.join(output_folder, f"processed_{filename}"), index=False)

		# --- Final Save ---
		filename = os.path.basename(csv_file)
		final_path = os.path.join(output_folder, f"final_{filename}")
		df_csv.to_csv(final_path, index=False)
		print(f"Finished. Saved to {final_path}")