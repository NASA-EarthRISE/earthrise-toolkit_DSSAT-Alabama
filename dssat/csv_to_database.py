from pathlib import Path
import pandas as pd
import json
from sqlalchemy import create_engine, text

# === CONFIGURATION ===
csv_file = 'Yield_2010_2020.csv'  # Replace with your CSV file path
schema = 'alabama'
table_name = 'historical_yield'
BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )
config = json.load(f)

db_url = f"postgresql://{config['DBUSER']}:{config['PASSWORD']}@{config['HOST']}:5432/{config['USERNAME']}"
engine = create_engine(db_url)

# === LOAD AND PREPARE CSV ===
df = pd.read_csv(csv_file)
df = df.drop(columns=df.columns[0])  # Drop ID column

# Rename CSV columns to expected names
df.columns = ['county', 'fips_code', 'rainfed', 'irrigated', 'year']

# Clean and convert types
df['fips_code'] = df['fips_code'].astype(str).str.extract(r'(\d+)').astype(int)
df['rainfed'] = df['rainfed'].astype(float).round(4)
df['irrigated'] = df['irrigated'].astype(float).round(4)
df['year'] = df['year'].astype(int)

# Add default values for missing columns
df['crop_name'] = 'corn'
df['soil_type'] = 'unknown'
df['cultivar'] = 'long'  # normalized lowercase

# Normalize string columns: strip spaces and lowercase
for col in ['crop_name', 'soil_type', 'cultivar']:
    df[col] = df[col].str.strip().str.lower()

# === INSERT DEFAULT CROP AND SOIL_TYPE IF NOT EXISTS ===
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO alabama.crop (name) VALUES (:name) ON CONFLICT DO NOTHING"),
        {"name": 'corn'}
    )
    conn.execute(
        text("INSERT INTO alabama.soil_type (soil_type) VALUES (:soil) ON CONFLICT DO NOTHING"),
        {"soil": 'unknown'}
    )

# === INSERT MISSING COUNTIES INTO alabama.county ===
with engine.begin() as conn:
    unique_counties = df[['fips_code', 'county']].drop_duplicates()
    for _, row in unique_counties.iterrows():
        conn.execute(
            text("""
                INSERT INTO alabama.county (fips_code, name)
                VALUES (:fips_code, :name)
                ON CONFLICT (fips_code) DO NOTHING
            """),
            {"fips_code": int(row['fips_code']), "name": row['county']}
        )

# === LOAD EXISTING historical_yield TO DEDUPLICATE ===
query = f"""
SELECT crop_name, soil_type, rainfed, irrigated, year, cultivar, fips_code
FROM {schema}.{table_name}
"""
existing_df = pd.read_sql(query, engine)

# Normalize existing data string columns as well
for col in ['crop_name', 'soil_type', 'cultivar']:
    existing_df[col] = existing_df[col].str.strip().str.lower()

# Round numeric columns in existing data
for col in ['rainfed', 'irrigated']:
    existing_df[col] = existing_df[col].astype(float).round(4)

# Ensure int types
for col in ['year', 'fips_code']:
    df[col] = df[col].astype(int)
    existing_df[col] = existing_df[col].astype(int)

# Define key columns for deduplication
key_cols = ['crop_name', 'soil_type', 'rainfed', 'irrigated', 'year', 'cultivar', 'fips_code']

# Sanity check for missing columns
missing = [col for col in key_cols if col not in df.columns]
if missing:
    raise ValueError(f"Missing columns in df: {missing}")

missing_existing = [col for col in key_cols if col not in existing_df.columns]
if missing_existing:
    raise ValueError(f"Missing columns in existing_df: {missing_existing}")

# Create deduplication keys explicitly
def make_key(row):
    return '-'.join(str(row[col]) for col in key_cols)

df['dedup_key'] = df.apply(make_key, axis=1)
existing_df['dedup_key'] = existing_df.apply(make_key, axis=1)

# Select new rows not already in DB
df_to_insert = df[~df['dedup_key'].isin(existing_df['dedup_key'])].drop(columns=['dedup_key'])

print(f"Rows in CSV: {len(df)}")
print(f"Rows already in DB: {len(existing_df)}")
print(f"Rows to insert after deduplication: {len(df_to_insert)}")

# Drop 'county' before inserting into historical_yield (not a DB column)
df_to_insert = df_to_insert.drop(columns=['county'], errors='ignore')

# Insert new records
if not df_to_insert.empty:
    df_to_insert.to_sql(table_name, engine, schema=schema, if_exists='append', index=False)
    print(f"✅ Inserted {len(df_to_insert)} new rows into {schema}.{table_name}")
else:
    print("ℹ️ No new rows to insert.")
