# AirNova — updated ML analysis

## Added
- K-Means clustering (K=4) on standardized pollutant/weather features.
- PCA visualization of the first two principal components.
- 10-fold cross-validation for Random Forest regression, reporting R², MAE and RMSE for each fold and the mean.
- A new **Clustering, PCA & CV** page in the Flask dashboard.

## Run
1. Open this folder in PyCharm or a terminal.
2. Create/activate your project virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run:
   `python main.py`
5. Open `http://127.0.0.1:5000` and choose **Clustering, PCA & CV** in the sidebar.

The advanced-analysis endpoint computes on demand and caches its result for the current server process. To refresh the display, click **Run / Refresh Analysis**; to recompute from scratch, restart the Flask app.

## Method notes
- K-Means uses K=4 as a practical exploratory choice. Cluster IDs are arbitrary and are not automatically pollution severity categories.
- PCA uses standardized numeric features and displays up to 1,500 points for a readable chart.
- Ten-fold CV uses a reproducible sample of up to 6,000 complete records to keep runtime manageable on the full multi-station dataset. Preprocessing is inside a scikit-learn Pipeline so each fold learns its own imputation/scaling values.
- CV results are computed when the page is first opened. They are not hard-coded.
