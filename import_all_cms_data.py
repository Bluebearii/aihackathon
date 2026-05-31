"""
CareFlow AI — Full CMS Medicare Data Import Script
====================================================
Streams ALL records from the CMS Medicare Physician & Other Practitioners API
directly into PostgreSQL in batches (memory-efficient).

Usage:
    python import_all_cms_data.py
"""

import time
import sys
import requests
import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

CMS_API_URL = "https://data.cms.gov/data-api/v1/dataset/92396110-2aed-4d63-a6a2-5d6207d46a29/data"

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'careflow_ai',
    'user': 'postgres',
    'password': 'postgres',
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

BATCH_SIZE = 5_000       # records per API call (max the API supports well)
DB_CHUNK_SIZE = 2_000    # rows per INSERT statement
MAX_RETRIES = 5          # retries per failed batch
TOTAL_RECORDS = 1_500_000  # stop after 1.5 million records

# ============================================================
# COLUMN RENAME MAP
# ============================================================

COLUMN_RENAME_MAP = {
    'Rndrng_NPI':                     'provider_npi',
    'Rndrng_Prvdr_Last_Org_Name':     'provider_last_or_org_name',
    'Rndrng_Prvdr_First_Name':        'provider_first_name',
    'Rndrng_Prvdr_MI':                'provider_middle_initial',
    'Rndrng_Prvdr_Crdntls':           'provider_credentials',
    'Rndrng_Prvdr_Ent_Cd':            'provider_entity_type',
    'Rndrng_Prvdr_St1':               'provider_street_address_1',
    'Rndrng_Prvdr_St2':               'provider_street_address_2',
    'Rndrng_Prvdr_City':              'provider_city',
    'Rndrng_Prvdr_State_Abrvtn':      'provider_state',
    'Rndrng_Prvdr_State_FIPS':        'provider_state_fips',
    'Rndrng_Prvdr_Zip5':              'provider_zip_code',
    'Rndrng_Prvdr_RUCA':              'provider_ruca_code',
    'Rndrng_Prvdr_RUCA_Desc':         'provider_rural_urban_description',
    'Rndrng_Prvdr_Cntry':             'provider_country',
    'Rndrng_Prvdr_Type':              'provider_specialty',
    'Rndrng_Prvdr_Mdcr_Prtcptg_Ind':  'medicare_participating',
    'Rndrng_Prvdr_Gndr':              'provider_gender',
    'HCPCS_Cd':                       'procedure_code',
    'HCPCS_Desc':                     'procedure_description',
    'HCPCS_Drug_Ind':                 'is_drug_service',
    'Place_Of_Srvc':                  'place_of_service',
    'Tot_Benes':                      'total_patients',
    'Tot_Srvcs':                      'total_services',
    'Tot_Bene_Day_Srvcs':             'total_patient_day_services',
    'Avg_Sbmtd_Chrg':                 'avg_submitted_charge',
    'Avg_Mdcr_Alowd_Amt':             'avg_medicare_allowed_amount',
    'Avg_Mdcr_Pymt_Amt':              'avg_medicare_payment',
    'Avg_Mdcr_Stdzd_Amt':             'avg_medicare_standardized_amount',
}

NUMERIC_COLUMNS = [
    'total_patients', 'total_services', 'total_patient_day_services',
    'avg_submitted_charge', 'avg_medicare_allowed_amount',
    'avg_medicare_payment', 'avg_medicare_standardized_amount',
]

# ============================================================
# TABLE SCHEMA
# ============================================================

CREATE_TABLE_SQL = """
DROP TABLE IF EXISTS cms_medicare_providers CASCADE;

CREATE TABLE cms_medicare_providers (
    id                                SERIAL PRIMARY KEY,
    provider_npi                      VARCHAR(20),
    provider_last_or_org_name         VARCHAR(255),
    provider_first_name               VARCHAR(100),
    provider_middle_initial           VARCHAR(10),
    provider_credentials              VARCHAR(50),
    provider_entity_type              VARCHAR(5),
    provider_street_address_1         VARCHAR(255),
    provider_street_address_2         VARCHAR(255),
    provider_city                     VARCHAR(100),
    provider_state                    VARCHAR(5),
    provider_state_fips               VARCHAR(5),
    provider_zip_code                 VARCHAR(10),
    provider_ruca_code                VARCHAR(10),
    provider_rural_urban_description  TEXT,
    provider_country                  VARCHAR(5),
    provider_specialty                VARCHAR(255),
    medicare_participating            VARCHAR(5),
    provider_gender                   VARCHAR(5),
    procedure_code                    VARCHAR(20),
    procedure_description             TEXT,
    is_drug_service                   VARCHAR(5),
    place_of_service                  VARCHAR(5),
    total_patients                    INTEGER,
    total_services                    NUMERIC(15, 2),
    total_patient_day_services        NUMERIC(15, 2),
    avg_submitted_charge              NUMERIC(15, 2),
    avg_medicare_allowed_amount       NUMERIC(15, 2),
    avg_medicare_payment              NUMERIC(15, 2),
    avg_medicare_standardized_amount  NUMERIC(15, 2),
    imported_at                       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_provider_npi ON cms_medicare_providers(provider_npi);
CREATE INDEX idx_provider_state ON cms_medicare_providers(provider_state);
CREATE INDEX idx_provider_specialty ON cms_medicare_providers(provider_specialty);
CREATE INDEX idx_procedure_code ON cms_medicare_providers(procedure_code);
CREATE INDEX idx_provider_city_state ON cms_medicare_providers(provider_city, provider_state);
"""


