import numpy as np
from scipy.optimize import linprog

e_cap = 210
p_cap = 60
soc_min = .10
soc_max = 1
eff = 0.9
miles_per_kwh = 0.71
distance = 66
num_hours = 24

# Returns minimum cost and optimal charge/discharge schedule for a given price profile on an particular day.
def optimize_day(price, on_day, e_cap = e_cap, soc_min = soc_min, soc_max = soc_max, p_cap = p_cap, eff = eff, miles_per_kwh = miles_per_kwh, distance = distance, num_hours = num_hours):
    e_min = e_cap * soc_min
    e_max = e_cap * soc_max
    n = len(price)
    required_energy = distance / miles_per_kwh / eff

    dt = num_hours/n

    # Route times in hours after 6 AM: 6-9 AM and 3-6 PM
    routes = [(0, 3), (9, 12)]
    route_hours = set()
    for start, end in routes:
        route_hours.update(range(round(start / dt), round(end / dt)))

    price = np.array(price) * dt
    negative_price = price * -1
    price_list = np.concatenate((price, negative_price))

    #Objective function: minimize cost = sum(price * charge) + sum(-price * discharge)

   # State of charge must remain between e_min and e_max, inclusive, at all times.
    soc = np.zeros((n, 2*n))
    driven = np.zeros(n)
    for i in route_hours:
        driven[i:] += required_energy / len(route_hours)

    for i in range(n):
        for j in range (i+1):
            soc[i,j] = eff * dt
            soc[i,j+n] = -1/eff * dt

    A_ub = np.vstack([soc, -soc])

    if(on_day):
        b_ub = np.concatenate([driven, (e_max - e_min) - driven])
    else:
        b_ub = np.concatenate([np.full(n, 0), np.full(n, e_max - e_min)])

   #  End the day full: refill everything driven today.
    A_eq = soc[-1:]

    if(on_day):
        b_eq = [required_energy]
    else:
        b_eq = [0]

   # Bounds on charge and discharge power: 0 <= charge, discharge <= p_cap
   # Edge case: for negative price, res will simultaneously charge and discharge. 
   # This makes money due to efficiency losses; however, this is not physically possible.
    bounds = [(0, p_cap)] * n + [(0, p_cap)] * n

    for i in range(n):
        if price[i] < 0:
            bounds[i+n] = (0, 0)  # Disallow discharge when price is negative

    if(on_day): 
        # Does not allow charging/discharging during route hours 
        for h in route_hours:
            bounds[h] = (0, 0)
            bounds[h+n] = (0, 0)
    
    res = linprog(c=price_list, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x[:n], res.x[n:2*n], res.fun



