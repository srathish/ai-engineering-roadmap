# Week 6 - Data Cleaning

Takes a deliberately messy customer CSV and produces a clean, analysis-ready dataset.

## What it does

Loads `messy_data.csv` and cleans it step by step, printing a before/after summary:

- **Text standardization** - strips whitespace, Title-cases names and cities, lowercases the `plan` column
- **Type fixing** - converts `monthly_spend` from strings like `$49.99` to floats, and parses `signup_date` into real datetimes
- **Duplicates** - drops exact duplicate rows so customers are not double-counted
- **Missing values** - fills missing `age` with the median (then casts to int) and drops rows missing `signup_date` (a value that cannot be guessed)
- **Feature engineering** - derives `annual_spend` (monthly x 12) and an `age_group` bucket

The result is written to `cleaned_data.csv`.

## How to run

```bash
pip install -r requirements.txt
python3 clean_data.py
```

## What I learned

- I learned that real-world data is rarely tidy, and that the same value (like a plan name) can show up as `PREMIUM`, `Premium`, and `premium` unless I normalize casing.
- I learned the difference between `fillna` and `dropna`, and that the right choice depends on the column: I can impute a missing age with the median, but I shouldn't invent a signup date.
- I learned that a number stored as a string (`$49.99`) silently breaks math, and that I have to strip the symbol and cast to float before aggregating.
- I learned that `drop_duplicates` matters because duplicate rows quietly inflate counts and totals downstream.
- I learned that feature engineering, like bucketing age with `pd.cut`, turns raw values into something more useful for segmentation.
- I learned why clean data matters: every analysis I do later is only as trustworthy as the cleaning step in front of it.
