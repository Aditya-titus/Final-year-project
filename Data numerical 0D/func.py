from sympy import symbols, diff, exp, sqrt, lambdify
from sympy import *

# =============================================================================
# Helper Functions Below:
# =============================================================================
## Derivative function:
def var_func_der(var_list, u, sym):
    # Returns a list of all the derivative
    # List is lambdified w.r.t to the symbols defined (sym)
    der_list = []
    for i in range(len(var_list)):
        der = diff(u, var_list[i])
        der = lambdify(sym, der, 'numpy')
        der_list.append(der)
        
    # Return the lambdified derivative list
    return der_list

## Function to lambdify u array
def u_func_lambdify(u_list, sym):
    for i in range(len(u_list)):
        u_list[i] = lambdify(sym, u_list[i], 'numpy')
        
    return u_list

## Function to return Voltage variable index:
def find_index_with_v(input_list):
    for idx, item in enumerate(input_list):
        if "V" in item:
            return idx
    return -1

# =============================================================================
#               This is the new 2023 3-Stage Model Formulation
# =============================================================================

## Define all parameters as symbols
F = symbols('F') 
Ms = symbols('Ms')    # Molar mass
nH = symbols('nH')
nL = symbols('nL')
ns8 = symbols('ns8')
R = symbols('R')
ps = symbols('ps') # rho_s
a = symbols('a')
v = symbols('v')
EH0 = symbols('EH0')
EL0= symbols('EL0')
jH0 = symbols('jH0')
jL0 = symbols('jL0')
kp = symbols('kp')
ks = symbols('ks')
T = symbols('T')
s_sat = symbols('s_sat') 

# Define variable symbols

## Cathode Variables
s8_cath = symbols('s8_cath')
s4_cath = symbols('s4_cath')
s2_cath = symbols('s2_cath')
s1_cath = symbols('s1_cath')
sp_cath = symbols('sp_cath')

## Voltage
V = symbols('V')

## Prev_vars
s8_cath_prev = symbols('s8_cath_prev')
s4_cath_prev = symbols('s4_cath_prev')
s2_cath_prev = symbols('s2_cath_prev')
s1_cath_prev = symbols('s1_cath_prev')
sp_cath_prev = symbols('sp_cath_prev')
V_prev = symbols('V_prev')


## h and I
h = symbols('h')  # timestep value
I = symbols('I')  # current

# =============================================================================
# *** NOTE: DO NOT CHANGE THE LIST NAMES AND V_INDEX NAME BELOW AS THEY ARE 
# REFERENCED IN THE SOLVER CLASS AND SOLVER FUNCTION SCRIPT ***
# =============================================================================
## Define lists to pass variable
var_list = [s8_cath, s4_cath, s2_cath, s1_cath, sp_cath, V]
prev_var = [s8_cath_prev, s4_cath_prev, s2_cath_prev, s1_cath_prev, sp_cath_prev, V_prev]
## Both these list (var_list and prev_var) must have the same order
h_I = [h, I]
param_list = [F, Ms, nH, nL, ns8, R, ps, a, v, EH0, EL0,jH0, jL0, kp, ks, T, s_sat]
sym = tuple(var_list + prev_var + h_I + param_list)

## Here we check the index of the Voltage variable
V_index = find_index_with_v([str(item) for item in var_list])

# =============================================================================
# ## Now we define the dependant equations before the ODEs
# =============================================================================

fh = 2*Ms*v
fl = ((Ms**2)*(v**2))/2

EH = EH0 + (((R*T)/4*F)*log((fh*s8_cath)/(s4_cath**2)))
EL = EL0 + (((R*T)/4*F)*log((fl*s4_cath)/((s1_cath**2)*s2_cath)))

etaH = V - EH
etaL = V - EL

iH = (-2*jH0*a)*(sinh((2*F*etaH)/(R*T)))   # Need to find values for iH0 and iL0 
iL = (-2*jL0*a)*(sinh((2*F*etaL)/(R*T)))

## Now we define the Backward Euler Equations:

# =============================================================================
# u2 is the discretised function for s8_cath (time-dependent) and Jacobian Elements
# =============================================================================
k_s8_cath = -1*((iH*2*Ms)/F) - (ks*s8_cath)

u2 = h*k_s8_cath - s8_cath + s8_cath_prev

u2_ders = var_func_der(var_list, u2, sym)

# =============================================================================
# u3 is the discretised function for s4_cath (time-dependent) and Jacobian Elements  
# =============================================================================
k_s4_cath = ((iH*2*Ms)/F) + (ks*s8_cath) - ((Ms*iL)/F)

u3 = h*k_s4_cath - s4_cath + s4_cath_prev

u3_ders = var_func_der(var_list, u3, sym)

# =============================================================================
# u4 is the discretised function for s2_cath (time-dependent) and Jacobian Elements  
# =============================================================================
k_s2_cath = ((Ms*iL)/(2*F))

u4 = h*k_s2_cath - s2_cath + s2_cath_prev

u4_ders = var_func_der(var_list, u4, sym)

# =============================================================================
# u5 is the discretised function for s1_cath (time-dependent) and Jacobian Elements    
# =============================================================================
k_s1_cath = ((Ms*iL)/(2*F)) - ((kp*sp_cath*(s1_cath - s_sat))/(v*ps))

u5 = h*k_s1_cath - s1_cath + s1_cath_prev

u5_ders = var_func_der(var_list, u5, sym)

# =============================================================================
# u6 is the discretised function for sp_cath (time-dependent) and Jacobian Elements   
# =============================================================================
k_sp_cath = ((kp*sp_cath*(s1_cath - s_sat))/(v*ps))

u6 = h*k_sp_cath - sp_cath + sp_cath_prev

u6_ders = var_func_der(var_list, u6, sym)

# =============================================================================
# u12 is the discretised function for V (non-time-dependent) and Jacobian Elements
# =============================================================================
# This is the Algebraic Constraint
u12 = I - iH - iL

u12_ders = var_func_der(var_list, u12, sym)

# =============================================================================
# ## Update the u_list and jacob_list with the u values and differentials ##
# ## DO NOT CHANGE THE NAMES OF THE LIST i.e. u_list and jacob_list ##
# =============================================================================

u_list = [u2, u3, u4, u5, u6, u12] # Un-lambdified list
u_list = u_func_lambdify(u_list, sym) # Lamdify the u_list
jacob_list = [u2_ders, u3_ders, u4_ders, u5_ders, 
              u6_ders, u12_ders]