from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

app = Flask(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "air_quality_cleaned.csv"
)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

# Convert datetime if available
if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

# --------------------------------------------------
# Features and target
# --------------------------------------------------

FEATURES = [
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

TARGET = "PM2.5"

model_df = df[FEATURES + [TARGET]].copy()
model_df = model_df.dropna()

X = model_df[FEATURES]
y = model_df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# --------------------------------------------------
# Train Random Forest model
# --------------------------------------------------

random_forest_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    max_depth=None
)

random_forest_model.fit(X_train, y_train)

rf_predictions = random_forest_model.predict(X_test)

rf_mae = mean_absolute_error(y_test, rf_predictions)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_predictions))
rf_r2 = r2_score(y_test, rf_predictions)

# --------------------------------------------------
# Advanced analysis cache (computed when requested)
# --------------------------------------------------
advanced_analysis_cache = None


def run_advanced_analysis():
    """
    K-Means groups records with similar pollutant/weather profiles.
    PCA projects standardized features to 2 dimensions for visualization.
    10-fold CV evaluates the existing Random Forest regression pipeline.
    Sampling keeps analysis responsive on the full multi-site dataset.
    """
    global advanced_analysis_cache
    if advanced_analysis_cache is not None:
        return advanced_analysis_cache

    analysis_features = [
        "PM2.5", "PM10", "SO2", "NO2", "CO", "O3",
        "TEMP", "PRES", "DEWP", "RAIN", "WSPM", "hour", "month"
    ]
    available = [c for c in analysis_features if c in df.columns]
    work = df[available].replace([np.inf, -np.inf], np.nan).dropna()
    if len(work) > 12000:
        work = work.sample(n=12000, random_state=42)

    # Unsupervised learning: K-Means on standardized air-quality features.
    cluster_columns = [c for c in available if c != "PM2.5"]
    cluster_data = work[cluster_columns].copy()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(cluster_data)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)

    # PCA uses the same standardized feature matrix.
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    points = [
        {"x": round(float(coords[i, 0]), 4),
         "y": round(float(coords[i, 1]), 4),
         "cluster": int(labels[i])}
        for i in range(min(1500, len(coords)))
    ]
    cluster_counts = [
        {"cluster": f"Cluster {i + 1}", "count": int((labels == i).sum())}
        for i in range(4)
    ]

    # Supervised evaluation: 10-fold cross-validation, with preprocessing
    # fitted inside each fold to avoid data leakage.
    cv_features = [c for c in FEATURES if c in df.columns]
    cv_work = df[cv_features + [TARGET]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(cv_work) > 6000:
        cv_work = cv_work.sample(n=6000, random_state=42)
    cv_X, cv_y = cv_work[cv_features], cv_work[TARGET]
    cv_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(
            n_estimators=40, random_state=42, n_jobs=-1, max_depth=18
        ))
    ])
    cv = KFold(n_splits=10, shuffle=True, random_state=42)
    scores = cross_validate(
        cv_pipeline, cv_X, cv_y, cv=cv,
        scoring={"r2": "r2", "mae": "neg_mean_absolute_error",
                 "rmse": "neg_root_mean_squared_error"},
        n_jobs=1, return_train_score=False
    )
    folds = []
    for i in range(10):
        folds.append({
            "fold": i + 1,
            "r2": round(float(scores["test_r2"][i] * 100), 2),
            "mae": round(float(-scores["test_mae"][i]), 3),
            "rmse": round(float(-scores["test_rmse"][i]), 3)
        })

    advanced_analysis_cache = {
        "success": True,
        "clustering": {
            "algorithm": "K-Means",
            "k": 4,
            "sample_size": int(len(work)),
            "features": cluster_columns,
            "counts": cluster_counts,
            "points": points,
            "interpretation": "Clusters group observations with similar standardized pollutant and weather patterns. Cluster IDs are groups, not pollution severity labels."
        },
        "pca": {
            "pc1_variance": round(float(pca.explained_variance_ratio_[0] * 100), 2),
            "pc2_variance": round(float(pca.explained_variance_ratio_[1] * 100), 2),
            "total_variance": round(float(pca.explained_variance_ratio_.sum() * 100), 2),
            "points": points
        },
        "cross_validation": {
            "folds": folds,
            "mean_r2": round(float(scores["test_r2"].mean() * 100), 2),
            "std_r2": round(float(scores["test_r2"].std() * 100), 2),
            "mean_mae": round(float(-scores["test_mae"].mean()), 3),
            "mean_rmse": round(float(-scores["test_rmse"].mean()), 3),
            "sample_size": int(len(cv_work)),
            "fold_count": 10
        }
    }
    return advanced_analysis_cache


