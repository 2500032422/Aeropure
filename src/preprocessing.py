import pandas as pd

# Load combined dataset
input_path = "../data/processed/air_quality_combined.csv"

df = pd.read_csv(input_path)

print("Dataset loaded successfully!")
print("Original shape:", df.shape)


# --------------------------------------------------
# 1. Create DateTime column
# --------------------------------------------------

df["datetime"] = pd.to_datetime(
    df[["year", "month", "day", "hour"]]
)

print("\nDateTime column created.")

print(df[["year", "month", "day", "hour", "datetime"]].head())


# --------------------------------------------------
# 2. Check duplicate rows
# --------------------------------------------------

duplicates = df.duplicated().sum()

print("\nNumber of duplicate rows:", duplicates)


# --------------------------------------------------
# 3. Sort data by station and datetime
# --------------------------------------------------

df = df.sort_values(
    by=["station", "datetime"]
)

print("\nData sorted by station and datetime.")


# --------------------------------------------------
# 4. Check missing values
# --------------------------------------------------

print("\nMissing values before handling:")

print(df.isnull().sum())


# --------------------------------------------------
# 5. Handle missing values
# --------------------------------------------------

numeric_columns = df.select_dtypes(
    include="number"
).columns

# Fill missing numeric values using
# interpolation within each station
df[numeric_columns] = (
    df.groupby("station")[numeric_columns]
      .transform(lambda group: group.interpolate(method="linear"))
)


# Fill remaining numeric missing values
# using forward fill and backward fill
df[numeric_columns] = (
    df.groupby("station")[numeric_columns]
      .transform(lambda group: group.ffill().bfill())
)


# Handle missing wind direction
df["wd"] = (
    df.groupby("station")["wd"]
      .transform(lambda group: group.ffill().bfill())
)


# --------------------------------------------------
# 6. Check missing values after handling
# --------------------------------------------------

print("\nMissing values after handling:")

print(df.isnull().sum())


# --------------------------------------------------
# 7. Save cleaned dataset
# --------------------------------------------------

output_path = "../data/processed/air_quality_cleaned.csv"

df.to_csv(
    output_path,
    index=False
)

print("\nCleaned dataset saved successfully!")

print("Saved to:", output_path)

print("Final shape:", df.shape)