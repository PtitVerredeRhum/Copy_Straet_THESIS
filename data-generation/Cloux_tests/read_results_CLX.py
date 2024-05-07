# -*- coding: utf-8 -*-
"""
Minimalist example file showing how to read the results of a Dispa-SET run

@author: Sylvain Quoilin
"""

# Add the root folder of Dispa-SET to the path so that the library can be loaded:
import sys,os, re
sys.path.append(os.path.abspath('..'))

# Import Dispa-SET
import dispaset as ds

#IMPORT
import pandas as pd
import numpy as np
# Load the inputs and the results of the simulation
#inputs,results = ds.get_sim_results(path='../Simulations/simulation_test',cache=False)
path='../simulations/simu_cloux/TestALLTrue_CR_250' #'adj_VRES_1001-1030_LP' 
inputs,results = ds.get_sim_results(path,cache=False)

peak_load = inputs["parameters"]["Demand"]["val"][0].sum(axis=0).max()

availability_factors = inputs["parameters"]["AvailabilityFactor"]["val"].mean(axis=1)
af_df = pd.DataFrame(availability_factors, index=inputs["sets"]["au"], columns=["availability_factor_avg"])

CF_pv = af_df.filter(like="PHOT", axis=0).mean().loc["availability_factor_avg"]
CF_wton_list0 = af_df.filter(like="WindOn", axis=0)
CF_wton_list1 = af_df.filter(like="WTON", axis=0)
CF_wton_list = pd.concat([CF_wton_list0, CF_wton_list1])
CF_wton = CF_wton_list.mean().loc["availability_factor_avg"]
#CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc("availability_factor_avg")
filtered_df = af_df.filter(like="WTOF", axis=0)
filtered_df.replace(0.0, np.nan, inplace=True)
CF_wtof = filtered_df.mean().loc["availability_factor_avg"]

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





# POST PROCESSING !!! #############################################################################################

fuel_power = ds.aggregate_by_fuel(results["OutputPower"], inputs, SpecifyFuels=None)
capacities = ds.plot_zone_capacities(inputs, results, plot=False)

zone_results = ds.get_result_analysis(inputs, results)

lost_load = 0
for key in ["LostLoad_MaxPower", "LostLoad_MinPower", "LostLoad_2D", "LostLoad_2U", "LostLoad_3U", "LostLoad_RampDown", "LostLoad_RampUp"]:
    if key in results:
        lost_load += results[key].sum().sum()

total_generation = results["OutputPower"].sum().sum()

# read pd.Series from csv
# then add elements to the row
#m = re.search("/sim-(\d+)_", path)
# m[0]: entire match, m[1]: first group
#sample_index = int(m[1])
#samples = pd.read_csv(SIMULATIONS_DIR + os.sep + SAMPLES_CSV_NAME, index_col=0)

params = inputs["parameters"]
afs = params["AvailabilityFactor"]

all_af = pd.DataFrame(np.transpose(afs["val"]),
                      columns=inputs["sets"]["au"], 
                      index=inputs["sets"]["h"])
af = ds.filter_by_tech_list(all_af, inputs, ["HROR", "PHOT", "WTON", "WTOF"])

all_pc = pd.DataFrame(np.expand_dims(params["PowerCapacity"]["val"], axis=0),
                      columns=inputs["sets"]["au"],
                      index=["val"])
pc = ds.filter_by_tech_list(all_pc, inputs, ["HROR", "PHOT", "WTON", "WTOF"])

En = af.mean() * pc
Energy2 = af.dot(pc.transpose())
total_vres = 365 * 24 * En.sum().sum() / 1E6
total_vres2 = 365 * 24 * Energy2.sum() / 1E6

print("af mean desc")
print(af.mean().describe())
print(af.columns)
print(len(af.index))

print("pc desc")
print(pc.describe())
print(pc.columns)
print(len(pc.index))

print("En")
print(En.describe())
print(En.columns)
print(len(En.index))

#row = samples.loc[sample_index,:]
#print(f"Read single index:  {sample_index}")

zone_results["Cost_[E/MWh]"] = zone_results["Cost_kwh"]
zone_results["Congestion_[h]"] = sum(zone_results["Congestion"].values())

zone_results["PeakLoad_[MW]"] = zone_results["PeakLoad"]

zone_results['MaxCurtailment_[MW]'] = zone_results['MaxCurtailment']
zone_results['MaxLoadShedding_[MW]'] = zone_results['MaxShedLoad']

zone_results['Demand_[TWh]'] = zone_results['TotalLoad'] / 1E6
zone_results['NetImports_[TWh]']= zone_results['NetImports'] / 1E6

zone_results['Curtailment_[TWh]'] = zone_results['Curtailment'] / 1E6
zone_results['Shedding_[TWh]'] = zone_results['ShedLoad'] / 1E6
zone_results['LostLoad_[TWh]'] = lost_load / 1E6

zone_results['MaxRESGeneration_[TWh]'] = total_vres2
zone_results['CurtailmentToRESGeneration_[%]'] = 100 * zone_results['Curtailment_[TWh]'] / total_vres2
zone_results['TotalGeneration_[TWh]'] = total_generation / 1E6
zone_results['ShareResGeneration_[%]'] = 100 * total_vres2 / total_generation
#row.loc['MaxLoadSheddingShare_[%]'] = 100 * zone_results['MaxShedLoadShare']
zone_results['MaxLoadSheddingShare_[%]'] = 0
cf = {}
#for fuel in ["GAS", "NUC", "WAT", "WIN", "SUN"]:
#    cf[fuel] = fuel_power[fuel].sum() / (capacities["PowerCapacity"][fuel].sum() * 8760)
#    keyname = "CF_" + fuel.lower()
#    row.loc[keyname] = cf[fuel]

#print("Curtailment to RES generation: ", row.loc['CurtailmentToRESGeneration_[%]'])



# PLOT !!! #############################################################################################
# PLOT !!! #############################################################################################

# # if needed, define the plotting range for the dispatch plot:
# import pandas as pd
# rng = pd.date_range(start='2019-10-09',end='2019-10-25',freq='h')

# # Generate country-specific plots
# ds.plot_zone(inputs,results, z='SE', z_th='SE_th', rng=rng)

# ds.plot_zone(inputs,results, z='DE', z_th='DE_th', rng=rng)

# # #Bar plot with the installed capacities in all countries:
# cap = ds.plot_zone_capacities(inputs,results)

# # #Bar plot with installed storage capacity
# sto = ds.plot_tech_cap(inputs)

# # #Violin plot for CO2 emissions
# ds.plot_co2(inputs, results, figsize=(9, 6), width=0.9)

# # #Bar plot with the energy balances in all countries:
# ds.plot_energy_zone_fuel(inputs,results,ds.get_indicators_powerplant(inputs,results))

# # #Analyse the results for each country and provide quantitative indicators:
# # #r = ds.get_result_analysis(inputs,results)

# # #Plot the reservoir levels
# #ds.plot_storage_levels(inputs,results,'DE')

# # #Analyze power flow tracing
# # #pft, pft_prct = ds.plot_power_flow_tracing_matrix(inputs, results, cmap="magma_r", figsize=(15, 10))

# # #Plot net flows on a map
# ds.plot_net_flows_map(inputs,results)

# # #Plot congestion in the interconnection lines on a map
# # ds.plot_line_congestion_map(inputs,results)