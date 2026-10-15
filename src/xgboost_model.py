import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

file_path = "../data/processed/air_quality_cleaned.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 2. FEATURES AND TARGET
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
# 4. XGBOOST MODEL
# --------------------------------------------------

model = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

print("\nTraining XGBoost...")

model.fit(X_train, y_train)

print("XGBoost training completed!")


# --------------------------------------------------
# 5. PREDICTION
# --------------------------------------------------

y_pred = model.predict(X_test)


# --------------------------------------------------
# 6. EVALUATION
# --------------------------------------------------

mae = mean_absolute_error(y_test, y_pred)

rmse = np.sqrt(
    mean_squared_error(y_test, y_pred)
)

r2 = r2_score(y_test, y_pred)


print("\n========== XGBOOST RESULTS ==========")

print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)


# --------------------------------------------------
# 7. FEATURE IMPORTANCE
# --------------------------------------------------

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\n========== FEATURE IMPORTANCE ==========")

print(importance)


# --------------------------------------------------
# 8. FEATURE IMPORTANCE GRAPH
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    importance["Feature"],
    importance["Importance"]
)

plt.xticks(rotation=45)

plt.xlabel("Features")
plt.ylabel("Importance")

plt.title("XGBoost Feature Importance")

plt.tight_layout()

plt.savefig(
    "../outputs/plots/xgboost_feature_importance.png"
)

plt.show()


# --------------------------------------------------
# 9. ACTUAL VS PREDICTED
# --------------------------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    y_pred,
    alpha=0.3
)

plt.xlabel("Actual PM2.5")
plt.ylabel("Predicted PM2.5")

plt.title("XGBoost - Actual vs Predicted PM2.5")

plt.plot(
    [y_test.min(), y_test.max()],
    [y_test.min(), y_test.max()],
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "../outputs/plots/xgboost_actual_vs_predicted.png"
)

plt.show()