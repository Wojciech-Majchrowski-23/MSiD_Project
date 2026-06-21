import pandas as pd
import re  # DODANE: Biblioteka do wyrażeń regularnych
from utils import get_data_from_csv

def load_raw_data():
    """
    Wczytuje surowe dane przy użyciu istniejącej funkcji z utils.py.
    """
    return get_data_from_csv('company_esg_financial_dataset.csv')

def get_unique_companies(raw_df):
    """
    Pobiera i sortuje w sposób naturalny listę unikalnych spółek z pliku.
    """
    if 'CompanyName' in raw_df.columns:
        companies = raw_df['CompanyName'].dropna().unique().tolist()
        
        # Funkcja rozbijająca tekst, dzięki której Python rozpoznaje liczby w stringu
        def natural_keys(text):
            return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]
            
        return sorted(companies, key=natural_keys)
    
    return []


def calculate_custom_portfolio_returns(portfolio_list, raw_df, invest_year):
    """
    Oblicza zysk/stratę z wybranego portfela użytkownika.
    :param portfolio_list: lista słowników [{'name': 'Firma A', 'amount': 1000.0}, ...]
    :param raw_df: surowy DataFrame z danymi o firmach
    :param invest_year: rok inwestycji, sprawdzamy MarketCap dla invest_year i invest_year + 1
    """
    total_initial_investment = 0.0
    total_value_next_year = 0.0
    
    details = []

    for item in portfolio_list:
        c_name = item['name']
        cash_in = item['amount']
        total_initial_investment += cash_in
        
        try:
            # Filtrowanie danych dla konkretnej firmy
            comp_df = raw_df[raw_df['CompanyName'] == c_name]
            
            if comp_df.empty:
                raise ValueError("Brak spółki")

            # Pobieramy rynkową kapitalizację (MarketCap) dla roku bazowego i następnego
            mcap_start_df = comp_df[comp_df['Year'] == invest_year]
            mcap_end_df = comp_df[comp_df['Year'] == invest_year + 1]
            
            # Jeżeli nie ma pełnych danych do wyliczenia wzrostu, symulujemy zachowanie kapitału na poziomie 0%
            if mcap_start_df.empty or mcap_end_df.empty:
                current_value = cash_in
            else:
                mcap_start = mcap_start_df['MarketCap'].values[0]
                mcap_end = mcap_end_df['MarketCap'].values[0]
                current_value = cash_in * (mcap_end / mcap_start)
                
            total_value_next_year += current_value
            
            details.append({
                'company': c_name,
                'invested': cash_in,
                'final_value': current_value
            })
            
        except Exception:
            # Fallback dla nieoczekiwanych błędów per spółka
            total_value_next_year += cash_in
            details.append({
                'company': c_name,
                'invested': cash_in,
                'final_value': cash_in
            })
            
    # Obliczenie całkowitego współczynnika ROI
    roi = (total_value_next_year - total_initial_investment) / total_initial_investment if total_initial_investment > 0 else 0.0
    
    return roi, total_value_next_year, details