import numpy as np
import pandas

def get_data_from_csv(filename = r'local_folder\company_esg_financial_dataset.csv'):

    dataFrame = pandas.read_csv(filename)
    return dataFrame

def get_data_year_range(dataFrame : pandas.DataFrame, min = 2020, max = 2024):
     return dataFrame[(dataFrame['Year'] >= min) & (dataFrame['Year'] <= max)]
    
def aggregate_data_mean_sd_cv(dataFrame : pandas.DataFrame):

    numeric_cols = ['Revenue', 'ProfitMargin', 'MarketCap', 'GrowthRate', 
                'ESG_Overall', 'ESG_Environmental', 'ESG_Social', 'ESG_Governance',
                'CarbonEmissions', 'WaterUsage', 'EnergyConsumption']
    
    string_cols = ['CompanyID', 'CompanyName', 'Industry', 'Region']

    metrics = ['mean', 'std', cv]
    
    dataFrame_grouped = dataFrame.groupby(string_cols)[numeric_cols].agg(metrics)
    dataFrame_grouped.columns = [f"{col[0]}_{col[1]}" for col in dataFrame_grouped.columns]
    dataFrame_grouped = dataFrame_grouped.reset_index()
    dataFrame_grouped = dataFrame_grouped.round(2)

    return dataFrame_grouped

def cv(x : float):
    """
    Oblicza współczynnik zmienności (Coefficient of Variation) dla serii danych.
    W pandas nie ma wbudowanego cv, wiec tutaj jest prosta funkcja lambda
    """
    return x.std() / x.mean() if x.mean() != 0 else np.nan

def save_data_to_csv(dataFrame : pandas.DataFrame, directory = 'local_folder'):
    output_file = 'aggregated_company_data.csv'
    dataFrame.to_csv(fr"{directory}\{output_file}", index = False)

if __name__ == '__main__':
    df = get_data_from_csv()
    df = get_data_year_range(df)
    df = aggregate_data_mean_sd_cv(df)
    save_data_to_csv(df)