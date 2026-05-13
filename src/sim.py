import pandas as pd
from utils import get_data_from_csv
from pathlib import Path
import numpy as np
import random
import matplotlib.pyplot as plt

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

def create_portfolios(scored_df, top_n=10):
    
    sorted_df = scored_df.sort_values(by='TARGET_SCORE', ascending=False).copy()
    
    top_df = sorted_df.iloc[0:11].copy()
    bottom_df = sorted_df.tail(top_n).copy()


    print("\n" + "="*30)
    print("TOP 3 LIDERÓW PORTFELA:")
    top_3 = top_df.head(3)
    for i, (idx, row) in enumerate(top_3.iterrows(), 1):
        print(f"{i}. ID: {row['CompanyID']} | Score: {row['TARGET_SCORE']:.4f}")
    print("="*30 + "\n")
    
    all_ids = scored_df['CompanyID'].unique()
    top_ids = top_df['CompanyID'].tolist()
    remaining_ids = [idx for idx in all_ids if idx not in top_ids]
    random_company_ids = random.sample(remaining_ids, top_n)
    random_df = scored_df[scored_df['CompanyID'].isin(random_company_ids)].copy()
    
    return top_df, bottom_df, random_df

def calculate_score_weighted_returns_cash(portfolio_df, raw_df, initial_cash=100000, years=[2024, 2025]):
    portfolio_df = portfolio_df.copy()
    portfolio_df['TARGET_SCORE'] = pd.to_numeric(portfolio_df['TARGET_SCORE'], errors='coerce')
    portfolio_df = portfolio_df.dropna(subset=['TARGET_SCORE'])
    
    total_score = portfolio_df['TARGET_SCORE'].sum()
    portfolio_df['Weight'] = portfolio_df['TARGET_SCORE'] / total_score
    
    portfolio_df['Initial_Investment'] = initial_cash * portfolio_df['Weight']
    
    roi_results = {2023: 0.0}
    cash_results = {2023: initial_cash}
    
    for year in years:
        total_value_this_year = 0
        
        for _, row in portfolio_df.iterrows():
            cid = row['CompanyID']
            cash_in_company = row['Initial_Investment']
            
            try:
                mcap_23 = raw_df[(raw_df['CompanyID'] == cid) & (raw_df['Year'] == 2023)]['MarketCap'].values[0]
                mcap_curr = raw_df[(raw_df['CompanyID'] == cid) & (raw_df['Year'] == year)]['MarketCap'].values[0]
                
                current_value = cash_in_company * (mcap_curr / mcap_23)
                total_value_this_year += current_value
            except:
                total_value_this_year += cash_in_company
                
        cash_results[year] = total_value_this_year
        roi_results[year] = (total_value_this_year - initial_cash) / initial_cash
        
    return roi_results, cash_results

def plot_simulation(top_res, bottom_res, random_res):
    years = sorted(top_res.keys())
    
    plt.figure(figsize=(11, 7))
    
    plt.plot(years, [top_res[y]*100 for y in years], 
             marker='o', label='Portfel TOP (Weighted by Score)', color='#2ca02c', linewidth=3)
    
    plt.plot(years, [random_res[y]*100 for y in years], 
             marker='d', label='Portfel RANDOM', color='#ff7f0e', linestyle='--', linewidth=2)
    
    plt.plot(years, [bottom_res[y]*100 for y in years], 
             marker='s', label='Portfel BOTTOM', color='#d62728', linewidth=2)

    plt.axhline(0, color='black', linewidth=1, alpha=0.5)
    plt.title('Symulacja Inwestycyjna (2024-2025)', fontsize=14)
    plt.ylabel('Skumulowany Zysk / Strata (%)', fontsize=12)
    plt.xlabel('Rok', fontsize=12)
    plt.xticks(years)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    final_top = top_res[2025]*100
    plt.annotate(f'{final_top:.1f}%', xy=(2025, final_top), xytext=(5, 5), 
                 textcoords='offset points', weight='bold', color='#2ca02c')

    plt.show()

def run_final_simulation():
    raw_df = get_data_from_csv('company_esg_financial_dataset.csv')
    scored_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data.csv', sep=',')
    
    top_df, bottom_df, random_df = create_portfolios(scored_df, top_n=10)
    
    top_roi, top_cash = calculate_score_weighted_returns_cash(top_df, raw_df, initial_cash=100000)

    random_roi, random_cash = calculate_score_weighted_returns_cash(random_df, raw_df, initial_cash=100000)

    print("-" * 30)
    print(f"SYMULACJA INWESTYCYJNA (Kapitał początkowy: 100 000 PLN)")
    print(f"Wartość portfela po 2024: {top_cash[2024]:,.2f} PLN")
    print(f"Wartość portfela po 2025: {top_cash[2025]:,.2f} PLN")
    print(f"Czysty zysk: {top_cash[2025] - 100000:,.2f} PLN")
    print("-" * 30)


    print("-" * 30)
    print(f"SYMULACJA INWESTYCYJNA RANDOM (Kapitał początkowy: 100 000 PLN)")
    print(f"Wartość portfela po 2024: {random_cash[2024]:,.2f} PLN")
    print(f"Wartość portfela po 2025: {random_cash[2025]:,.2f} PLN")
    print(f"Czysty zysk: {random_cash[2025] - 100000:,.2f} PLN")
    print("-" * 30)
    


if __name__ == '__main__':
    run_final_simulation()