import numpy as np
import pandas
from pathlib import Path
from Baza_oraz_GUI.db_manager import DatabaseManager

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

def get_data_from_csv(filepath : str = 'company_esg_financial_dataset.csv'):
    filepath = LOCAL_FOLDER / filepath

    dataFrame = pandas.read_csv(filepath)
    return dataFrame


def get_data_year_range(dataFrame : pandas.DataFrame, min, max):
     return dataFrame[(dataFrame['Year'] >= min) & (dataFrame['Year'] <= max)]
    

def aggregate_data_stats(dataFrame : pandas.DataFrame):
    """
    W tej funkcji decydujecie po czym agregujecie.
    Agregujecie po wszystkim, co jest w liscie "metrics"
    Chcecie dodac nowa statystyke, to tworzycie funkcje, ktora ją wylicza
    i dorzucacie na koniec listy
    """

    numeric_cols = ['Revenue', 'ProfitMargin', 'MarketCap', 'GrowthRate', 'ESG_Overall']
    
    string_cols = ['CompanyID', 'CompanyName', 'Industry', 'Region']

    # WMA - Weighted Moving Average (średnia ważona zamiast zwykłej)
    metrics = [WMA, 'std', cv, slope]
    
    dataFrame_grouped = dataFrame.groupby(string_cols)[numeric_cols].agg(metrics)
    dataFrame_grouped.columns = [f"{col[0]}_{col[1]}" for col in dataFrame_grouped.columns]
    dataFrame_grouped = dataFrame_grouped.reset_index()
    dataFrame_grouped = dataFrame_grouped.round(2)

    return dataFrame_grouped


def add_metrics(dataFrame : pandas.DataFrame):

    dataFrame['PriceToSales'] = dataFrame['MarketCap_WMA'] / dataFrame['Revenue_WMA'].replace(0, np.nan)
    dataFrame['NetIncome'] = dataFrame['Revenue_WMA'] * (dataFrame['ProfitMargin_WMA'] / 100)
    dataFrame['PriceToEarnings'] = dataFrame['MarketCap_WMA'] / dataFrame['NetIncome'].replace(0, np.nan)
    dataFrame['EarningsYield'] = dataFrame['NetIncome'] / dataFrame['MarketCap_WMA'].replace(0, np.nan)
    dataFrame['Risk-AdjustedGrowth'] = dataFrame['GrowthRate_WMA'] / dataFrame['GrowthRate_std'].replace(0,np.nan)
    dataFrame['Earnings-to-Growth'] = dataFrame['PriceToEarnings'] / dataFrame['Risk-AdjustedGrowth'].replace(0, np.nan)

    # Dla firm, w ktorych jest ujemny przychod netto lub ujemny wzrost firmy dajemy olbrzymią karę.
    down_trend_companies = ((dataFrame['NetIncome'] <= 0) | (dataFrame['Risk-AdjustedGrowth'] <= 0))
    MAX_PENALTY_VALUE = dataFrame['Earnings-to-Growth'].replace([np.inf, -np.inf], np.nan).quantile(0.95)
    dataFrame.loc[down_trend_companies, 'Earnings-to-Growth'] = MAX_PENALTY_VALUE

    ESG_STN = dataFrame['ESG_Overall_slope'] / dataFrame['ESG_Overall_cv'].replace(0, np.nan)
    ESG_STN_finite = ESG_STN.replace([np.inf, -np.inf], np.nan)
    cap = ESG_STN_finite.quantile(0.95)
    dataFrame['ESG_Signal-to-Noise'] = ESG_STN_finite.fillna(cap)
    dataFrame = dataFrame.round(2)

    return dataFrame


def WMA(x: pandas.Series) -> float:
    """
    Oblicza średnią ważoną (Weighted Moving Average) dla serii danych.
    Najnowsze obserwacje otrzymują najwyższą wagę, a najstarsze najniższą.
    Zakłada, że dane wejściowe są posortowane chronologicznie!
    """

    x_clean = x.dropna()
    n = len(x_clean)
    
    if n == 0:
        return np.nan
        
    # 2. Generujemy wagi liniowe: np. [1, 2, 3, 4, 5] dla 5 lat
    weights = np.arange(1, n + 1)
    
    # 3. Zwracamy średnią ważoną wbudowaną w NumPy
    # JEŚLI CHCEMY JEDNAK ZWYKŁĄ ŚREDNIĄ, to wystarczy usunąć linijkę niżej "weights=weights"
    return np.average(x_clean, weights=weights)


