import os
import pandas as pd

def load_csv(file_path):
    """Load a CSV file safely."""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded: {os.path.basename(file_path)} | Rows: {len(df)} | Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return pd.DataFrame()

def merge_safely(left_df, right_df, possible_keys):
    """Merge two dataframes using the best available common keys."""
    common_keys = [k for k in possible_keys if k in left_df.columns and k in right_df.columns]
    if not common_keys:
        print("⚠️ No common keys found between datasets. Skipping merge.")
        return left_df
    print(f"🔗 Merging using keys: {common_keys}")
    return pd.merge(left_df, right_df, on=common_keys, how='outer')

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading CSV files from: {data_dir}")

    # Load all datasets
    crop_df = load_csv(os.path.join(data_dir, "crop_yield.csv"))
    rain_df = load_csv(os.path.join(data_dir, "rainfall.csv"))
    temp_df = load_csv(os.path.join(data_dir, "temperature.csv"))
    weather_df = load_csv(os.path.join(data_dir, "weather.csv"))
    pest_df = load_csv(os.path.join(data_dir, "pesticides.csv"))
    yield_off_df = load_csv(os.path.join(data_dir, "yield_off.csv"))

    # Merge dynamically using best possible keys
    merged_df = crop_df
    possible_keys = ['area', 'region', 'district', 'state', 'year']

    for df, name in zip(
        [rain_df, temp_df, weather_df, pest_df, yield_off_df],
        ['rainfall', 'temperature', 'weather', 'pesticides', 'yield_off']
    ):
        print(f"\n🔹 Merging {name}.csv ...")
        merged_df = merge_safely(merged_df, df, possible_keys)

    print("\n✅ All datasets merged successfully!")
    print(f"Final columns: {list(merged_df.columns)}")

    # Handle missing values
    merged_df.fillna(method='ffill', inplace=True)
    merged_df.fillna(method='bfill', inplace=True)

    # Normalize numeric columns
    for col in merged_df.select_dtypes(include=['float64', 'int64']).columns:
        merged_df[col] = (merged_df[col] - merged_df[col].min()) / (merged_df[col].max() - merged_df[col].min())

    # Save processed data
    output_path = os.path.join(output_dir, "processed_data.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"\n💾 Processed dataset saved to: {output_path}")

if __name__ == "__main__":
    main()
