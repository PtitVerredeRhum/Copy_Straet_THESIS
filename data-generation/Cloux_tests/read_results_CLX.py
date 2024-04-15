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

# Load the inputs and the results of the simulation
#inputs,results = ds.get_sim_results(path='../Simulations/simulation_test',cache=False)
inputs,results = ds.get_sim_results(path='../simulations/simu_cloux/0102_0702-LPCLUS',cache=False)

# if needed, define the plotting range for the dispatch plot:
import pandas as pd
rng = pd.date_range(start='2019-01-01',end='2019-01-07',freq='h')

# Generate country-specific plots
ds.plot_zone(inputs,results,rng=rng)

# Bar plot with the installed capacities in all countries:
cap = ds.plot_zone_capacities(inputs,results)

# Bar plot with installed storage capacity
#sto = ds.plot_tech_cap(inputs)

# Violin plot for CO2 emissions
ds.plot_co2(inputs, results, figsize=(9, 6), width=0.9)

# Bar plot with the energy balances in all countries:
ds.plot_energy_zone_fuel(inputs,results,ds.get_indicators_powerplant(inputs,results))

# Analyse the results for each country and provide quantitative indicators:
r = ds.get_result_analysis(inputs,results)

# Plot the reservoir levels
#ds.storage_levels(inputs,results)
#ds.plot_storage_levels(inputs,results,'NO')

# Analyze power flow tracing
pft, pft_prct = ds.plot_power_flow_tracing_matrix(inputs, results, cmap="magma_r", figsize=(15, 10))

# Plot net flows on a map
ds.plot_net_flows_map(inputs,results)

# Plot congestion in the interconnection lines on a map
#ds.plot_line_congestion_map(inputs,results)