def log(msg):
    """Print with timestamp."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def create_table(engine):
    """Drop and recreate the table."""
    log("Creating table schema...")
    with engine.connect() as conn:
        for statement in CREATE_TABLE_SQL.strip().split(';'):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()
    log("Table 'cms_medicare_providers' created with indexes.")


def process_batch(records, engine, table_columns):
    """Rename, clean, and insert a batch of records into PostgreSQL."""
    df = pd.DataFrame(records)
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)

    # Convert numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Replace empty strings with None
    df.replace('', None, inplace=True)

    # Keep only columns that match the table
    import_cols = [c for c in df.columns if c in table_columns]
    df = df[import_cols]

    # Insert into PostgreSQL
    df.to_sql(
        name='cms_medicare_providers',
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=DB_CHUNK_SIZE
    )
    return len(df)


def fetch_and_import():
    """Main pipeline: stream from API -> PostgreSQL."""
    log("=" * 60)
    log("CareFlow AI - Full CMS Medicare Data Import")
    log("=" * 60)

    # Connect to database
    engine = create_engine(DATABASE_URL, echo=False)
    log(f"Connected to PostgreSQL: {DB_CONFIG['database']} @ port {DB_CONFIG['port']}")

    # Recreate table
    create_table(engine)

    # Get table columns for filtering
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(engine)
    table_columns = [col['name'] for col in inspector.get_columns('cms_medicare_providers')]
    table_columns = [c for c in table_columns if c not in ('id', 'imported_at')]

    # Start fetching
    offset = 0
    batch_num = 0
    total_imported = 0
    start_time = time.time()

    log(f"Fetching {TOTAL_RECORDS:,} records from CMS API (batch size: {BATCH_SIZE:,})")
    log("-" * 60)

    while True:
        # Stop if we've reached the limit
        if total_imported >= TOTAL_RECORDS:
            log(f"Reached target of {TOTAL_RECORDS:,} records. Stopping.")
            break

        batch_num += 1
        retries = 0

        # Fetch with retry logic
        while retries < MAX_RETRIES:
            try:
                resp = requests.get(
                    CMS_API_URL,
                    params={'size': BATCH_SIZE, 'offset': offset},
                    timeout=120
                )
                resp.raise_for_status()
                records = resp.json()
                break
            except Exception as e:
                retries += 1
                wait = retries * 5
                log(f"  ERROR on batch {batch_num} (attempt {retries}/{MAX_RETRIES}): {e}")
                log(f"  Retrying in {wait}s...")
                time.sleep(wait)
        else:
            log(f"FAILED: Batch {batch_num} failed after {MAX_RETRIES} retries. Stopping.")
            break

        # End of dataset
        if not records:
            log(f"No more data at offset {offset:,}. Dataset complete!")
            break

        # Process and insert
        try:
            inserted = process_batch(records, engine, table_columns)
            total_imported += inserted
            offset += len(records)
            elapsed = time.time() - start_time
            rate = total_imported / elapsed if elapsed > 0 else 0

            log(
                f"  Batch {batch_num:>5,} | "
                f"Imported: {total_imported:>12,} | "
                f"Elapsed: {elapsed:>7.0f}s | "
                f"Rate: {rate:>6,.0f} rec/s"
            )
        except Exception as e:
            log(f"  DB INSERT ERROR on batch {batch_num}: {e}")
            log(f"  Skipping batch and continuing...")
            offset += len(records)
            continue

        # End of dataset (partial batch)
        if len(records) < BATCH_SIZE:
            log(f"Received {len(records)} < {BATCH_SIZE}. End of dataset.")
            break

        # Rate limit — be respectful to CMS API
        time.sleep(0.2)

    # Final summary
    total_time = time.time() - start_time
    log("=" * 60)
    log("IMPORT COMPLETE")
    log(f"  Total records imported: {total_imported:,}")
    log(f"  Total time: {total_time/60:.1f} minutes")
    log(f"  Average rate: {total_imported/total_time:,.0f} records/sec")
    log("=" * 60)

    # Verify
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM cms_medicare_providers")).scalar()
    log(f"  PostgreSQL row count: {count:,}")


if __name__ == '__main__':
    fetch_and_import()
