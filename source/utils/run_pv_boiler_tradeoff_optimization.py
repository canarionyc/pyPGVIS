import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# ==========================================
# 1. CONFIGURATION & ASSUMPTIONS (REVISED MODEL)
# ==========================================

# --- User-Defined Financial & Technical Assumptions ---
COST_PER_KWP_INSTALLED = 1500
GRID_EXPORT_PRICE_KWH = 0.02

# --- System & Economic Assumptions ---
BIOMASS_COST_PER_KWH = 0.09
LOAN_INTEREST_RATE = 0.06
LOAN_YEARS = 15
HEAT_PUMP_COP = 3.5
COOLING_EER = 3.5
GRID_IMPORT_PRICE_KWH = 0.16

# --- File Paths ---
project_root = r'C:\dev\pyPVGIS'
input_folder = os.path.join(project_root, 'input')
output_folder = os.path.join(project_root, 'output')
os.makedirs(output_folder, exist_ok=True)

DEMAND_FILE = os.path.join(input_folder, 'ejemploi_2526_option1_config1.csv')
IRRADIATION_FILE = os.path.join(output_folder, 'Albarracín_Spain_monthly.csv')


# ==========================================
# 2. FUNCTIONS
# ==========================================

def calculate_capital_recovery_factor(rate, years):
    if rate == 0: return 1 / years
    return (rate * (1 + rate)**years) / ((1 + rate)**years - 1)

def run_optimization():
    # --- Load and Clean Data ---
    try:
        demand_df = pd.read_csv(DEMAND_FILE)
        pv_generation_df = pd.read_csv(IRRADIATION_FILE)
    except FileNotFoundError as e:
        print(f"Error: Could not find input file - {e}")
        return

    demand_df.columns = demand_df.columns.str.strip()
    def clean_and_convert_to_numeric(series):
        return pd.to_numeric(series.str.replace(',', '').str.strip(), errors='coerce').fillna(0) / 1000

    demand_acs = clean_and_convert_to_numeric(demand_df['demandaACS (Wh)'])
    demand_cal = clean_and_convert_to_numeric(demand_df['demandaCAL (Wh)'])
    demand_cool = clean_and_convert_to_numeric(demand_df['demandaREF (Wh)'])
    monthly_pv_generation_per_kwp = pv_generation_df['E_m']

    # --- Run Simulation ---
    crf = calculate_capital_recovery_factor(LOAN_INTEREST_RATE, LOAN_YEARS)
    results = []
    
    for pv_size_kwp in np.arange(0, 25.5, 0.5):
        initial_investment = pv_size_kwp * COST_PER_KWP_INSTALLED
        annualized_pv_cost = initial_investment * crf
        monthly_pv_generation_elec = monthly_pv_generation_per_kwp * pv_size_kwp
        
        elec_needed_for_cooling = demand_cool / COOLING_EER
        elec_from_pv_for_cooling = np.minimum(monthly_pv_generation_elec, elec_needed_for_cooling)
        unmet_cooling_elec_demand = elec_needed_for_cooling - elec_from_pv_for_cooling
        
        elec_remaining_after_cooling = monthly_pv_generation_elec - elec_from_pv_for_cooling
        heat_from_pv_thermal = elec_remaining_after_cooling * HEAT_PUMP_COP
        
        unmet_heating_demand_thermal = np.maximum(0, (demand_acs + demand_cal) - heat_from_pv_thermal)
        
        cost_of_grid_imports = unmet_cooling_elec_demand.sum() * GRID_IMPORT_PRICE_KWH
        cost_of_biomass = unmet_heating_demand_thermal.sum() * BIOMASS_COST_PER_KWH
        
        elec_used_for_heating = np.minimum(elec_remaining_after_cooling, (demand_acs + demand_cal) / HEAT_PUMP_COP)
        surplus_elec = elec_remaining_after_cooling - elec_used_for_heating
        revenue_from_exports = surplus_elec.sum() * GRID_EXPORT_PRICE_KWH
        
        total_annual_cost = (annualized_pv_cost + cost_of_biomass + cost_of_grid_imports - revenue_from_exports)
        
        results.append({'pv_size_kwp': pv_size_kwp, 'total_annual_cost': total_annual_cost})

    # --- Find and Print the Optimum ---
    results_df = pd.DataFrame(results)
    optimal_result = results_df.loc[results_df['total_annual_cost'].idxmin()]
    
    cost_no_pv_heating = (demand_acs.sum() + demand_cal.sum()) * BIOMASS_COST_PER_KWH
    cost_no_pv_cooling = (demand_cool.sum() / COOLING_EER) * GRID_IMPORT_PRICE_KWH
    cost_no_pv = cost_no_pv_heating + cost_no_pv_cooling
    results_df['annual_savings'] = cost_no_pv - results_df['total_annual_cost']
    
    print("--- PV System Optimization Results (Advanced Model - Corrected) ---")
    print(f"Optimal PV System Size: {optimal_result['pv_size_kwp']:.1f} kWp")
    
    # --- Generate Plots ---
    plot_savings_vs_kwp(results_df)
    plot_monthly_energy_balance(optimal_result['pv_size_kwp'], demand_acs, demand_cal, demand_cool, monthly_pv_generation_per_kwp)
    
    print(f"\nCharts have been saved to the '{output_folder}' directory.")

