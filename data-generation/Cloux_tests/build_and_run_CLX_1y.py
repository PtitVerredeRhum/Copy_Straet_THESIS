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
import numpy as np
# Load the configuration file
config = ds.load_config('ConfigFiles/Config_CLX-MILP.xlsx')

# Parameters 
config['SimulationDirectory'] = 'simulations/simu_cloux_slurm/Test_MILP_1y_60euMWH'
config['SimulationType'] = 'Integer clustering' #'Integer clustering' # 'LP clustered'
config['StartDate'] = (2019, 1, 1, 0, 0, 0)
config['StopDate'] = (2019, 12, 31, 0, 0, 0)

adj_sto = True 
adj_ren = True
adj_flex = True
ajd_ntc = True
adj_cr = True

# Build the simulation environment:
sim_data = ds.build_simulation(config)


# CALCUL SOME IMPORTANT VALUES
print("#-#-#-#-#-#-# Build simulation end")

# POST PROCESSING !!! #############################################################################################


 # Extract some significant values from the config:
peak_load = sim_data["parameters"]["Demand"]["val"][0].sum(axis=0).max()
FC = (sim_data["parameters"]["Demand"]["val"][0].sum().sum())/(peak_load*8784)
availability_factors = sim_data["parameters"]["AvailabilityFactor"]["val"].mean(axis=1)
af_df = pd.DataFrame(availability_factors, index=sim_data["sets"]["au"], columns=["availability_factor_avg"])

CF_pv = af_df.filter(like="PHOT", axis=0).mean().loc["availability_factor_avg"]
CF_wton_list0 = af_df.filter(like="WindOn", axis=0)
CF_wton_list1 = af_df.filter(like="WTON", axis=0)
CF_wton_list = pd.concat([CF_wton_list0, CF_wton_list1])
CF_wton = CF_wton_list.mean().loc["availability_factor_avg"]
#CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc("availability_factor_avg")
#CF_wtof = af_df.filter(like="WTOF", axis=0).mean().loc["availability_factor_avg"]
#CF_wtof = 3.14
filtered_df = af_df.filter(like="WTOF", axis=0)
filtered_df.replace(0.0, np.nan, inplace=True)
CF_wtof = filtered_df.mean().loc["availability_factor_avg"]

units = sim_data["units"]
flex_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & (units.PartLoadMin < 0.5) & (units.TimeUpMinimum <5)  & (units.RampUpRate > 0.01)  ].index
slow_units = units[ units.Fuel.isin( ['GAS','HRD','OIL','BIO','LIG','PEA','NUC','GEO'] ) & ((units.PartLoadMin >= 0.5) | (units.TimeUpMinimum >=5)  | (units.RampUpRate <= 0.01)   )  ].index
base_units = flex_units.append(slow_units)
#sto_units  = units[ units.Fuel.isin( ['OTH'] ) ].index
sto_units  = units[ units.Technology == 'BATS' ].index
#wind_units = units[ units.Fuel.isin( ['WIN'] ) ].index 
windon_units = units[ units.Technology == 'WTON' ].index 
windoff_units = units[ units.Technology == 'WTOF' ].index 
pv_units   = units[ units.Technology == 'PHOT'].index   
hror_units = units[ units.Technology == 'HROR'].index   
coal_units = units[units.Fuel.isin(["HRD"])].index
variable_costs = sim_data["parameters"]["CostVariable"]["val"]

# Cosnidering that there are no Stationnary batteries in 2019 , a low value of Power Capacity of 10MW is considered for each.
units.PowerCapacity[sto_units] = 10 #MW

for u in coal_units:
    idx = coal_units.get_loc(u)
    variable_cost = variable_costs[idx].mean()
    print(f"Variable cost for {u} (idx: {idx}): {variable_cost}")
ref = {}
ref['overcapacity'] = (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum()) / peak_load
ref['share_flex'] =   units.PowerCapacity[flex_units].sum() / (units.PowerCapacity[flex_units].sum() + units.PowerCapacity[slow_units].sum())
ref['share_sto'] =    units.PowerCapacity[sto_units].sum() / peak_load
ref['share_wind_on'] =   units.PowerCapacity[windon_units].sum()* CF_wton / (peak_load*FC)
ref['share_wind_off'] =   units.PowerCapacity[windoff_units].sum()* CF_wtof / (peak_load*FC)
ref['share_wind'] =   ((units.PowerCapacity[windon_units].sum()* CF_wton) + (units.PowerCapacity[windoff_units].sum()* CF_wtof)) / (peak_load*FC) 
ref['share_pv'] =     units.PowerCapacity[pv_units].sum()* CF_pv / (peak_load*FC) 


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
    
FC_load = 0.736 #based on reference database demand
    
    #if share_flex > 0.905:
    #    print("Killing stalling simulation at the root")
    #    return 1

if adj_sto :     
    # ADJUST STORAGE:
    data = ds.adjust_capacity(sim_data, ('BATS','OTH'), singleunit=True, 
                                value=peak_load*1.708981)
if adj_cr : 
    # ADJUST CAPACITY_RATIO : Variable dépendante de share storage et de share flex =>
    resultat = []
    base_units = flex_units.append(slow_units)
    for index in base_units:
         terme = index.split('_')[1]  # Récupérer le deuxième terme
         terme_suivant = index.split('_')[2]  # Récupérer le troisième terme
         tuple_actuel = (terme, terme_suivant)
         if tuple_actuel not in resultat:  # Vérifier si le tuple n'est pas déjà dans la liste
             resultat.append(tuple_actuel)
             data = ds.adjust_capacity(data, tuple_actuel, scaling=(1.291183)/(ref['overcapacity']), singleunit=True)
 
    
    
    # ADJUST FLEX
if  adj_flex : 
    data = ds.adjust_flexibility(data, flex_units, slow_units, 0.757526, singleunit=True)
    
    
    # dispa-set function to adjust the ntc:
    # ADJUST NTC
if ajd_ntc :
    data = ds.adjust_ntc(data, value=0.393664/ref['rNTC'])
    
   
    
    # tmp = os.environ["LOCALSCRATCH"] + os.sep + "Inputs.gdx"
if  adj_ren :    
    # For wind and PV, the units should be lumped into a single unit:
        # ADJUST WIND AND PV :
    #
    perc_off = 0.3 # 2050 capacity installed : 100 000MWe * CF_wtof = 37 800
    perc_on = 0.7 # 2050 capacity installed : 400 000MWe* CF_wton =  100 000
    
    data = ds.adjust_capacity(data, ('WTOF','WIN'),
                            value=(peak_load*FC_load)/CF_wtof*(perc_off*0.343041), singleunit=True)
    data = ds.adjust_capacity(data, ('WTON','WIN'),
                            value=(peak_load*FC_load)/CF_wton*(perc_on*0.343041), singleunit=True)
    data = ds.adjust_capacity(data, ('PHOT','SUN'),
                            value=(peak_load*FC_load)*0.316212/CF_pv, singleunit=True,write_gdx=True,dest_path=config['SimulationDirectory'])

# Solve using GAMS by scirpt.sh

#r = ds.solve_GAMS(config['SimulationDirectory'], config['GAMS_folder'])