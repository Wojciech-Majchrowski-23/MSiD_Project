import pandas as pd
from utils import get_data_from_csv
from pathlib import Path
import matplotlib.pyplot as plt

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

def create_concentration_portfolios(scored_df):
    sorted_df = scored_df.sort_values(by='TARGET_SCORE', ascending=False).copy()
    
    top_3 = sorted_df.head(3).copy()
    top_10 = sorted_df.head(10).copy()
    top_30 = sorted_df.head(30).copy()
    all_market = sorted_df.copy()
    
    return top_3, top_10, top_30, all_market

def calculate_returns_cash(portfolio_df, raw_df, initial_cash=100000, years=[2024, 2025]):
    portfolio_df = portfolio_df.copy()
    portfolio_df['TARGET_SCORE'] = pd.to_numeric(portfolio_df['TARGET_SCORE'], errors='coerce')
    portfolio_df = portfolio_df.dropna(subset=['TARGET_SCORE'])
    
    portfolio_df['Weight'] = 1.0 / len(portfolio_df)
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

def plot_concentration_test(top3_res, top10_res, top30_res, all_res):
    years = sorted(top3_res.keys())
    
    plt.figure(figsize=(12, 7))
    
    plt.plot(years, [top3_res[y]*100 for y in years], 
             marker='*', label='TOP 3 (Wysokie ryzyko/zysk)', color='#d62728', linewidth=4, markersize=14)
             
    plt.plot(years, [top10_res[y]*100 for y in years], 
             marker='o', label='TOP 10 (Złoty środek)', color='#2ca02c', linewidth=3, markersize=10)
    
    plt.plot(years, [top30_res[y]*100 for y in years], 
             marker='s', label='TOP 30 (Bezpieczna dywersyfikacja)', color='#1f77b4', linewidth=2)
             
    plt.plot(years, [all_res[y]*100 for y in years], 
             marker='.', label='Cały Badany Rynek (Benchmark)', color='gray', linestyle='--', linewidth=2)

    plt.axhline(0, color='black', linewidth=1, alpha=0.5)
    plt.title('Porównanie portfeli', fontsize=15, pad=15)
    plt.ylabel('Skumulowany Zysk / Strata (%)', fontsize=12)
    plt.xlabel('Rok', fontsize=12)
    plt.xticks(years)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    offsets = [15, 0, -15]
    for res, color, offset in zip([top3_res, top10_res, top30_res], ['#d62728', '#2ca02c', '#1f77b4'], offsets):
        final_val = res[2025]*100
        plt.annotate(f'{final_val:.1f}%', xy=(2025, final_val), xytext=(15, offset), 
                     textcoords='offset points', weight='bold', color=color, fontsize=11)

    plt.show()

def run_final_simulation():
    raw_df = get_data_from_csv('company_esg_financial_dataset.csv')
    scored_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data.csv', sep=',')
    
    top3_df, top10_df, top30_df, all_df = create_concentration_portfolios(scored_df)
    
    top3_roi, top3_cash = calculate_returns_cash(top3_df, raw_df)
    top10_roi, top10_cash = calculate_returns_cash(top10_df, raw_df)
    top30_roi, top30_cash = calculate_returns_cash(top30_df, raw_df)
    all_roi, all_cash = calculate_returns_cash(all_df, raw_df)

    print("-" * 45)
    print("WYNIKI TESTU (Kapitał: 100,000 PLN)")
    print("-" * 45)
    print(f"TOP 3    Zysk: {top3_cash[2025] - 100000:>10,.2f} PLN")
    print(f"TOP 10  Zysk: {top10_cash[2025] - 100000:>10,.2f} PLN")
    print(f"TOP 30 Zysk: {top30_cash[2025] - 100000:>10,.2f} PLN")
    print(f"Cały Rynek     Zysk: {all_cash[2025] - 100000:>10,.2f} PLN")
    print("-" * 45)
    
    plot_concentration_test(top3_roi, top10_roi, top30_roi, all_roi)

if __name__ == '__main__':
    run_final_simulation()