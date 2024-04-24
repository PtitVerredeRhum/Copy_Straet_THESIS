# -*- coding: utf-8 -*-
"""
Minimalist example file showing how to read the results of a Dispa-SET run

@author: Sylvain Quoilin
"""

# Add the root folder of Dispa-SET to the path so that the library can be loaded:
import sys,os
sys.path.append(os.path.abspath('..'))

# Import Dispa-SET
import dispaset as ds

#IMPORT
import pandas as pd

# Load the inputs and the results of the simulation
#inputs,results = ds.get_sim_results(path='../Simulations/simulation_test',cache=False)
inputs,results = ds.get_sim_results(path='../simulations/simu_cloux/1001_1030_LP',cache=False)

# POST PROCESSING !!! #############################################################################################


 # Extract some significant values from the config:
peak_load = inputs["parameters"]["Demand"]["val"][0].sum(axis=0).max()

availability_factors = inputs["parameters"]["AvailabilityFactor"]["val"].mean(axis=1)
af_df = pd.DataFrame(availability_factors, index=inputs["sets"]["au"], columns=["availability_factor_avg"])

CF_pv = af_df.filter(like="PHOT", axis=0).mean().loc["availability_factor_avg"]
CF_wton_list0 = af_df.filter(like="WindOn", axis=0)
CF_wton_list1 = af_df.filter(like="WTON", axis=0)
CF_wton_list = pd.concat([CF_wton_list0, CF_wton_list1])
CF_wton = CF_wton_list.mean().loc["availability_factor_avg"]
#CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc("availability_factor_avg")
CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc["availability_factor_avg"]
#CF_wtof = 3.14

units = inputs["units"]
flex_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & (units.PartLoadMin < 0.5) & (units.TimeUpMinimum <5)  & (units.RampUpRate > 0.01)  ].index
slow_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & ((units.PartLoadMin >= 0.5) | (units.TimeUpMinimum >=5)  | (units.RampUpRate <= 0.01)   )  ].index
#sto_units  = units[ units.Fuel.isin( ['OTH'] ) ].index
sto_units  = units[ units.Technology == 'BATS' ].index
#wind_units = units[ units.Fuel.isin( ['WIN'] ) ].index 
windon_units = units[ units.Technology == 'WTON' ].index 
windoff_units = units[ units.Technology == 'WTOF' ].index 
pv_units   = units[ units.Technology == 'PHOT'].index   
hror_units = units[ units.Technology == 'HROR'].index   
coal_units = units[units.Fuel.isin(["HRD"])].index
variable_costs = inputs["parameters"]["CostVariable"]["val"]
for u in coal_units:
    idx = coal_units.get_loc(u)
    variable_cost = variable_costs[idx].mean()
    print(f"Variable cost for {u} (idx: {idx}): {variable_cost}")
ref = {}
ref['overcapacity'] = (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum() + units.PowerCapacity[sto_units].sum()) / peak_load
ref['share_flex'] =   units.PowerCapacity[flex_units].sum() / (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum())
ref['share_sto'] =    units.PowerCapacity[sto_units].sum() / peak_load
ref['share_wind_on'] =   units.PowerCapacity[windon_units].sum() / peak_load * CF_wton
ref['share_wind_off'] =   units.PowerCapacity[windoff_units].sum() / peak_load * CF_wtof
ref['share_pv'] =     units.PowerCapacity[pv_units].sum() / peak_load * CF_pv


# Computing rNTCs
h_mean = inputs['parameters']['FlowMaximum']['val'].mean(axis=1)
NTC = pd.DataFrame(h_mean, index=inputs['sets']['l'], columns=['FlowMax_hmean']).groupby(level=0).sum()

countries = inputs['sets']['n']
max_load = inputs['parameters']['Demand']['val'][0].max(axis=1)
     
peak_load_df = pd.DataFrame(max_load, index=countries, columns=['max_load'])
     
for c in countries:
    ntc = 0
    for l in NTC.index:
        if c in l: 
            ntc += NTC.loc[l,'FlowMax_hmean']
    peak_load_df.loc[c,'rNTC'] = ntc / 2 / peak_load_df.loc[c,'max_load']

peak_load_df['weigthed'] = peak_load_df['max_load'] * peak_load_df['rNTC'] / peak_load_df['max_load'].sum()

ref['rNTC'] = peak_load_df['weigthed'].sum()     

#refinfo = ReferenceInfo.from_values(peak_load, flex_units, slow_units, CF_wton, CF_wtof, CF_pv, ref)
#refinfo.serialize(refinfo_path)

print(af_df.filter(like="WTOF", axis=0))
print("----------------------------------------------------")

print("CF WTON: ", CF_wton)
print("CF WTOF: ", CF_wtof)
print(af_df.filter(like="WTOF", axis=0).mean())
print("CF PV: ", CF_pv)
print("peak load: ", peak_load)

CF_pv2_list = af_df.filter(like="PHOT", axis=0)
CF_pv2_list[CF_pv2_list["availability_factor_avg"].ne(0)].mean().loc["availability_factor_avg"]

CF_wton_list = af_df.filter(like="WTON", axis=0)
CF_wton_list[CF_wton_list["availability_factor_avg"].ne(0)].mean().loc["availability_factor_avg"]

CF_wtof_list = af_df.filter(like="WTOF", axis=0)
CF_wtof_list[CF_wtof_list["availability_factor_avg"].ne(0)].mean().loc["availability_factor_avg"]

print('CR: ', ref['overcapacity'])
print('flex: ', ref['share_flex'])
print('sto: ', ref['share_sto'])
print('on: ', ref['share_wind_on'])
print('off: ', ref['share_wind_off'])
print('pv: ', ref['share_pv'])
print('NTC: ', ref['rNTC'])




# PLOT !!! #############################################################################################
# PLOT !!! #############################################################################################

# if needed, define the plotting range for the dispatch plot:
import pandas as pd
rng = pd.date_range(start='2019-10-01',end='2019-10-30',freq='h')

# Generate country-specific plots
ds.plot_zone(inputs,results, z='FR', z_th='FR_th', rng=rng)

# # Bar plot with the installed capacities in all countries:
# cap = ds.plot_zone_capacities(inputs,results)

# # Bar plot with installed storage capacity
# #sto = ds.plot_tech_cap(inputs)

# # Violin plot for CO2 emissions
# ds.plot_co2(inputs, results, figsize=(9, 6), width=0.9)

# # Bar plot with the energy balances in all countries:
# ds.plot_energy_zone_fuel(inputs,results,ds.get_indicators_powerplant(inputs,results))

# # Analyse the results for each country and provide quantitative indicators:
# r = ds.get_result_analysis(inputs,results)

# # Plot the reservoir levels
# #ds.storage_levels(inputs,results)
# #ds.plot_storage_levels(inputs,results,'NO')

# # Analyze power flow tracing
# pft, pft_prct = ds.plot_power_flow_tracing_matrix(inputs, results, cmap="magma_r", figsize=(15, 10))

# # Plot net flows on a map
# ds.plot_net_flows_map(inputs,results)

# # Plot congestion in the interconnection lines on a map
# #ds.plot_line_congestion_map(inputs,results)