def cv(x : pandas.Series) -> float:
    """
    Oblicza współczynnik zmienności (Coefficient of Variation) dla serii danych.
    W pandas nie ma wbudowanego cv, wiec tutaj jest prosta funkcja lambda
    """
    wma_val = WMA(x)

    return x.std() / wma_val if wma_val != 0 else np.nan


def slope(y : pandas.Series) -> float:
    """
    Oblicza współczynnik kierunkowy regresji liniowej (tendencję).
    Dodatni = wzrost, ujemny = spadek.
    """
    if len(y) < 2:
        return np.nan
        
    x = np.arange(len(y))
    
    # polyfit zwraca listę [współczynnik_a, współczynnik_b] dla y = ax + b
    # Bierzemy indeks [0], czyli nasze 'a'
    slope = np.polyfit(x, y, 1)[0]
    return slope


def save_data_to_csv(dataFrame : pandas.DataFrame, output_dir, output_file):

    full_path = output_dir / output_file
    dataFrame.to_csv(full_path, index = False)


def standardization(dataFrame: pandas.DataFrame):
    dataFrame = dataFrame.replace([np.inf, -np.inf], np.nan)

    numeric_cols = dataFrame.select_dtypes(include=[np.number]).columns.tolist()
    
    if 'CompanyID' in numeric_cols:
        numeric_cols.remove('CompanyID')
    
    std_vals = dataFrame[numeric_cols].std()
    valid_cols = std_vals[std_vals > 0].index.tolist()
    
    skipped = [c for c in numeric_cols if c not in valid_cols]
    if skipped:
        print(f"Skipping standardization for constant columns: {skipped}")
    
    mean_vals = dataFrame[valid_cols].mean()
    std_vals_valid = dataFrame[valid_cols].std()
    dataFrame[valid_cols] = (dataFrame[valid_cols] - mean_vals) / std_vals_valid
    dataFrame[valid_cols] = dataFrame[valid_cols].round(4)
    
    return dataFrame


def clean_data_for_fuzzy(dataFrame: pandas.DataFrame):
    df_clean = dataFrame.copy()
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)

    # Diagnostic: see who dies and why
    key_cols = ['EarningsYield', 'Risk-AdjustedGrowth', 'ESG_Signal-to-Noise']
    dropped = df_clean[df_clean[key_cols].isna().any(axis=1)][['CompanyName'] + key_cols]
    if not dropped.empty:
        print(f"Dropping {len(dropped)} rows due to NaN:\n{dropped}\n")

    df_clean = df_clean.dropna(subset=key_cols)
    df_clean = df_clean.reset_index(drop=True)
    return df_clean

if __name__ == '__main__':
    df = get_data_from_csv()
    df = get_data_year_range(df, 2022, 2024)
    df = aggregate_data_stats(df)
    df = add_metrics(df)
    df = standardization(df)
    df = clean_data_for_fuzzy(df)
    save_data_to_csv(df, LOCAL_FOLDER, 'aggregated_company_data.csv')

    # db_manager = DatabaseManager('financial_data.db')
    # db_manager.save_companies(df)
    
    # df_from_db = db_manager.get_companies()
    # print(df_from_db.head())

    # print("\n" + "="*40)
    # print("  GENEROWANIE RAPORTÓW Z BAZY DANYCH  ")
    # print("="*40)
    
    # print("\n[Raport 1] Firmy z regionu Europa:")
    # europe_df = db_manager.get_companies_by_region('Europe')
    # print(europe_df)
    
    # print("\n[Raport 2] TOP 3 firmy z najlepszym sygnałem ESG:")
    # top_esg = db_manager.get_top_esg_stars(limit=3)
    # print(top_esg)