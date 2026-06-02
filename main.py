import pandas as pd
import glob

#reading all csvs files for columns that would affect a denials claim
for file in glob.glob("/Users/tommynguyen/codingprojects/AIhackathon/output/csv/*.csv"):
    df = pd.read_csv(file)
    print(f"\n--- {file} ---")
    print(df.columns.tolist())


