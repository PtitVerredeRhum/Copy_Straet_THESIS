# -*- coding: utf-8 -*-
"""
Minimalist example file showing how to access the Dispa-SET api to read a configuration file, 
create a simulation environment folder and run the simulation in GAMS

@author: Sylvain Quoilin
"""

# Add the root folder of Dispa-SET to the path so that the library can be loaded:
import sys,os
sys.path.append(os.path.abspath('..'))

# Import Dispa-SET
import dispaset as ds
import pandas as pd
# Load the configuration file
config = ds.load_config('../ConfigFiles/Config_CLX-MILP.xlsx')

# Parameters 
config['SimulationDirectory'] = 'simulations/simu_cloux_slurm/adj_VRES_1001-1030_LP'
config['SimulationType'] = 'LP clustered' #'Integer clustering' # 'LP clustered'
config['StartDate'] = (2019, 10, 1, 0, 0, 0)
config['StopDate'] = (2019, 10, 30, 0, 0, 0)

adj_sto = False 
adj_ren = True
adj_flex = False
ajd_ntc = False
adj_cr = False

# Build the simulation environment:
sim_data = ds.build_simulation(config)


# CALCUL SOME IMPORTANT VALUES
print("#-#-#-#-#-#-# Build simulation end")

# POST PROCESSING !!! #############################################################################################


 # Extract some significant values from the config:
peak_load = sim_data["parameters"]["Demand"]["val"][0].sum(axis=0).max()

availability_factors = sim_data["parameters"]["AvailabilityFactor"]["val"].mean(axis=1)
af_df = pd.DataFrame(availability_factors, index=sim_data["sets"]["au"], columns=["availability_factor_avg"])

CF_pv = af_df.filter(like="PHOT", axis=0).mean().loc["availability_factor_avg"]
CF_wton_list0 = af_df.filter(like="WindOn", axis=0)
CF_wton_list1 = af_df.filter(like="WTON", axis=0)
CF_wton_list = pd.concat([CF_wton_list0, CF_wton_list1])
CF_wton = CF_wton_list.mean().loc["availability_factor_avg"]
#CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc("availability_factor_avg")
CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc["availability_factor_avg"]
#CF_wtof = 3.14

units = sim_data["units"]
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
variable_costs = sim_data["parameters"]["CostVariable"]["val"]
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
h_mean = sim_data['parameters']['FlowMaximum']['val'].mean(axis=1)
NTC = pd.DataFrame(h_mean, index=sim_data['sets']['l'], columns=['FlowMax_hmean']).groupby(level=0).sum()

countries = sim_data['sets']['n']
max_load = sim_data['parameters']['Demand']['val'][0].max(axis=1)
     
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


######################################################################################################
######################################################################################################


tmp = os.environ["GLOBALSCRATCH"] + os.sep + "Temp_folder"  + os.sep + "Inputstmp.gdx"
    

if adj_sto :
    # ADJUST STORAGE:
    data = ds.adjust_capacity(sim_data, ('BATS','OTH'), singleunit=True, 
                                value=peak_load*0.75, write_gdx=True, dest_path=config['SimulationDirectory'])
if  adj_ren :   
    # ADJUST WIND AND PV :
    data = ds.adjust_capacity(sim_data, ('WTON','WIN'),
                            value=peak_load*0.065/CF_wton, singleunit=True)
    data = ds.adjust_capacity(data, ('WTOF','WIN'),
                            value=peak_load*0.3/CF_wtof, singleunit=True)
    data = ds.adjust_capacity(data, ('PHOT','SUN'),
                            value=peak_load*0.15/CF_pv, singleunit=True, write_gdx=True, dest_path=config['SimulationDirectory'])
if  adj_flex : 
    # ADJUST FLEX
    data = ds.adjust_flexibility(sim_data, flex_units, slow_units, 0.8, singleunit=True, write_gdx=True, dest_path=config['SimulationDirectory'])
if ajd_ntc :   
    # ADJUST NTC
    data = ds.adjust_ntc(sim_data, value=0.64, write_gdx=True, dest_path=config['SimulationDirectory'])
if adj_cr :   
    # ADJUST CAPACITY_RATIO
    data = ds.adjust_unit_capacity(sim_data, flex_units, value=1.0*peak_load - (units.PowerCapacity[slow_units].sum() + units.PowerCapacity[sto_units].sum()), singleunit=True)
    data = ds.adjust_unit_capacity(data, slow_units, value=1.0*peak_load - (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[sto_units].sum()), singleunit=True)
    data = ds.adjust_unit_capacity(data, sto_units, value=1.0*peak_load - (units.PowerCapacity[slow_units].sum() + units.PowerCapacity[flex_units].sum()), singleunit=True, write_gdx=True, dest_path=config['SimulationDirectory'])

# Solve using GAMS:
r = ds.solve_GAMS(config['SimulationDirectory'], config['GAMS_folder'])
