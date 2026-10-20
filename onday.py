import numpy as np
from scipy.optimize import linprog
# numpy is a library for numerical computations; thus, all calls to numpy functions require np. prefix.
# scipy is a library for scientific computations; optimize is a module of scipy; linprog is a function of optimize

# price: list of $/kWh, one per hour. Returns (charge, discharge, cost).

e_cap = 210
p_cap = 60
soc_min = .10
soc_max = 1
eff = 0.9

def optimize_off_day(price, e_cap, soc_min, soc_max, p_cap, eff):
    e_min = e_cap * soc_min
    e_max = e_cap * soc_max
    n = len(price)
    #assumption: 24 hour days
    dt = 24/n 

    price = np.array(price) * dt
    negative_price = price * -1
    price_list = np.concatenate((price, negative_price))

    #Objective function: minimize cost = sum(price * charge) + sum(-price * discharge)

   # State of charge must remain between e_min and e_max, inclusive, at all times. 
    soc = np.zeros((n, 2*n))
    for i in range(n):
        for j in range (i+1):
            soc[i,j] = eff * dt
            soc[i,j+n] = -1/eff * dt

    A_ub = np.vstack([soc, -soc])
    b_ub = np.concatenate([np.full(n, 0), np.full(n, e_max - e_min)])
   # The state of charge at the end of the day must equal e_start.
    A_eq = soc[-1:]
    b_eq = [0]

   # Bounds on charge and discharge power: 0 <= charge, discharge <= p_cap
   # Edge case: for negative price, res will simaltaneously charge and discharge. 
   # This makes money due to efficiency losses; however, this is not physically possible.
    bounds = [(0, p_cap)] * n + [(0, p_cap)] * n
    for i in range(n):
        if price[i] < 0:
            bounds[i+n] = (0, 0)  # Disallow discharge when price is negative
    res = linprog(c=price_list, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x[:n], res.x[n:2*n], res.fun



