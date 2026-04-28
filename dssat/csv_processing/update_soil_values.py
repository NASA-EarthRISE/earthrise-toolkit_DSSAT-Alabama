import json
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
# === CONFIGURATION ===
schema = 'alabama'
BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )
config = json.load(f)

# 1. Load the CSV
df = pd.read_csv('ALSoilsSSURGOV2.csv')

# 2. Define the exact soil columns from your CSV
# (Notice these exactly match the text in your soil_type table)
soil_columns = [
    'Clay', 'Clay_Loam', 'Loam', 'Loamy_Sand', 'Sand',
    'Sandy_Clay', 'Sandy_Clay_Loam', 'Sandy_Loam',
    'Silt_Loam', 'Silty_Clay', 'Silty_Clay_Loam'
]

# 3. Unpivot the data (This turns the 67 rows into 737 rows)
df_melted = df.melt(
    id_vars=['FIPS'],           # Keep FIPS as the anchor
    value_vars=soil_columns,    # The columns we are melting down
    var_name='soil_type',       # The new column matching your lookup table
    value_name='soil_value'     # The actual numerical value
)

# 4. Clean up before inserting
# Rename FIPS to fips_code
df_melted.rename(columns={'FIPS': 'fips_code'}, inplace=True)

# Make sure fips_code is an integer to match your database
df_melted['fips_code'] = df_melted['fips_code'].astype(int)

# 5. Connect to PostgreSQL
db_url = f"postgresql://{config['DBUSER']}:{config['PASSWORD']}@{config['HOST']}:5432/{config['USERNAME']}"
engine = create_engine(db_url)

# 6. Push the 737 rows to a new mapping table in Postgres
df_melted.to_sql('county_soil_values', engine, schema='alabama', if_exists='replace', index=False)

print(f"Success! Inserted {len(df_melted)} rows into alabama.county_soil_values")