import pandas as pd
import numpy as np
import utils 
from pathlib import Path

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

# "Y COLUMN" to kolumna wynikowa modelu(Ground Truth)
# Target_score jest tutaj znormalizowanym wynikiem Min-Max [0, 100] po odcięciu kwantyli (Winsoryzacji).

# UWAGA !!!
# curr_mcap (rok z którego jest) nie może pokrywać się z rokiem, który jest w przedziale w funkcji get_data_year_range()
# jesli year = x, to prawa strona przedziału (max) musi wynosić: max = x -1

def calculate_and_add_Y_column(year, company_df):
    if 'YEAR_TO_YEAR_MCAP' not in company_df.columns:
        company_df['YEAR_TO_YEAR_MCAP'] = np.nan
    if 'TARGET_SCORE' not in company_df.columns:
        company_df['TARGET_SCORE'] = np.nan

    # 1. Wyciągamy kapitalizacje dla danego roku i poprzedniego
    prev_mcap = company_df[company_df['Year'] == year - 1].set_index('CompanyID')['MarketCap']
    curr_mcap = company_df[company_df['Year'] == year].set_index('CompanyID')['MarketCap']

    # 2. Obliczamy surowy stosunek YoY
    yoy_ratio = curr_mcap / prev_mcap

    # =====================================================================
    # 3. WINSORYZACJA I MIN-MAX SCALING (Metoda z kwantylami 0.05 i 0.95)
    # =====================================================================
    
    # Krok A: Wyliczamy bezpieczne granice dla TEGO KONKRETNEGO ROKU
    MIN_QUANTILE = 0.05
    MAX_QUANTILE = 0.95
    
    q_min = yoy_ratio.quantile(MIN_QUANTILE)
    q_max = yoy_ratio.quantile(MAX_QUANTILE)
    
    # Krok B: Obcinamy "meme stocks" oraz firmy bankrutujące. 
    # Funkcja clip() sprawia, że wszystko powyżej q_max dostaje wartość q_max.
    yoy_clipped = yoy_ratio.clip(lower=q_min, upper=q_max)
    
    # Krok C: Min-Max Scaling na odciętym zbiorze do perfekcyjnego zakresu [0, 1]
    # Wzór: (x - min) / (max - min)
    yoy_scaled_0_1 = (yoy_clipped - q_min) / (q_max - q_min)
    
    # Krok D: Mnożymy * 100, ponieważ Twój system rozmyty ma Consequent od 0 do 100.
    # (Jeśli wolisz czyste [0, 1] do innego algorytmu ML, po prostu usuń to * 100)
    target_score = yoy_scaled_0_1 * 100

    # 4. Przypisanie wyników w miejsce odpowiadające danemu rokowi w głównym DataFrame
    mask = company_df['Year'] == year
    company_df.loc[mask, 'YEAR_TO_YEAR_MCAP'] = company_df.loc[mask, 'CompanyID'].map(yoy_ratio)
    company_df.loc[mask, 'TARGET_SCORE'] = company_df.loc[mask, 'CompanyID'].map(target_score)

    return company_df

def merge_data_frames(df_features, df_target, target_year):
    # 1. Wyciągamy z targetu TYLKO ten rok, w którym fizycznie wyliczyliśmy ocenę (żeby nie powielić wierszy)
    df_target_filtered = df_target[df_target['Year'] == target_year]
    
    # 2. Usuwamy ewentualne braki danych (np. firmy, które zniknęły w 2025)
    df_target_filtered = df_target_filtered.dropna(subset=['TARGET_SCORE'])

    # 3. Łączymy: Lewa strona to nasze zagregowane cechy (X), Prawa to nasz wyliczony cel (Y)
    df_final_ml = pd.merge(
        df_features, 
        df_target_filtered[['CompanyID', 'TARGET_SCORE']], 
        on='CompanyID', 
        how='inner'
    )

    return df_final_ml

    
if __name__ == '__main__':

    # Nowy folder bo za dużo tych plików csv
    ML_dataset_dir = LOCAL_FOLDER / "ML_dataset"
    ML_dataset_dir.mkdir(parents=True, exist_ok=True)

    TARGET_YEAR = 2025

    # 1a) wyliczenie kolumn yoy_marketCap i TargetScore z oryginalnych danych
    df_target = utils.get_data_from_csv('company_esg_financial_dataset.csv')
    df_target = calculate_and_add_Y_column(TARGET_YEAR, df_target)
    # utils.save_data_to_csv(df_target, ML_dataset_dir, 'yoy_mc_check.csv')

    # 1b) preprocessing przez utils (ML lepiej dziala jak dane maja zakres są ustandaryzowane, a nie tylko kolumna Y)
    df_features = utils.get_data_from_csv('company_esg_financial_dataset.csv')
    # To, o czym pisałem na górze: TARGET_YEAR - 1
    df_features = utils.get_data_year_range(df_features, 2022, TARGET_YEAR - 1)
    df_features = utils.aggregate_data_stats(df_features)
    df_features = utils.add_metrics(df_features)
    df_features = utils.standardization(df_features)
    df_features = utils.clean_data_for_fuzzy(df_features)

    # 2) Merge dwóch datasetów (doklejenie kolumny target_score wyliczonej z yoy_mc)
    df_final_ML = merge_data_frames(df_features, df_target, TARGET_YEAR)
    utils.save_data_to_csv(df_final_ML, ML_dataset_dir, 'ML_dataset_merged.csv')

    print(f"Sukces! Wygenerowano finalny zbiór ML z {len(df_final_ML)} wierszami.")