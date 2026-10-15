import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


# ============================================================
# 1. LOAD CLEANED DATA
# ============================================================

input_path = "../data/processed/air_quality_cleaned.csv"

df = pd.read_csv(input_path)

# Convert datetime back to datetime format
df["datetime"] = pd.to_datetime(df["datetime"])

print("Cleaned dataset loaded successfully!")

print("\nDataset shape:")
print(df.shape)

print("\nBasic statistics:")
print(df.describe())


# Create output folder if it doesn't exist
output_dir = "../outputs/plots"

os.makedirs(output_dir, exist_ok=True)


# ============================================================
# 2. PM2.5 DISTRIBUTION
# ============================================================

plt.figure(figsize=(10, 6))

sns.histplot(
    df["PM2.5"],
    bins=50,
    kde=True
)

plt.title("Distribution of PM2.5")
plt.xlabel("PM2.5")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_distribution.png"
)

plt.show()


# ============================================================
# 3. PM2.5 OVER TIME
# ============================================================

# Calculate daily average PM2.5
daily_pm25 = (
    df.set_index("datetime")
      .groupby("station")["PM2.5"]
      .resample("D")
      .mean()
      .reset_index()
)

plt.figure(figsize=(14, 6))

# Plot one station as an example
station_name = "Aotizhongxin"

station_data = daily_pm25[
    daily_pm25["station"] == station_name
]

plt.plot(
    station_data["datetime"],
    station_data["PM2.5"]
)

plt.title(
    f"Daily Average PM2.5 - {station_name}"
)

plt.xlabel("Date")
plt.ylabel("PM2.5")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_daily_trend.png"
)

plt.show()


# ============================================================
# 4. PM2.5 BY HOUR
# ============================================================

hourly_pm25 = (
    df.groupby("hour")["PM2.5"]
      .mean()
)

plt.figure(figsize=(10, 6))

plt.plot(
    hourly_pm25.index,
    hourly_pm25.values,
    marker="o"
)

plt.title("Average PM2.5 by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Average PM2.5")

plt.xticks(range(24))

plt.grid(True)

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_by_hour.png"
)

plt.show()


# ============================================================
# 5. PM2.5 BY MONTH
# ============================================================

monthly_pm25 = (
    df.groupby("month")["PM2.5"]
      .mean()
)

plt.figure(figsize=(10, 6))

plt.plot(
    monthly_pm25.index,
    monthly_pm25.values,
    marker="o"
)

plt.title("Average PM2.5 by Month")

plt.xlabel("Month")
plt.ylabel("Average PM2.5")

plt.xticks(range(1, 13))

plt.grid(True)

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_by_month.png"
)

plt.show()


# ============================================================
# 6. PM2.5 BY STATION
# ============================================================

station_pm25 = (
    df.groupby("station")["PM2.5"]
      .mean()
      .sort_values(ascending=False)
)

plt.figure(figsize=(12, 6))

station_pm25.plot(
    kind="bar"
)

plt.title("Average PM2.5 by Monitoring Station")

plt.xlabel("Station")

plt.ylabel("Average PM2.5")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_by_station.png"
)

plt.show()


# ============================================================
# 7. CORRELATION HEATMAP
# ============================================================

numeric_columns = [
    "PM2.5",
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3",
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "WSPM"
]

correlation = df[numeric_columns].corr()

plt.figure(figsize=(12, 8))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)

plt.title("Correlation Matrix")

plt.tight_layout()

plt.savefig(
    f"{output_dir}/correlation_heatmap.png"
)

plt.show()


# ============================================================
# 8. PM2.5 VS PM10
# ============================================================

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df.sample(10000),
    x="PM10",
    y="PM2.5",
    alpha=0.4
)

plt.title("PM2.5 vs PM10")

plt.xlabel("PM10")

plt.ylabel("PM2.5")

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_vs_pm10.png"
)

plt.show()


# ============================================================
# 9. PM2.5 VS TEMPERATURE
# ============================================================

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df.sample(10000),
    x="TEMP",
    y="PM2.5",
    alpha=0.4
)

plt.title("PM2.5 vs Temperature")

plt.xlabel("Temperature")

plt.ylabel("PM2.5")

plt.tight_layout()

plt.savefig(
    f"{output_dir}/pm25_vs_temperature.png"
)

plt.show()


# ============================================================
# 10. EDA COMPLETE
# ============================================================

print("\nEDA completed successfully!")

print("\nPlots saved in:")
print(output_dir)