def plot_savings_vs_kwp(results_df):
    plt.figure(figsize=(10, 6))
    optimal_kwp = results_df.loc[results_df['annual_savings'].idxmax()]['pv_size_kwp']
    plt.plot(results_df['pv_size_kwp'], results_df['annual_savings'], marker='.', linestyle='-')
    plt.axvline(x=optimal_kwp, color='r', linestyle='--', label=f"Optimal Size: {optimal_kwp:.1f} kWp")
    plt.title('Estimated Annual Savings vs. PV System Size (Advanced Model)')
    plt.xlabel('PV System Size (kWp)')
    plt.ylabel('Annual Savings (EUR)')
    plt.xlim(0, 3)
    plt.ylim(bottom=0) # Set Y-axis to start at 0
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(output_folder, 'optimization_savings_vs_kwp_advanced.png'))
    plt.close()

def plot_monthly_energy_balance(optimal_kwp, demand_acs, demand_cal, demand_cool, pv_gen_per_kwp):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_pv_generation_elec = pv_gen_per_kwp * optimal_kwp
    elec_needed_for_cooling = demand_cool / COOLING_EER
    elec_from_pv_for_cooling = np.minimum(monthly_pv_generation_elec, elec_needed_for_cooling)
    elec_remaining_after_cooling = monthly_pv_generation_elec - elec_from_pv_for_cooling
    heat_from_pv_thermal = elec_remaining_after_cooling * HEAT_PUMP_COP
    
    total_pv_supply_equivalent = (elec_from_pv_for_cooling * COOLING_EER) + heat_from_pv_thermal

    plt.figure(figsize=(12, 7))
    
    plt.bar(months, demand_acs, label='DHW Demand', color='#1f77b4')
    plt.bar(months, demand_cal, bottom=demand_acs, label='Heating Demand', color='#ff7f0e')
    plt.bar(months, demand_cool, bottom=demand_acs + demand_cal, label='Cooling Demand', color='#d62728')
    
    plt.plot(months, total_pv_supply_equivalent, marker='o', linestyle='--', color='black', label='Total Supply from PV')
    
    plt.title(f'Monthly Energy Demand & PV Supply for Optimal {optimal_kwp:.1f} kWp System')
    plt.xlabel('Month')
    plt.ylabel('Energy (kWh)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'optimal_monthly_energy_balance.png'))
    plt.close()

# ==========================================
# 3. EXECUTION
# ==========================================

if __name__ == "__main__":
    run_optimization()
