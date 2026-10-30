from prices import load_prices, operating_day, all_operating_days
from school_calendar import load_school_days
from optimize import optimize_day

rt = load_prices("data/rt_lz_aen_2023.csv")
school_days = load_school_days()

yearly_cost = 0
for date in all_operating_days(rt): 
    price = operating_day(rt, date)
    on_day = date in school_days
    charge, discharge, cost = optimize_day(price, on_day=on_day)
    yearly_cost += cost
print(yearly_cost)