# --------------------------------------------------
# Static project results
# --------------------------------------------------

linear_results = {
    "mae": 20.7314,
    "rmse": 31.6597,
    "r2": 84.67
}

random_forest_results = {
    "mae": round(rf_mae, 4),
    "rmse": round(rf_rmse, 4),
    "r2": round(rf_r2 * 100, 2)
}

xgboost_results = {
    "mae": 13.4037,
    "rmse": 21.4716,
    "r2": 92.95
}

# --------------------------------------------------
# Missing values before preprocessing
# --------------------------------------------------

missing_before = {
    "PM2.5": 8739,
    "PM10": 6449,
    "SO2": 9021,
    "NO2": 12116,
    "CO": 20701,
    "O3": 13277,
    "TEMP": 398,
    "PRES": 393,
    "DEWP": 403,
    "RAIN": 390,
    "wd": 1822,
    "WSPM": 318
}

missing_after = {
    column: 0 for column in missing_before
}

# --------------------------------------------------
# Helper function
# --------------------------------------------------

def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    return value


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def index():

    stations = sorted(
        df["station"].dropna().unique().tolist()
    )

    dataset_info = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "stations": len(stations),
        "target": TARGET,
        "date_start": str(df["datetime"].min()) if "datetime" in df.columns else "2013",
        "date_end": str(df["datetime"].max()) if "datetime" in df.columns else "2017"
    }

    return render_template(
        "index.html",
        stations=stations,
        dataset_info=dataset_info,
        missing_before=missing_before,
        missing_after=missing_after,
        linear_results=linear_results,
        random_forest_results=random_forest_results,
        xgboost_results=xgboost_results,
        features=FEATURES
    )


# --------------------------------------------------
# Station-wise dataset API
# --------------------------------------------------

@app.route("/api/station/<station_name>")
def station_data(station_name):

    station_df = df[
        df["station"].astype(str) == str(station_name)
    ].copy()

    if station_df.empty:
        return jsonify({
            "success": False,
            "message": "Station not found"
        }), 404

    # Number of rows to display
    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        limit = 100

    limit = min(max(limit, 1), 1000)

    station_df = station_df.head(limit)

    columns = station_df.columns.tolist()

    rows = [
        {
            column: clean_value(row[column])
            for column in columns
        }
        for _, row in station_df.iterrows()
    ]

    return jsonify({
        "success": True,
        "station": station_name,
        "total_rows": int(
            len(df[df["station"].astype(str) == str(station_name)])
        ),
        "columns": columns,
        "rows": rows
    })


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        input_values = []

        for feature in FEATURES:
            value = float(data.get(feature, 0))
            input_values.append(value)

        input_array = np.array(input_values).reshape(1, -1)

        prediction = random_forest_model.predict(input_array)[0]

        return jsonify({
            "success": True,
            "prediction": round(float(prediction), 2)
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# --------------------------------------------------
# Model information API
# --------------------------------------------------

@app.route("/api/model-info")
def model_info():

    importances = random_forest_model.feature_importances_

    feature_importance = {
        feature: round(float(importance), 6)
        for feature, importance in zip(FEATURES, importances)
    }

    return jsonify({
        "model": "Random Forest Regressor",
        "mae": random_forest_results["mae"],
        "rmse": random_forest_results["rmse"],
        "r2": random_forest_results["r2"],
        "feature_importance": feature_importance
    })




# --------------------------------------------------
# Clustering, PCA and 10-fold CV API
# --------------------------------------------------
@app.route("/api/advanced-analysis")
def advanced_analysis():
    try:
        return jsonify(run_advanced_analysis())
    except Exception as error:
        app.logger.exception("Advanced analysis failed")
        return jsonify({"success": False, "message": str(error)}), 500


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )
