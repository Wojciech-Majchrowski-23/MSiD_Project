import numpy as np
import pandas

def get_data_from_csv(filename = r'local_folder\company_esg_financial_dataset.csv'):

    dataFrame = pandas.read_csv(filename)
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

    metrics = ['mean', 'std', cv, slope]
    
    dataFrame_grouped = dataFrame.groupby(string_cols)[numeric_cols].agg(metrics)
    dataFrame_grouped.columns = [f"{col[0]}_{col[1]}" for col in dataFrame_grouped.columns]
    dataFrame_grouped = dataFrame_grouped.reset_index()
    dataFrame_grouped = dataFrame_grouped.round(2)

    return dataFrame_grouped

def add_metrics(dataFrame : pandas.DataFrame):

    dataFrame['PriceToSales'] = dataFrame['MarketCap_mean'] / dataFrame['Revenue_mean']
    dataFrame['NetIncome'] = dataFrame['Revenue_mean'] * (dataFrame['ProfitMargin_mean'] / 100)
    dataFrame['PriceToEarnings'] = dataFrame['MarketCap_mean'] / dataFrame['NetIncome']
    dataFrame['Risk-AdjustedGrowth'] = dataFrame['GrowthRate_mean'] / dataFrame['GrowthRate_std']
    dataFrame = dataFrame.round(2)

    return dataFrame

def cv(x : pandas.Series) -> float:
    """
    Oblicza współczynnik zmienności (Coefficient of Variation) dla serii danych.
    W pandas nie ma wbudowanego cv, wiec tutaj jest prosta funkcja lambda
    """
    return x.std() / x.mean() if x.mean() != 0 else np.nan

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

def save_data_to_csv(dataFrame : pandas.DataFrame, directory = 'local_folder'):
    output_file = 'aggregated_company_data.csv'
    dataFrame.to_csv(fr"{directory}\{output_file}", index = False)

if __name__ == '__main__':
    df = get_data_from_csv()
    df = get_data_year_range(df)
    df = aggregate_data_stats(df)
    df = add_metrics(df)
    save_data_to_csv(df)