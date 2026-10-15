import pandas as pd
import glob
import os

# Location of the raw CSV files
data_path = "../data/raw/"

# Find all CSV files
files = glob.glob(data_path + "PRSA_Data_*.csv")

print("Number of files found:", len(files))

# Store each station's DataFrame
dataframes = []

# Load each CSV file
for file in files:

    print("Loading:", os.path.basename(file))

    df = pd.read_csv(file)

    dataframes.append(df)

# Combine all station datasets
combined_df = pd.concat(
    dataframes,
    ignore_index=True
)

print("\nAll stations combined successfully!")

print("Combined dataset shape:")
print(combined_df.shape)

print("\nStations:")
print(combined_df["station"].unique())

# Save combined dataset
output_path = "../data/processed/air_quality_combined.csv"

combined_df.to_csv(
    output_path,
    index=False
)

print("\nCombined dataset saved to:")
print(output_path)