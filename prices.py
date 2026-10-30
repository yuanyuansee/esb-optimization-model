"""Loading ERCOT prices and splitting them into 6 AM-to-6 AM operating days.

Every price source (the 2023 case-study CSVs now, the live ERCOT API later)
produces the same standard table, using ERCOT's column names:

    deliveryDate | hourEnding | settlementPoint | settlementPointPrice | DSTFlag
    2023-01-01   | 1          | LZ_AEN          | -2.11                | False

ERCOT uses "hour ending": hourEnding 7 means 6-7 AM. Prices are in $/MWh.
"""
import pandas as pd

DAY_START_HOUR = 6   # each operating day runs 6 AM to 6 AM


def load_prices(path):
    """Read a standard price CSV and label each hour with its operating day."""
    prices = pd.read_csv(path)
    return add_operating_day(prices)


def add_operating_day(prices):
    """Add two columns:
        start         when each hour begins, e.g. hourEnding 7 on Jan 1 -> 2023-01-01 06:00
        operatingDay  the 6 AM-to-6 AM day the hour belongs to, e.g. "2023-01-01"
    """
    prices = prices.copy()
    prices["start"] = (pd.to_datetime(prices["deliveryDate"])
                       + pd.to_timedelta(prices["hourEnding"] - 1, unit="h"))
    # Shift back by 6 hours so 6 AM counts as the start of a day:
    # 5 AM on Jan 2 becomes 11 PM on Jan 1, so it belongs to Jan 1's operating day.
    shifted = prices["start"] - pd.to_timedelta(DAY_START_HOUR, unit="h")
    prices["operatingDay"] = shifted.dt.strftime("%Y-%m-%d")
    return prices


def operating_day(prices, date):
    """Return one operating day's prices in $/kWh, from 6 AM on `date` to 6 AM the next day."""
    rows = prices[prices["operatingDay"] == date].sort_values("start")
    if len(rows) != 24:
        raise ValueError(f"{date} has {len(rows)} hours of prices, expected 24 "
                         "(the next day's early-morning prices may be missing)")
    return rows["settlementPointPrice"].to_numpy() / 1000


def all_operating_days(prices):
    """List every operating day that has a full 24 hours of prices."""
    counts = prices.groupby("operatingDay").size()
    return list(counts[counts == 24].index)


if __name__ == "__main__":
    rt = load_prices("data/rt_lz_aen_2023.csv")
    da = load_prices("data/da_lz_aen_2023.csv")

    day = operating_day(rt, "2023-01-01")
    print("hours:", len(day))                 # 24
    print("first (Jan 1, 6-7 AM):", day[0])   # 0.0046925
    print("last  (Jan 2, 5-6 AM):", day[-1])  # -0.0053625

    days = all_operating_days(rt)
    print("full days:", len(days), "from", days[0], "to", days[-1])
    print("same days in DA file:", all_operating_days(da) == days)
