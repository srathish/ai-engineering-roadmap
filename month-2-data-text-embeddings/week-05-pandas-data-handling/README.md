# Week 5 - Pandas Data Handling

Exploratory data analysis of a small sales dataset using pandas.

## What it does

Loads `sample_data.csv` (27 sales orders) and prints a readable EDA report:

- Shape and column dtypes
- `describe()` summary statistics for numeric columns
- Group-by aggregations (revenue by category, average order revenue by region, sales rep leaderboard)
- Filtering (orders above a revenue threshold)
- Sorting (top orders by revenue)

A derived `revenue` column (`units * unit_price`) is added at load time and used throughout.

## How to run

```bash
pip install -r requirements.txt
python3 analyze_dataset.py
```

## What I learned

- I learned how `pd.read_csv` with `parse_dates` turns a text date column into real datetimes I can work with, instead of plain strings.
- I learned that `df.shape`, `df.dtypes`, and `df.describe()` are the fastest way to get a feel for a dataset before doing anything else.
- I learned that `groupby(...).agg(...)` lets me compute several metrics at once (sum, count, mean) and name the output columns clearly.
- I learned that boolean masks like `df[df["revenue"] > 1000]` make filtering feel natural once I stopped thinking of it as a loop.
- I learned that `sort_values` plus `head()` is an easy pattern for "top N" questions, and that chaining these operations keeps the code short and readable.
- I learned it's often cleaner to derive a column once (revenue) and reuse it everywhere than to recompute the same math in each step.
