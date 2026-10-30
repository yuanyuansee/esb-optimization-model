"""One-time script: convert the 2023 case-study spreadsheets into standard CSVs.

Run from the repo root:
    python scripts/convert_spreadsheets.py
"""
import pandas as pd


def load_excel_prices(path, settlement_point="LZ_AEN"):
    # Read all 12 month sheets and stack them into one table
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    df = pd.concat(sheets.values(), ignore_index=True)
    df.columns = ["date", "hour", "flag", "price"]

    # Build the standard table, using ERCOT's column names
    out = pd.DataFrame({
        "deliveryDate": pd.to_datetime(df["date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d"),
        "hourEnding": df["hour"].astype(str).str[:2].astype(int),
        "settlementPoint": settlement_point,
        "settlementPointPrice": df["price"].astype(float),
        # Every day in these files was already adjusted to 24 hours by hand,
        # so no row is a repeated daylight-saving hour.
        "DSTFlag": False,
    })
    return out.sort_values(["deliveryDate", "hourEnding"]).reset_index(drop=True)


def check(df, name):
    hours_per_day = df.groupby("deliveryDate").size()
    assert len(df) == 8760, f"{name}: expected 8760 rows, got {len(df)}"
    assert (hours_per_day == 24).all(), f"{name}: some days don't have 24 hours"
    assert df["settlementPointPrice"].notna().all(), f"{name}: missing prices"
    print(f"{name}: {len(df)} rows, {len(hours_per_day)} days, "
          f"prices {df['settlementPointPrice'].min():.2f} to {df['settlementPointPrice'].max():.2f} $/MWh")


if __name__ == "__main__":
    files = {
        "data/da_lz_aen_2023.csv": "DA_Price_AEN_Hourly_daylightsaving2023.xlsx",
        "data/rt_lz_aen_2023.csv": "Price_AEN_Hourly_daylightsaving2023.xlsx",
    }
    for out_path, xlsx in files.items():
        df = load_excel_prices(xlsx)
        check(df, out_path)
        df.to_csv(out_path, index=False)
