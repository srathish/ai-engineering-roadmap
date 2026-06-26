"""Exploratory data analysis of a small sales dataset using pandas.

Loads a CSV, then walks through the common EDA steps: inspecting shape and
dtypes, summary statistics, group-by aggregation, filtering, and sorting.
Run with:  python3 analyze_dataset.py
"""

import os
import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), "sample_data.csv")


def load_data(path):
    """Load the CSV and parse the date column as real datetimes."""
    df = pd.read_csv(path, parse_dates=["date"])
    # Derive total revenue per order; handy for every aggregation below.
    df["revenue"] = df["units"] * df["unit_price"]
    return df


def section(title):
    """Print a simple section header so the report is easy to scan."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    df = load_data(DATA_FILE)

    section("SHAPE")
    rows, cols = df.shape
    print(f"{rows} rows x {cols} columns")

    section("COLUMN DTYPES")
    print(df.dtypes)

    section("FIRST 5 ROWS")
    print(df.head())

    section("DESCRIBE (numeric columns)")
    print(df.describe())

    section("GROUPBY: revenue by category")
    by_category = (
        df.groupby("category")
        .agg(total_revenue=("revenue", "sum"),
             total_units=("units", "sum"),
             orders=("order_id", "count"))
        .sort_values("total_revenue", ascending=False)
    )
    print(by_category)

    section("GROUPBY: average order revenue by region")
    by_region = df.groupby("region")["revenue"].mean().round(2)
    print(by_region)

    section("FILTER: orders with revenue over 1000")
    big_orders = df[df["revenue"] > 1000]
    print(f"{len(big_orders)} orders above 1000")
    print(big_orders[["order_id", "product", "region", "revenue"]])

    section("SORT: top 5 orders by revenue")
    top5 = df.sort_values("revenue", ascending=False).head(5)
    print(top5[["order_id", "product", "category", "revenue"]])

    section("SALES REP LEADERBOARD")
    rep_totals = (
        df.groupby("sales_rep")["revenue"].sum().round(2).sort_values(ascending=False)
    )
    print(rep_totals)

    section("REPORT COMPLETE")


if __name__ == "__main__":
    main()
