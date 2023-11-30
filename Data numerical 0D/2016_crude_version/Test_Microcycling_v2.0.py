import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from LiS_Module_Solver import LiS_Solver

## Now we call the solver and solve ##
span = 3600
t0 = 0
t_end = t0 + span # End time
h0 = 0.05 # Initial step size

## Initialize the variable values and arrays for microcycling
## Start with Discharge 1st
s8i = 2.6892000000000003
s4i = 0.0027
s2i = 0.002697299116926997
si = 8.83072852310722e-10
spi = 2.7e-06
Vi = 2.430277479547109
I = 1.7 # Current (constant)
discharge_break = 2.241 # Voltage point where simulation is stopped to prevent Singular Matrix Error
charge_break = 2.45

cycles = 1 ## Number of cycles to run (1 cycle is Discharge followed by Charge)
overall_array = []
for j in range(cycles):
    overall_array.append([])
    

## Run the solver within a for loop and cycle between Discharge and Charge
for i in range(cycles):
    # Discharge
    solved = LiS_Solver(s8i, s4i, s2i, si, Vi, spi, 
                        t_end, h0, I, discharge_break, state='Discharge', t0=t0)
    

    list1 = solved
    overall_array[i].append(list1)
    s8i = solved[0][-1]
    s4i = solved[1][-1]
    s2i = solved[2][-1]
    si = solved[3][-1]
    Vi = solved[4][-1]
    spi = solved[5][-1]
    t0 = solved[6][-1]
    t_end = t0 + span
    
    # Charge
    solved2 = LiS_Solver(s8i, s4i, s2i, si, Vi, spi, 
                        t_end, 1, -I, charge_break, state='Charge', t0=t0)
    
    list2 = solved2
    overall_array[i].append(list2)
    s8i = solved2[0][-1]
    s4i = solved2[1][-1]
    s2i = solved2[2][-1]
    si = solved2[3][-1]
    Vi = solved2[4][-1]
    spi = solved2[5][-1]
    t0 = solved2[6][-1]
    t_end = t0 + span
      
    print(f'No. Cycles: {i+1}/{cycles}')

overall_array_np = np.empty(len(overall_array), dtype=object)
overall_array_np[:] = overall_array

## Now we save the array above ##
## The results can be obtained in the Test_Saved_Microcycling.py script
np.savez('variable_arrays.npz', solved=overall_array_np, I=I)
print("Solved array returned in the form: [s8_array, s4_array, s2_array, s_array, V_array, sp_array, time_array]")
print("The indexing of the variables follows the list above, Ex: Voltage is index:4 or Precipitated Sulfur is index:5")

excel_array = []
excel_2_array = []

for i in range(len(overall_array_np[0][0][0])-1):
    list = []
    list2 = []
    for j in range(len(overall_array_np[0][0])):
        list.append(overall_array[0][0][j][i])
        list2.append(overall_array[0][0][j][i+1])
    excel_array.append(list)
    excel_2_array.append(list2)

excel_array = np.array(excel_array)
excel_2_array = np.array(excel_2_array)


concatenated_array = np.concatenate((excel_array, excel_2_array), axis = 1)


columns = ['S8_cur','S4_cur','S2_cur','S1_cur','V_cur', 'Sp_cur','t_cur', 'S8_nxt','S4_nxt','S2_nxt','S1_nxt','V_nxt', 'Sp_nxt','t_nxt']

df = pd.DataFrame(concatenated_array[:, :], columns=columns)

file_path = 'C:/Users/ADITYA/OneDrive - Imperial College London/Year 4/FYP/Final-year-project/Data numerical 0D/2016_crude_version/dataset.xlsx'

df.to_excel(file_path, index=True)