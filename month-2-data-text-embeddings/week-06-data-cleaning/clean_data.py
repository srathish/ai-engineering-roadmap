"""Clean a deliberately messy customer CSV with pandas.

The raw file has missing values, duplicate rows, inconsistent text casing and
stray whitespace, and a numeric column ("monthly_spend") stored as strings
with dollar signs. This script cleans all of that, engineers a couple of new
columns, and writes the result to cleaned_data.csv.

Run with:  python3 clean_data.py
"""

import os
import pandas as pd

HERE = os.path.dirname(__file__)
RAW_FILE = os.path.join(HERE, "messy_data.csv")
OUT_FILE = os.path.join(HERE, "cleaned_data.csv")


def summarize(df, label):
    """Print a compact snapshot of the dataframe's state."""
    print(f"\n--- {label} ---")
    print(f"shape: {df.shape}")
    print(f"duplicate rows: {df.duplicated().sum()}")
    print("missing values per column:")
    print(df.isna().sum())


def clean(df):
    """Apply all cleaning steps and return a new dataframe."""

    # 1. Standardize text: strip whitespace and fix casing.
    #    Names -> Title Case, cities -> Title Case, plan -> lowercase.
    df["name"] = df["name"].str.strip().str.title()
    df["city"] = df["city"].str.strip().str.title()
    df["plan"] = df["plan"].str.strip().str.lower()

    # 2. Fix the numeric column stored as strings: drop "$" and cast to float.
    df["monthly_spend"] = (
        df["monthly_spend"].astype(str).str.replace("$", "", regex=False).astype(float)
    )

    # 3. Remove exact duplicate rows. They are real duplicates (same customer_id
    #    and same details), so dropping them avoids double-counting.
    df = df.drop_duplicates()

    # 4. Handle missing values with reasoning:
    #    - age: numeric, so fill with the median (robust to outliers) and cast to int.
    #    - signup_date: a date we cannot guess, so drop rows where it is missing.
    df["age"] = df["age"].fillna(df["age"].median())
    df = df.dropna(subset=["signup_date"])
    df["age"] = df["age"].astype(int)

    # 5. Fix dtypes: parse signup_date as a real datetime.
    df["signup_date"] = pd.to_datetime(df["signup_date"])

    # 6. Feature engineering:
    #    - annual_spend: a simple derived metric (monthly * 12).
    #    - age_group: bucket customers for easy segmentation.
    df["annual_spend"] = (df["monthly_spend"] * 12).round(2)
    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 30, 45, 200],
        labels=["under_30", "30_to_45", "over_45"],
    )

    return df.reset_index(drop=True)


def main():
    raw = pd.read_csv(RAW_FILE)
    summarize(raw, "BEFORE")
    print("\nraw dtypes:")
    print(raw.dtypes)

    cleaned = clean(raw.copy())
    summarize(cleaned, "AFTER")
    print("\ncleaned dtypes:")
    print(cleaned.dtypes)

    print("\ncleaned preview:")
    print(cleaned.head())

    cleaned.to_csv(OUT_FILE, index=False)
    print(f"\nSaved cleaned data -> {OUT_FILE}")


if __name__ == "__main__":
    main()
