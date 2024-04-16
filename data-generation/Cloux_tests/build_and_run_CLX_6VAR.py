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

# Load the configuration file
config = ds.load_config('ConfigFiles/Config_CLX-MILP.xlsx')

# Parameters 
config['SimulationDirectory'] = 'simulations/simu_cloux_slurm/1001_1030_MILP'
config['SimulationType'] = 'Integer clustering' # 'LP clustered'
config['StartDate'] = (2019, 10, 1, 0, 0, 0)
config['StopDate'] = (2019, 10, 30, 0, 0, 0)

# Build the simulation environment:
SimData = ds.build_simulation(config)

# Modify some of the inputs with the availables functions : 
    
# SimData = ds.adjust_flexibility(inputs, flex_units, slow_units, flex_ratio, singleunit=False, write_gdx=False, dest_path='')    
    
# SimData = ds.adjust_ntc(inputs, value=None, write_gdx=False, dest_path='')    
    
# SimData = ds.adjust_capacity(inputs, tech_fuel, scaling=1, value=None, singleunit=False, write_gdx=False, dest_path='')    
   
# SimData = ds.adjust_unit_capacity(SimData, u_idx, scaling=1, value=None, singleunit=False) 
    
# Solve using GAMS:
r = ds.solve_GAMS(config['SimulationDirectory'], config['GAMS_folder'])