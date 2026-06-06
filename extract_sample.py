import pandas as pd
from sqlalchemy import create_engine
import os

DB_CONFIG = {
    'host': 'localhost', 'port': 5433, 'database': 'careflow_ai',
    'user': 'postgres', 'password': 'postgres',
}
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

print("Connecting to PostgreSQL...")
engine = create_engine(DATABASE_URL)

print("Extracting 100,000 records...")
query = "SELECT * FROM cms_medicare_providers LIMIT 100000"
df = pd.read_sql(query, engine)

os.makedirs('sample_data', exist_ok=True)
output_path = 'sample_data/cms_medicare_providers.csv'
df.to_csv(output_path, index=False)
print(f"Successfully saved {len(df)} records to {output_path}")
