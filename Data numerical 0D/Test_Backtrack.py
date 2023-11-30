from LiS_Backtrack_Solver import LiS_Solver
import numpy as np
import matplotlib.pyplot as plt

h_try = [1, 0.5, 0.05, 0.005] # Step sizes to try
tries = 0 # Number of tries executed

while tries < len(h_try):
    print("===========================================================")
    try:
        ## Now we call the solver and solve ##
        t_end = 5000 # End time
        h0 = h_try[tries] # Initial step size
        
        ## Initialize the variable values and arrays
        s8_cath = 2.6892000000000003
        s4_cath = 0.0027
        s2_cath = 0.002697299116926997
        s1_cath = 8.83072852310722e-10
        sp_cath = 2.7e-06
        V = 2.430277479547109
        I = 1.7
        x_var = [s8_cath, s4_cath, s2_cath, s1_cath, sp_cath, V]
        
        param_EL0 = 2.19
        break_voltage = param_EL0-0.05 # Voltage point where simulation is stopped to prevent Singular Matrix Error
        
        upd_param = {}
        #params_backtracked = {"EL0": 1.94*1.005}
        params_backtracked = {}
        ## Run the solver and save results within npz file
        solved = LiS_Solver(x_var, t_end, h0, I, break_voltage, state='Discharge', 
                            params_backtrack=params_backtracked, upd_params=upd_param)

        V = solved[-2]
        t = solved[-1]
        
        
        ## Turn all arrays to numpy arrays
        V = np.array(V)

        # Now we plot:
        t = np.array(t)
        Ah = (t/3600)*I
        plt.plot(Ah,V)
        plt.title(f"Cell Output Voltage vs Discharge Capacity {round(I,4)}A")
        plt.ylabel("Potential (V)")
        plt.xlabel("Discharge Capacity (Ah)")
        #plt.xlim([-0.0002, 0.18])
        min_y = break_voltage - 0.05
        #plt.ylim([min_y, 2.45])
        plt.savefig('Voltage_Output_40C.png', dpi=1200)
        plt.show()
        
        print(f"Successful Run step size: {h_try[tries]}")
        print("===========================================================")
        break
        
    except Exception as e:
        if tries >= len(h_try) - 1:
            print("No Successful Runs, Simulation Terminated!")
            print("===========================================================")
            raise
            break
        print(f"Error occurred: {e}")
        print(f"Changing step size from {h_try[tries]} to {h_try[tries+1]}")
        print("===========================================================")
        print("\n")
        tries += 1