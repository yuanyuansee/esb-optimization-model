import pandas as pd

# Spring 2023 (2022-23 calendar): Jan 1 - May 25, last day of classes May 25
spring = pd.bdate_range("2023-01-01", "2023-05-25")
spring_off = pd.to_datetime([
    "2023-01-02", "2023-01-03", "2023-01-16",                              # staff dev, MLK
    "2023-02-20",                                                          # staff dev
    "2023-03-13", "2023-03-14", "2023-03-15", "2023-03-16", "2023-03-17",  # spring break
    "2023-04-07", "2023-04-21",                                            # holiday, staff dev
])

# Fall 2023 (2023-24 calendar): first day Aug 15, last day of classes Dec 14
fall = pd.bdate_range("2023-08-15", "2023-12-14")
fall_off = pd.to_datetime([
    "2023-09-04", "2023-09-25",                                            # Labor Day, staff dev
    "2023-10-09",                                                          # staff dev
    "2023-11-10",                                                          # staff dev
    "2023-11-20", "2023-11-21", "2023-11-22", "2023-11-23", "2023-11-24",  # Thanksgiving
])

school_days = spring.difference(spring_off).union(fall.difference(fall_off))
assert len(school_days) == 172, f"expected 172 school days, got {len(school_days)}"

pd.DataFrame({"date": school_days.strftime("%Y-%m-%d")}).to_csv(
    "data/school_days_2023.csv", index=False)
print("saved", len(school_days), "school days")