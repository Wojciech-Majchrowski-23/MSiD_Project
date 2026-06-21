import pandas as pd
import numpy as np
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

def calculate_returns_2025(portfolio_df, raw_df, initial_cash=100000):
    portfolio_df = portfolio_df.copy()
    portfolio_df['TARGET_SCORE'] = pd.to_numeric(portfolio_df['TARGET_SCORE'], errors='coerce')
    portfolio_df = portfolio_df.dropna(subset=['TARGET_SCORE'])
    
    portfolio_df['Weight'] = 1.0 / len(portfolio_df)
    portfolio_df['Initial_Investment'] = initial_cash * portfolio_df['Weight']
    
    total_value_2025 = 0
    
    for _, row in portfolio_df.iterrows():
        cid = row['CompanyID']
        cash_in_company = row['Initial_Investment']
        
        try:
            mcap_24 = raw_df[(raw_df['CompanyID'] == cid) & (raw_df['Year'] == 2023)]['MarketCap'].values[0]
            mcap_25 = raw_df[(raw_df['CompanyID'] == cid) & (raw_df['Year'] == 2024)]['MarketCap'].values[0]
            
            current_value = cash_in_company * (mcap_25 / mcap_24)
            total_value_2025 += current_value
        except:
            total_value_2025 += cash_in_company
            
    roi = (total_value_2025 - initial_cash) / initial_cash
    return roi, total_value_2025

def plot_comparison_bar_chart(hfs_res, pca_res):
    strategies = ['TOP 3', 'TOP 10', 'TOP 30']
    
    hfs_scores = [hfs_res['top3'][0]*100, hfs_res['top10'][0]*100, hfs_res['top30'][0]*100]
    pca_scores = [pca_res['top3'][0]*100, pca_res['top10'][0]*100, pca_res['top30'][0]*100]

    x = np.arange(len(strategies))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width/2, hfs_scores, width, label='HFS', color='#1f77b4', edgecolor='black')
    bars2 = ax.bar(x + width/2, pca_scores, width, label='PCA', color='#d62728', edgecolor='black')

    ax.axhline(0, color='black', linewidth=1)

    ax.set_ylabel('Roczna Stopa Zwrotu w 2025 (%)', fontsize=12)
    ax.set_title('Porównanie Modeli: HFS vs PCA na rynku w 2025', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            va_dir = 'bottom' if height >= 0 else 'top'
            xy_offset = (0, 5) if height >= 0 else (0, -15)
            ax.annotate(f'{height:.2f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=xy_offset, textcoords="offset points",
                        ha='center', va=va_dir, weight='bold', fontsize=10)

    add_labels(bars1)
    add_labels(bars2)

    all_scores = hfs_scores + pca_scores
    plt.ylim(min(all_scores) * 1.3 if min(all_scores) < 0 else -5, max(all_scores) * 1.3 if max(all_scores) > 0 else 5)

    plt.tight_layout()
    plt.show()

def run_final_simulation():
    raw_df = get_data_from_csv('company_esg_financial_dataset.csv')
    
    hfs_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data_HFS.csv', sep=',')
    pca_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data_PCA_RULES.csv', sep=',')
    
    hfs_top3, hfs_top10, hfs_top30, all_market = create_concentration_portfolios(hfs_df)
    pca_top3, pca_top10, pca_top30, _ = create_concentration_portfolios(pca_df)
  
    hfs_res = {
        'top3': calculate_returns_2025(hfs_top3, raw_df),
        'top10': calculate_returns_2025(hfs_top10, raw_df),
        'top30': calculate_returns_2025(hfs_top30, raw_df)
    }
    
    pca_res = {
        'top3': calculate_returns_2025(pca_top3, raw_df),
        'top10': calculate_returns_2025(pca_top10, raw_df),
        'top30': calculate_returns_2025(pca_top30, raw_df)
    }
    
    market_res = calculate_returns_2025(all_market, raw_df)

    print("=" * 65)
    print("PORÓWNANIE MODELI: HFS vs PCA")
    print(f"Kapitał początkowy: 100,000 PLN | Zysk rynku: {market_res[1]-100000:,.2f} PLN ({market_res[0]*100:.2f}%)")
    print("=" * 65)
    print(f"{'Portfel':<15} | {'Zysk/Strata HFS (PLN)':<22} | {'Zysk/Strata PCA (PLN)':<22}")
    print("-" * 65)
    print(f"{'TOP 3':<15} | {hfs_res['top3'][1] - 100000:>14,.2f} ({hfs_res['top3'][0]*100:>5.2f}%) | {pca_res['top3'][1] - 100000:>14,.2f} ({pca_res['top3'][0]*100:>5.2f}%)")
    print(f"{'TOP 10':<15} | {hfs_res['top10'][1] - 100000:>14,.2f} ({hfs_res['top10'][0]*100:>5.2f}%) | {pca_res['top10'][1] - 100000:>14,.2f} ({pca_res['top10'][0]*100:>5.2f}%)")
    print(f"{'TOP 30':<15} | {hfs_res['top30'][1] - 100000:>14,.2f} ({hfs_res['top30'][0]*100:>5.2f}%) | {pca_res['top30'][1] - 100000:>14,.2f} ({pca_res['top30'][0]*100:>5.2f}%)")
    print("=" * 65)
    
    plot_comparison_bar_chart(hfs_res, pca_res)

if __name__ == '__main__':
    run_final_simulation()