# %% setup
import numpy as np
import matplotlib.pyplot as plt
import os
print(os.getcwd())

import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

# ==========================================
# 1. SETUP: Define Location & Module
# ==========================================
lat, lon = 48.137, 11.576  # Example: Munich
module_name = 'Canadian_Solar_Inc__CS5P_220M'  # Exact name from CEC database
inverter_name = 'ABB__MICRO_0_25_I_OUTD_US_208__208V_' # Example Microinverter

# ==========================================
# 2. FETCH DATABASES (The "Catalog" Plugin)
# ==========================================
print("Fetching NREL/CEC Module & Inverter Databases...")
# This pulls the latest catalogs from the NREL system
modules = pvlib.pvsystem.retrieve_sam('CECMod')
inverters = pvlib.pvsystem.retrieve_sam('CECInverter')

# Pick your specific hardware
module = modules[module_name]
inverter = inverters[inverter_name]

print(f"Selected Module: {module_name}")
print(f"  - Technology: {module['Technology']}")
print(f"  - STC Power: {module['STC']} W")

# ==========================================
# 3. GET WEATHER FROM PVGIS
# ==========================================
print("Fetching TMY Weather Data from PVGIS...")
# Get Typical Meteorological Year (TMY) data directly from JRC
weather, metadata = pvlib.iotools.get_pvgis_tmy(
    latitude=lat,
    longitude=lon,
    map_variables=True
)
#print(weather)
# Rename columns to match pvlib expectations if needed (map_variables=True usually handles this)
weather.index.name = "utc_time"

# ==========================================
# 4. RUN SIMULATION (The "Engine")
# ==========================================
location = Location(latitude=lat, longitude=lon)

# Define the mounting (Fixed, Tilted)
mount = FixedMount(surface_tilt=30, surface_azimuth=180) # South facing

# Define the Array (Strings/Sub-arrays)
array = Array(
    mount=mount,
    module_parameters=module,
    temperature_model_parameters=TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
)

# Define the System
system = PVSystem(
    arrays=[array],
    inverter_parameters=inverter
)

# Run the ModelChain
mc = ModelChain(system, location, aoi_model="ashrae")
mc.run_model(weather)

# ==========================================
# 5. RESULTS
# ==========================================
total_energy = mc.results.ac.sum() / 1000 # kWh
print(f"\nTotal Annual Energy: {total_energy:.2f} kWh")
print(f"Performance Ratio (approx): {total_energy / (module['STC'] * len(weather)/1000):.2f}")

# Optional: Plotting
mc.results.ac.plot(title=f"Power Output: {module_name}")