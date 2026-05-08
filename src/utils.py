import numpy as np
import pandas
from pathlib import Path


LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

def get_data_from_csv(filepath : str = 'company_esg_financial_dataset.csv'):
    filepath = LOCAL_FOLDER / filepath

    dataFrame = pandas.read_csv(filepath)
    return dataFrame

def get_data_year_range(dataFrame : pandas.DataFrame, min = 2020, max = 2024):
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

    dataFrame['PriceToSales'] = dataFrame['MarketCap_WMA'] / dataFrame['Revenue_WMA']
    dataFrame['NetIncome'] = dataFrame['Revenue_WMA'] * (dataFrame['ProfitMargin_WMA'] / 100)
    dataFrame['PriceToEarnings'] = dataFrame['MarketCap_WMA'] / dataFrame['NetIncome']
    dataFrame['EarningsYield'] = dataFrame['NetIncome'] / dataFrame['MarketCap_WMA']
    dataFrame['Risk-AdjustedGrowth'] = dataFrame['GrowthRate_WMA'] / dataFrame['GrowthRate_std']
    dataFrame['Earnings-to-Growth'] = dataFrame['PriceToEarnings'] / dataFrame['Risk-AdjustedGrowth']
    dataFrame['ESG_Signal-to-Noise'] = dataFrame['ESG_Overall_slope'] / dataFrame['ESG_Overall_cv']
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

def save_data_to_csv(dataFrame : pandas.DataFrame):
    output_dir = LOCAL_FOLDER
    output_file = 'aggregated_company_data.csv'

    full_path = output_dir / output_file

    dataFrame.to_csv(full_path, index = False)

if __name__ == '__main__':
    df = get_data_from_csv()
    df = get_data_year_range(df)
    df = aggregate_data_stats(df)
    df = add_metrics(df)
    save_data_to_csv(df)