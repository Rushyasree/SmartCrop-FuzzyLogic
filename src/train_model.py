import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "output", "processed_data.csv")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)

    # Load dataset
    df = pd.read_csv(data_path)
    print(f"✅ Loaded processed data: {df.shape}")
    print(f"📊 Columns: {list(df.columns)}")

    # Automatically find numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if len(numeric_cols) < 2:
        raise ValueError("Not enough numeric columns to train the model. Please check your processed_data.csv file.")

    # Choose features and target
    target_col = numeric_cols[-1]   # Last numeric column as target
    feature_cols = numeric_cols[:-1]  # All others as features

    X = df[feature_cols]
    y = df[target_col]

    print(f"🧮 Using features: {feature_cols}")
    print(f"🎯 Using target: {target_col}")

    # Handle missing values
    X.fillna(0, inplace=True)
    y.fillna(0, inplace=True)

    # Split dataset
    if len(X) < 10:
        raise ValueError("Dataset too small for training. Check if merge or preprocessing failed.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"✅ Model trained successfully!")
    print(f"📈 R² Score: {r2:.4f}")
    print(f"📉 MAE: {mae:.4f}")

    # Save model and scaler
    model_path = os.path.join(model_dir, "crop_model.pkl")
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"💾 Model saved at: {model_path}")
    print(f"💾 Scaler saved at: {scaler_path}")

if __name__ == "__main__":
    main()
