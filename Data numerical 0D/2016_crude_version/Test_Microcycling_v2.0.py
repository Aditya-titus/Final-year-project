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
I = [1.6,1.7,1.8]
discharge_break = 2.241 # Voltage point where simulation is stopped to prevent Singular Matrix Error
charge_break = 2.45

final_array = []

for k in range(len(I)):

    cycles = 1 ## Number of cycles to run (1 cycle is Discharge followed by Charge)
    overall_array = []
    
    for j in range(cycles):
        overall_array.append([])

    ## Run the solver within a for loop and cycle between Discharge and Charge
    for i in range(cycles):
        # Discharge
        solved = LiS_Solver(s8i, s4i, s2i, si, Vi, spi, 
                            t_end, h0, I[k], discharge_break, state='Discharge', t0=t0)
        


        list1 = solved
        # solved_with_column = [row + [I[k]] for row in list1]
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
                            t_end, 1, -I[k], charge_break, state='Charge', t0=t0)
        
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

    # Append the numpy array to the results list for this current
    final_array.append(overall_array_np)

# Now, results_list contains the results for each current value
for k, current_value in enumerate(I):
    print(f'Current Value: {current_value}')
    print(final_array[k])  # Print the results for this current

## Now we save the array above ##
## The results can be obtained in the Test_Saved_Microcycling.py script
np.savez('variable_arrays.npz', solved=overall_array_np, I=I)
print("Solved array returned in the form: [s8_array, s4_array, s2_array, s_array, V_array, sp_array, time_array]")
print("The indexing of the variables follows the list above, Ex: Voltage is index:4 or Precipitated Sulfur is index:5")


def Data_extraction(overall_array_np):

    # Getting data from the dataset and arranging in required format
    excel_array = []
    # for k in range(len(I)):
    for i in range(len(final_array[0][0][0][0])):
        list = []
        for j in range(len(final_array[0][0][0])):
            list.append(final_array[0][0][0][j][i])
        excel_array.append(list)
        # excel_array.append()
    excel_array = np.array(excel_array)
    

    # Ensuring all timesteps are constant
    desired_time_increment = 0.5

    # Calculate the minimum and maximum time values in the array
    min_time = excel_array[:, 6].min()
    max_time = excel_array[:, 6].max()

    # Create a new array with the desired time increments
    new_time_values = np.arange(min_time, max_time + desired_time_increment, desired_time_increment)

    # Initialize arrays to store interpolated values
    interpolated_values = np.zeros((len(new_time_values), 6))

    # Interpolate each column based on time
    for col_index in range(6):
        interpolated_values[:, col_index] = np.interp(new_time_values, excel_array[:, 6], excel_array[:, col_index])
    current_timestep = np.column_stack((interpolated_values, new_time_values))

    next_timestep = []
    # Stacking next timestep side by side with the current timestep
    for i in range(len(current_timestep)-1):
        next_timestep.append(current_timestep[i+1])
    next_timestep = np.array(next_timestep)

    # Removing last timestep in array to match with the next_timestep array
    current_timestep_data = current_timestep[:-1]

    # Forming the overall dataset
    training_data = np.concatenate((current_timestep_data, next_timestep), axis = 1)

    # Converting to pandas dataframe to store as an excel file    
    columns = ['S8_cur','S4_cur','S2_cur','S1_cur','V_cur', 'Sp_cur','t_cur', 'S8_nxt','S4_nxt','S2_nxt','S1_nxt','V_nxt', 'Sp_nxt','t_nxt']
    df = pd.DataFrame(training_data[:, :], columns=columns)
    file_path = 'C:/Users/ADITYA/OneDrive - Imperial College London/Year 4/FYP/Final-year-project/Data numerical 0D/2016_crude_version/dataset_updated.xlsx'
    df.to_excel(file_path, index=True)

    return training_data
        

# Dataset = Data_extraction(overall_array_np)
