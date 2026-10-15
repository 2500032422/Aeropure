import pandas as pd
import os

# Load cleaned dataset
file_path = "../data/processed/air_quality_cleaned.csv"
df = pd.read_csv(file_path)

print("Dataset loaded!")
print("Original shape:", df.shape)

# Convert datetime
df["datetime"] = pd.to_datetime(df["datetime"])

# Sort by station and time
df = df.sort_values(["station", "datetime"])

# -----------------------------
# TIME FEATURES
# -----------------------------

df["hour"] = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.dayofweek
df["month"] = df["datetime"].dt.month

# Season
df["season"] = df["month"].map({
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn"
})

# -----------------------------
# LAG FEATURES
# -----------------------------

df["PM2.5_lag_1"] = df.groupby("station")["PM2.5"].shift(1)
df["PM2.5_lag_3"] = df.groupby("station")["PM2.5"].shift(3)
df["PM2.5_lag_6"] = df.groupby("station")["PM2.5"].shift(6)
df["PM2.5_lag_12"] = df.groupby("station")["PM2.5"].shift(12)
df["PM2.5_lag_24"] = df.groupby("station")["PM2.5"].shift(24)
df["PM2.5_lag_168"] = df.groupby("station")["PM2.5"].shift(168)

# -----------------------------
# ROLLING FEATURES
# -----------------------------

df["PM2.5_rolling_3"] = (
    df.groupby("station")["PM2.5"]
    .transform(lambda x: x.shift(1).rolling(3).mean())
)

df["PM2.5_rolling_24"] = (
    df.groupby("station")["PM2.5"]
    .transform(lambda x: x.shift(1).rolling(24).mean())
)

# -----------------------------
# TARGET
# Predict next hour PM2.5
# -----------------------------

df["target_PM2.5"] = (
    df.groupby("station")["PM2.5"].shift(-1)
)

# Remove rows created by lag/target operations
df = df.dropna()

# Save
output_path = "../data/processed/air_quality_features.csv"
df.to_csv(output_path, index=False)

print("\nFeature engineering completed!")
print("Final shape:", df.shape)
print("\nNew columns:")
print([
    "day_of_week",
    "season",
    "PM2.5_lag_1",
    "PM2.5_lag_3",
    "PM2.5_lag_6",
    "PM2.5_lag_12",
    "PM2.5_lag_24",
    "PM2.5_lag_168",
    "PM2.5_rolling_3",
    "PM2.5_rolling_24",
    "target_PM2.5"
])

print("\nSaved to:", output_path)