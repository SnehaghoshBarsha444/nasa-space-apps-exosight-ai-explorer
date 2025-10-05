import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import joblib

# --- 1. Data Import ---
KEPLER_FILE = "cumulative_2025.10.03_00.23.38.csv"
SKIP_ROWS = 53 # Confirmed metadata rows to skip

try:
    df = pd.read_csv(KEPLER_FILE, skiprows=SKIP_ROWS)
except Exception as e:
    print(f"Error loading data: {e}. Check file name and skiprows value.")
    exit()

print("1. Data Imported Successfully.")

# --- 2. Feature and Target Selection (CRITICAL FIX: Including ID Columns) ---

# ID Columns are ABSOLUTELY required by the Streamlit app's display table
ID_COLUMNS = ['kepid', 'kepoi_name'] 
TARGET_COLUMN = 'koi_pdisposition'
FEATURE_COLUMNS = [
    'koi_period', 'koi_prad', 'koi_teq',  
    'koi_duration', 'koi_impact', 'koi_insol'
]

# Select all required columns for the model and display
ALL_COLUMNS = ID_COLUMNS + [TARGET_COLUMN] + FEATURE_COLUMNS
df_model = df[ALL_COLUMNS].copy()

# --- 3. Data Cleaning ---
df_model.dropna(subset=FEATURE_COLUMNS, inplace=True)
df_model['y'] = df_model[TARGET_COLUMN].apply(lambda x: 1 if x == 'CANDIDATE' else 0)

print(f"3. Shape after cleaning: {df_model.shape}")

# --- 4. Data Splitting and Scaling ---
X = df_model[FEATURE_COLUMNS]
y = df_model['y']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("4. Data preparation complete.")

# --- 5. MLP Training ---
mlp = MLPClassifier(hidden_layer_sizes=(16, 16), max_iter=500, random_state=42)
mlp.fit(X_train_scaled, y_train)

print("5. MLP Training Complete.")

# --- 6. Save Model and Scaler ---
joblib.dump(mlp, 'mlp_exoplanet_model.pkl')
joblib.dump(scaler, 'scaler_object.pkl')

print("6. Model and Scaler saved.")

# --- 7. Identify New High-Confidence Candidates ---
X_all_scaled = scaler.transform(X)
df_model['confidence'] = mlp.predict_proba(X_all_scaled)[:, 1]

# Filter for candidates with high confidence
new_candidates = df_model[
    (df_model['koi_pdisposition'] == 'FALSE POSITIVE') & 
    (df_model['confidence'] >= 0.90)
].sort_values(by='confidence', ascending=False)

print(f"7. Identified {len(new_candidates)} new candidates.")

# --- 8. Save Candidate List for the Web App (FINAL STEP) ---
# Select only the columns needed by the Streamlit display and save
columns_for_app = [
    'kepid', 'koi_pdisposition', 'confidence', 'koi_period', 'koi_prad', 
    'koi_teq', 'koi_duration', 'koi_impact', 'koi_insol'
]
candidates_to_save = new_candidates[columns_for_app].copy()

# This action overwrites the old, bad CSV file!
candidates_to_save.to_csv('ai_identified_candidates.csv', index=False)

print("8. SUCCESS: Corrected 'ai_identified_candidates.csv' file has been saved.")