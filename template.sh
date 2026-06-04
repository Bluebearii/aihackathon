mkdir -p data/raw data/processed notebooks src/data src/models src/utils models reports/charts

touch notebooks/01_data_cleaning.ipynb
touch notebooks/02_eda.ipynb
touch notebooks/03_no_show_model.ipynb

touch src/data/load_data.py
touch src/data/clean_data.py

touch src/models/train_no_show_model.py
touch src/models/predict.py

touch src/utils/helpers.py