import pandas as pd

def load_school_days(path="data/school_days_2023.csv"):
    """Return the set of school-day dates, as strings like "2023-01-04"."""
    return set(pd.read_csv(path)["date"])