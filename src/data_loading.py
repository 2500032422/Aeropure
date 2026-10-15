import pandas as pd

# Path to one station's CSV file
file_path = "../data/raw/PRSA_Data_Aotizhongxin_20130301-20170228.csv"

# Read the CSV file
df = pd.read_csv(file_path)

# Display basic information
print("Dataset loaded successfully!")

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())