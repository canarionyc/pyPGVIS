Here is a properly formatted markdown document containing the API documentation for the PVGIS Non-interactive service, based on the provided link and supplementary official resources.

-----

# PVGIS API Non-interactive Service Documentation

This document describes the non-interactive (API) service for the **Photovoltaic Geographical Information System (PVGIS)**. This service allows users to access PVGIS tools using HTTP `GET` requests and receive results in various formats (CSV, JSON, etc.) without using the web interface.

**Official Source:** [EU Science Hub - PVGIS API](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en)

-----

## 1\. Basics

### 1.1 Entry Points

All PVGIS tools can be accessed via web APIs. The current version entry points are:

  - **PVGIS 5.3**: `https://re.jrc.ec.europa.eu/api/v5_3/tool_name?param1=value1&...`
  - **PVGIS 5.2**: `https://re.jrc.ec.europa.eu/api/v5_2/tool_name?param1=value1&...`

**Variables:**

  - `tool_name`: The specific tool to access (e.g., `PVcalc`, `SHScalc`, `MRcalc`, `DRcalc`, `seriescalc`, `tmy`, `printhorizon`).
  - `param=value`: Input parameters for the tool concatenated in a query string format.

### 1.2 Usage Guidelines

  - **Method**: `GET` only. (Other methods return `405`).
  - **Rate Limit**: 30 calls/second per IP address. Exceeding this returns `429`.
  - **Overload Protection**: If the server is overloaded, requests may be suspended briefly or return `529`.

### 1.3 Common Inputs & Outputs

All tools share several common input and output parameters.

**Common Inputs:**

  - If an input is out of range, a JSON error message is returned.
  - Mandatory inputs must be present.
  - Default values are used for undefined optional parameters.

**Common Output Parameters:**

| Name | Type | Description |
| :--- | :--- | :--- |
| `outputformat` | Text | Format of the output.<br>**Options:**<br>`csv`: Standard CSV with metadata.<br>`json`: JSON output (Recommended for scripts).<br>`basic`: Raw CSV data only.<br>`epw`: EnergyPlus Weather file (TMY tool only). |
| `browser` | Int | **0** (Default): Output as stream.<br>**1**: Output as a file download. |

-----

## 2\. Inputs for Specific PVGIS Tools

### 2.1 Grid-connected & Tracking PV systems (`PVcalc`)

Calculates the performance of grid-connected PV systems, including fixed, tracking, and building-integrated options.

**Base URL:** `.../api/v5_3/PVcalc?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees (South is negative). |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees (West is negative). |
| `usehorizon` | Int | No | 1 | Calculate shadows from horizon? `1`=Yes, `0`=No. |
| `userhorizon` | List | No | - | Custom horizon height in degrees, starting North and moving clockwise (e.g., `0,10,20...`). |
| `raddatabase` | Text | No | *Default DB* | Radiation DB name (e.g., `PVGIS-SARAH3`, `PVGIS-NSRDB`, `PVGIS-ERA5`). |
| `peakpower` | Float | **Yes** | - | Nominal power of the PV system in **kW**. |
| `pvtechchoice` | Text | No | "crystSi" | PV technology: `crystSi`, `crystSi2025`, `CIS`, `CdTe`, `Unknown`. |
| `mountingplace` | Text | No | "free" | Mounting type: `free` (free-standing), `building` (integrated). |
| `loss` | Float | **Yes** | - | Sum of system losses in percent. |
| `fixed` | Int | No | 1 | Fixed mounting system? `1`=Yes, `0`=No. |
| `angle` | Float | No | 0 | Inclination angle from horizontal plane. |
| `aspect` | Float | No | 0 | Orientation (azimuth) angle. 0=South, 90=West, -90=East. |
| `optimalinclination`| Int | No | 0 | Calculate optimum inclination? `1`=Yes. (Ignores `angle`). |
| `optimalangles` | Int | No | 0 | Calculate optimum inclination AND orientation? `1`=Yes. |
| `inclined_axis` | Int | No | 0 | Single inclined axis system? `1`=Yes. |
| `inclined_optimum`| Int | No | 0 | Optimize angle for inclined axis? `1`=Yes. |
| `inclinedaxisangle`| Float| No | 0 | Inclination angle for single inclined axis. |
| `vertical_axis` | Int | No | 0 | Vertical axis system? `1`=Yes. |
| `vertical_optimum`| Int | No | 0 | Optimize angle for vertical axis? `1`=Yes. |
| `verticalaxisangle`| Float| No | 0 | Inclination angle for vertical axis. |
| `twoaxis` | Int | No | 0 | Two-axis tracking system? `1`=Yes. |
| `pvprice` | Int | No | 0 | Calculate electricity price? `1`=Yes. |
| `systemcost` | Float| If `pvprice`| - | Total cost of installing the system. |
| `interest` | Float| If `pvprice`| - | Interest rate in %/year. |
| `lifetime` | Int | No | 25 | Expected lifetime in years. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat=45&lon=8&peakpower=1&loss=14`

