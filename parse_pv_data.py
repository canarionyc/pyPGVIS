import json
import os
from pathlib import Path
from typing import Dict, List, Any
from pprint import pprint


def parse_pv_json(file_path: str) -> Dict[str, Any]:
    """Parse a single PV data JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def parse_all_json_files(directory: str = 'data') -> List[Dict[str, Any]]:
    """Parse all JSON files in the specified directory."""
    json_files = Path(directory).glob('*.json')
    results = []

    for file_path in json_files:
        print(f"Parsing: {file_path}")
        try:
            data = parse_pv_json(file_path); pprint(data)
            results.append({
                'file': str(file_path),
                'data': data
            })
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    return results


def extract_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key summary information from parsed PV data."""
    summary = {}

    # Location info
    if 'inputs' in data and 'location' in data['inputs']:
        location = data['inputs']['location']
        summary['latitude'] = location.get('latitude')
        summary['longitude'] = location.get('longitude')
        summary['elevation'] = location.get('elevation')

    # PV module info
    if 'inputs' in data and 'pv_module' in data['inputs']:
        pv_module = data['inputs']['pv_module']
        summary['technology'] = pv_module.get('technology')
        summary['peak_power_kW'] = pv_module.get('peak_power')
        summary['system_loss_pct'] = pv_module.get('system_loss')

    # Mounting system info
    if 'inputs' in data and 'mounting_system' in data['inputs']:
        mounting = data['inputs']['mounting_system']
        if 'fixed' in mounting:
            fixed = mounting['fixed']
            summary['slope'] = fixed.get('slope', {}).get('value')
            summary['azimuth'] = fixed.get('azimuth', {}).get('value')

    # Annual totals
    if 'outputs' in data and 'totals' in data['outputs'] and 'fixed' in data['outputs']['totals']:
        totals = data['outputs']['totals']['fixed']
        summary['yearly_energy_kWh'] = totals.get('E_y')
        summary['avg_daily_energy_kWh'] = totals.get('E_d')
        summary['avg_monthly_energy_kWh'] = totals.get('E_m')
        summary['yearly_irradiation_kWh_m2'] = totals.get('H(i)_y')
        summary['total_loss_pct'] = totals.get('l_total')

    return summary

if __name__ == '__main__':
    # Parse all JSON files
    results = parse_all_json_files('data')

    print(f"\n{'='*60}")
    print(f"Found {len(results)} JSON file(s)")
    print(f"{'='*60}\n")

    # Display summaries
    for result in results:
        print(f"File: {result['file']}")
        summary = extract_summary(result['data'])
        pprint(summary)
        print(f"  Location: {summary.get('latitude', 'N/A')}°N, {summary.get('longitude', 'N/A')}°E")
        print(f"  Elevation: {summary.get('elevation', 'N/A')} m")
        print(f"  Technology: {summary.get('technology', 'N/A')}")
        print(f"  Peak Power: {summary.get('peak_power_kW', 'N/A')} kW")
        print(f"  Slope/Azimuth: {summary.get('slope', 'N/A')}° / {summary.get('azimuth', 'N/A')}°")
        print(f"  Yearly Energy Production: {summary.get('yearly_energy_kWh', 'N/A'):,.2f} kWh")
        print(f"  Avg Daily Production: {summary.get('avg_daily_energy_kWh', 'N/A'):,.2f} kWh/d")
        print(f"  Total System Loss: {summary.get('total_loss_pct', 'N/A')}%")
        print()
