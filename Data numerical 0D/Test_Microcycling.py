import numpy as np
from LiS_Backtrack_Solver import LiS_Solver, LiS_Solver2
import timeit

## Now we call the solver and solve ##
span = 11000 
t0 = 0
t_end = span # End time
h0_try = [1, 0.5, 0.05, 0.005] # Initial step size for discharge
h01_try = [1.5, 0.5, 0.05, 0.005] # Initial step size for charge

## Initialize the variable values and arrays for microcycling
## Start with Discharge 1st
Li_cath = 23.618929391226814
s8_cath = 19.672721954609568
s4_cath = 0.011563045206703666*1000
s2_cath = 0.0001
s1_cath = 4.886310174346254e-10
sp_cath = 0.008672459420571042
V = 2.5279911819843837
I = 1.6*0.211*0.2

x_var = [Li_cath, s8_cath, s4_cath, s2_cath, s1_cath, sp_cath, V] # ensure list follows same as func.py
# Voltage point where simulation is stopped to prevent Singular Matrix Error
discharge_break = 1.9
charge_break = 2.5

cycles = 1 ## Number of cycles to run (1 cycle is Discharge followed by Charge)
overall_array = []
for j in range(cycles):
    overall_array.append([])

param_EL0 = 1.94
## Define backtracking parameter values
params_backtracked = {"EL0": param_EL0*1.005}
## Define different parameter values discharging
discharge_update = {"EL0": param_EL0}
## Define different parameter values charging
charge_upd = {}

## Define  solver for microcycling:
start = timeit.default_timer() ## Start timer
for i in range(cycles):
    tries = 0
    while tries < len(h0_try):
        # Discharge
        try:
            h0 = h0_try[tries]
            solved = LiS_Solver(x_var, 
                                t_end, h0, I, discharge_break, state='Discharge', t0=t0, 
                                params_backtrack = params_backtracked, upd_params = discharge_update)
            
            print(f'Cycle {i+1} Discharge Solved')
            break
        
        except Exception as e:
            print(e)
            if tries >= len(h0_try) - 1:
                raise
                break
            tries += 1
    
    list1 = solved
    overall_array[i].append(list1)
    s8_cath = solved[0][-1]
    s4_cath = solved[1][-1]
    s2_cath = solved[2][-1]
    s1_cath = solved[3][-1]
    sp_cath = solved[4][-1]
    V = solved[15][-1]
    x_var = [s8_cath, s4_cath, s2_cath, s1_cath, sp_cath,V]
    t0 = solved[6][-1]
    t_end = t0 + span
    
    tries = 0
    while tries < len(h01_try):
        # Discharge
        try:
            # Charge
            h01 = h01_try[tries]
            solved2 = LiS_Solver2(x_var, 
                                t_end, h01, -I, charge_break, state='Charge', t0=t0, 
                                upd_params = charge_upd)
            
            print(f'Cycle {i+1} Charge Solved')
            break
        
        except Exception as e:
            print(e)
            if tries >= len(h01_try) - 1:
                raise
                break
            tries += 1
    
    list2 = solved2
    overall_array[i].append(list2)
    s8_cath = solved2[0][-1]
    s4_cath = solved2[1][-1]
    s2_cath = solved2[2][-1]
    s1_cath = solved2[3][-1]
    sp_cath = solved2[4][-1]
    V = solved2[5][-1]
    x_var = [Li_cath, s8_cath, s4_cath, s2_cath, s1_cath, sp_cath, V]
    #print(x_var)
    t0 = solved2[6][-1]
    t_end = t0 + span
    # Update charge break 
    charge_break = min(charge_break, max(solved2[11]))
    
    print(f'No. Cycles: {i+1}/{cycles}')
    
overall_array_np = np.empty(len(overall_array), dtype=object)
overall_array_np[:] = overall_array

print("The time taken for completion :", (timeit.default_timer() - start), "s")
np.savez('variable_arrays.npz', solved=overall_array_np, I=I)