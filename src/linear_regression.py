import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# 1. LOAD CLEANED DATA
# --------------------------------------------------

file_path = "../data/processed/air_quality_cleaned.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 2. SELECT FEATURES AND TARGET
# --------------------------------------------------

features = [
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3",
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "WSPM",
    "hour",
    "month"
]

target = "PM2.5"

X = df[features]
y = df[target]


print("\nFeatures:")
print(features)

print("\nTarget:")
print(target)


# --------------------------------------------------
# 3. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining data:", X_train.shape)
print("Testing data:", X_test.shape)


# --------------------------------------------------
# 4. NORMALIZATION
# --------------------------------------------------

minmax_scaler = MinMaxScaler()

X_train_normalized = minmax_scaler.fit_transform(X_train)
X_test_normalized = minmax_scaler.transform(X_test)


# --------------------------------------------------
# 5. LINEAR REGRESSION WITH NORMALIZATION
# --------------------------------------------------

model_normalized = LinearRegression()

model_normalized.fit(
    X_train_normalized,
    y_train
)

y_pred_normalized = model_normalized.predict(
    X_test_normalized
)


# --------------------------------------------------
# 6. EVALUATION - NORMALIZATION
# --------------------------------------------------

mae_normalized = mean_absolute_error(
    y_test,
    y_pred_normalized
)

rmse_normalized = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred_normalized
    )
)

r2_normalized = r2_score(
    y_test,
    y_pred_normalized
)


print("\n========== NORMALIZATION + LINEAR REGRESSION ==========")

print("MAE :", mae_normalized)
print("RMSE:", rmse_normalized)
print("R2  :", r2_normalized)


# --------------------------------------------------
# 7. STANDARDIZATION
# --------------------------------------------------

standard_scaler = StandardScaler()

X_train_standardized = standard_scaler.fit_transform(
    X_train
)

X_test_standardized = standard_scaler.transform(
    X_test
)


# --------------------------------------------------
# 8. LINEAR REGRESSION WITH STANDARDIZATION
# --------------------------------------------------

model_standardized = LinearRegression()

model_standardized.fit(
    X_train_standardized,
    y_train
)

y_pred_standardized = model_standardized.predict(
    X_test_standardized
)


# --------------------------------------------------
# 9. EVALUATION - STANDARDIZATION
# --------------------------------------------------

mae_standardized = mean_absolute_error(
    y_test,
    y_pred_standardized
)

rmse_standardized = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred_standardized
    )
)

r2_standardized = r2_score(
    y_test,
    y_pred_standardized
)


print("\n========== STANDARDIZATION + LINEAR REGRESSION ==========")

print("MAE :", mae_standardized)
print("RMSE:", rmse_standardized)
print("R2  :", r2_standardized)


# --------------------------------------------------
# 10. COMPARISON
# --------------------------------------------------

print("\n========== MODEL COMPARISON ==========")

print("\nNormalization:")
print("MAE :", mae_normalized)
print("RMSE:", rmse_normalized)
print("R2  :", r2_normalized)

print("\nStandardization:")
print("MAE :", mae_standardized)
print("RMSE:", rmse_standardized)
print("R2  :", r2_standardized)


# --------------------------------------------------
# 11. ACTUAL VS PREDICTED GRAPH
# --------------------------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    y_pred_standardized,
    alpha=0.3
)

plt.xlabel("Actual PM2.5")
plt.ylabel("Predicted PM2.5")
plt.title("Actual vs Predicted PM2.5")

plt.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "../outputs/plots/actual_vs_predicted.png"
)

plt.show()


# --------------------------------------------------
# 12. FEATURE IMPORTANCE USING COEFFICIENTS
# --------------------------------------------------

coefficients = pd.DataFrame({
    "Feature": features,
    "Coefficient": model_standardized.coef_
})

coefficients = coefficients.sort_values(
    by="Coefficient",
    ascending=False
)

print("\n========== FEATURE COEFFICIENTS ==========")

print(coefficients)


# --------------------------------------------------
# 13. COEFFICIENT GRAPH
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    coefficients["Feature"],
    coefficients["Coefficient"]
)

plt.xticks(
    rotation=45
)

plt.xlabel("Features")
plt.ylabel("Regression Coefficient")

plt.title(
    "Feature Coefficients - Linear Regression"
)

plt.tight_layout()

plt.savefig(
    "../outputs/plots/feature_coefficients.png"
)

plt.show()