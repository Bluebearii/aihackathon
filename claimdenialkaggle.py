import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report


#TARGET COLUMN in claims.csv there is an 'outcome' column that has the column for target

#change this to your folder path for the csv folder
folder_path = "/Users/tommynguyen/codingprojects/AIhackathon/csv/"

#turns csvs into dictionary to have access to every one in the folder
dfs = {}
for file in os.listdir(folder_path):
    if file.endswith('.csv'):
        name = file.replace('.csv', '')
        dfs[name] = pd.read_csv(os.path.join(folder_path, file))


# for df_name, df in dfs.items():
#     print(f"\n=== {df_name} ===")
#     print(df.head())


#feature list
feature_list = [ 
    "payer_type", "provider_specialty", 
    "primary_icd10_dx","prior_auth_required",
    "prior_auth_obtained", "documentation_completeness",
    "claim_amount_usd","cpt_code"
]
stringdt_list =[
        "payer_type", "provider_specialty", "primary_icd10_dx", "cpt_code"
        ]


dfs["claims_main"]["binary_deny_outcome"] = np.where(dfs["claims_main"]["outcome"]=='denied', 1, 0)
onehotencode = pd.get_dummies(dfs["claims_main"], columns = stringdt_list)

#loops through feature list
# for col in feature_list:
#     print(f"\n=== {col} ===")
#     print(dfs["claims_main"][col].dtype)

#creates a binary classification for denials

y = onehotencode["binary_deny_outcome"]


X = onehotencode.select_dtypes(include=['number', 'bool']).drop(["binary_deny_outcome"], axis=1)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier()

model.fit(X_train,y_train)

y_pred = model.predict(X_test)

report = classification_report(y_pred, y_test)

print(report)