-----

### 2.2 Off-grid PV systems (`SHScalc`)

Calculates performance for off-grid systems with battery storage.

**Base URL:** `.../api/v5_3/SHScalc?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `peakpower` | Float | **Yes** | - | Nominal power of the PV system in **W** (Watts). |
| `batterysize` | Float | **Yes** | - | Battery capacity in **Wh** (Watt-hours). |
| `cutoff` | Float | **Yes** | - | Battery discharge cutoff limit in %. |
| `consumptionday` | Float | **Yes** | - | Daily energy consumption in **Wh**. |
| `angle` | Float | No | 0 | Inclination angle. |
| `aspect` | Float | No | 0 | Orientation angle. |
| `hourconsumption` | List | No | - | List of 24 values representing hourly fraction of daily consumption. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/SHScalc?lat=45&lon=8&peakpower=10&batterysize=50&consumptionday=200&cutoff=40`

-----

### 2.3 Monthly Radiation (`MRcalc`)

Outputs monthly average radiation and temperature data.

**Base URL:** `.../api/v5_3/MRcalc?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `startyear` | Int | No | DB Start | First year of monthly averages. |
| `endyear` | Int | No | DB End | Final year of monthly averages. |
| `horirrad` | Int | No | 0 | Output horizontal plane irradiation? `1`=Yes. |
| `optrad` | Int | No | 0 | Output optimal angle irradiation? `1`=Yes. |
| `selectrad` | Int | No | 0 | Output selected inclination irradiation? `1`=Yes. |
| `angle` | Float | No | 0 | Inclination angle (required if `selectrad=1`). |
| `mr_dni` | Int | No | 0 | Output direct normal irradiation? `1`=Yes. |
| `d2g` | Int | No | 0 | Output diffuse to global ratio? `1`=Yes. |
| `avtemp` | Int | No | 0 | Output monthly average daily temperature? `1`=Yes. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/MRcalc?lat=45&lon=8&horirrad=1`

-----

### 2.4 Daily Radiation (`DRcalc`)

Calculates average solar irradiance and temperature during the day for a chosen month.

**Base URL:** `.../api/v5_3/DRcalc?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `month` | Int | **Yes** | - | Number of the month (1-12). Use `0` for all months. |
| `global` | Int | No | 0 | Output global irradiance? `1`=Yes. |
| `diffuse` | Int | No | 0 | Output diffuse irradiance? `1`=Yes. |
| `angle` | Float | No | 0 | Inclination angle (if calculating on-plane). |
| `aspect` | Float | No | 0 | Orientation angle. |
| `usehorizon` | Int | No | 1 | Calculate shadows? `1`=Yes. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/DRcalc?lat=45&lon=8&month=6&global=1`

-----

### 2.5 Hourly Radiation (`seriescalc`)

Provides a time series of hourly solar radiation and/or PV power values.

**Base URL:** `.../api/v5_3/seriescalc?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `startyear` | Int | No | DB Start | Start year for the time series. |
| `endyear` | Int | No | DB End | End year for the time series. |
| `pvcalculation` | Int | No | 0 | Perform PV power calculation? `1`=Yes. |
| `peakpower` | Float | If `pvcalc=1`| - | Nominal power of PV system (kW). |
| `loss` | Float | If `pvcalc=1`| - | System losses (%). |
| `trackingtype` | Int | No | 0 | Type of tracking (0=fixed, 1=single horizontal, etc.). |
| `angle` | Float | No | 0 | Inclination angle. |
| `aspect` | Float | No | 0 | Orientation angle. |
| `components` | Int | No | 0 | Output beam, diffuse, & reflected components? `1`=Yes. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat=45&lon=8&startyear=2016&pvcalculation=1&peakpower=1&loss=14`

-----

### 2.6 TMY (Typical Meteorological Year) (`tmy`)

Generates a Typical Meteorological Year dataset containing hourly data.

**Base URL:** `.../api/v5_3/tmy?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `startyear` | Int | No | DB Start | First year of the period to generate TMY. |
| `endyear` | Int | No | DB End | Last year of the period to generate TMY. |
| `usehorizon` | Int | No | 1 | Calculate shadows? `1`=Yes. |
| `outputformat` | Text | No | "csv" | Choices: `csv`, `json`, `basic`, `epw`. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/tmy?lat=45&lon=8&outputformat=epw`

-----

## 3\. Horizon Profile (`printhorizon`)

Generates the horizon height (in degrees) at equidistant directions around the point of interest.

**Base URL:** `.../api/v5_3/printhorizon?`

| Name | Type | Obligatory | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | Float | **Yes** | - | Latitude in decimal degrees. |
| `lon` | Float | **Yes** | - | Longitude in decimal degrees. |
| `userhorizon` | List | No | - | Custom horizon user input to replace default. |

**Example:**
`https://re.jrc.ec.europa.eu/api/v5_3/printhorizon?lat=45&lon=8`