# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:41:31 2024

@author: romai
"""

import numpy as np
import pandas as pd

#slow 2050
nuc_cap = 55047 #MWe
foss_cap = 118191
solfoss_cap = 11604
petrol_cap = 1755

slow_2020 = 107457 + 324425 + 131085 + 27730
slow_2050 = nuc_cap + foss_cap + solfoss_cap

#flex 2050
gas_cap = 104831
biogas_cap = 55589

flex_2020 = 57604 + 165611
flex_2050 = gas_cap + biogas_cap + petrol_cap

#demand 2050 
demand_GWh = 3012786
CF_demand = 0.736
Peak_load_2050 = demand_GWh/(8760*CF_demand) #GW

demand_GWh_2020 = 2300000
Peak_load_2020 = demand_GWh_2020/(8760*CF_demand) #GW
# VRES 

Windon_gen = 990670 #GWh
Windoff_gen = 359768 #GWh
Solar_gen = 599657 #GWh

# Storage

# NTC

# INPUTS CALCULATIONS

CR_2020 = (slow_2020 + flex_2020)*1e-3/Peak_load_2020
CR_2050 = (slow_2050 + flex_2050)*1e-3/Peak_load_2050

share_flex_2020 = flex_2020/(slow_2020+flex_2020)
share_flex_2050 = flex_2050/(slow_2050+flex_2050)

share_wind_2050 = (Windon_gen + Windoff_gen)/demand_GWh

pv_2050 = Solar_gen/demand_GWh

# PRINT 

print('CR 2020:  ' + str(CR_2020))
print('CR 2050:  ' + str(CR_2050))
print('flex 2020:  ' + str(share_flex_2020))
print('flex 2050:  ' + str(share_flex_2050))
print('Wind 2050:  ' + str(share_wind_2050))
print('PV 2050:  ' + str(pv_2050))
print('Storage 2050:  ' + str(CR_2050))
print('rNTC 2050:  ' + str(CR_2050))