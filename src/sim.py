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

def calculate_returns_in_year(year, portfolio_df, raw_df, initial_cash=100000):
    portfolio_df = portfolio_df.copy()
    portfolio_df['TARGET_SCORE'] = pd.to_numeric(portfolio_df['TARGET_SCORE'], errors='coerce')
    portfolio_df = portfolio_df.dropna(subset=['TARGET_SCORE'])
    
    portfolio_df['Weight'] = 1.0 / len(portfolio_df) # podzielic przez rozmiar wszytskich spółek
    portfolio_df['Initial_Investment'] = initial_cash * portfolio_df['Weight']
    
    total_value_year = 0
    
    for _, row in portfolio_df.iterrows():
        company_id = row['CompanyID']
        cash_in_company = row['Initial_Investment']
        
        try:
            mcap_previous = raw_df[(raw_df['CompanyID'] == company_id) & (raw_df['Year'] == year - 1)]['MarketCap'].values[0]
            mcap_current = raw_df[(raw_df['CompanyID'] == company_id) & (raw_df['Year'] == year)]['MarketCap'].values[0]
            
            current_value = cash_in_company * (mcap_current / mcap_previous) 
            # obecna wartosc firmy podzielić przez jej wartość rok temu
            # jesli curr > prev, to cash * (>1.0) - ZYSK
            # wpp cash * (<1.0) - STRATA
            total_value_year += current_value
        except:
            total_value_year += cash_in_company
            
    roi = (total_value_year - initial_cash) / initial_cash
    return roi, total_value_year


# JAK BEDZIESZ MIEC GOTOWY MODEL, TO ODKOMENTUJ WSZYSTKO CO ZWIĄZANE Z ML W DWÓCH FUNKCJACH PONIŻEJ !!!

def plot_comparison_bar_chart(year, bestPossible_res, hfs_res, pca_res): #, ml_res):
    strategies = ['TOP 3', 'TOP 10', 'TOP 30']
    
    best_scores = [bestPossible_res['top3'][0]*100, bestPossible_res['top10'][0]*100, bestPossible_res['top30'][0]*100]
    hfs_scores = [hfs_res['top3'][0]*100, hfs_res['top10'][0]*100, hfs_res['top30'][0]*100]
    pca_scores = [pca_res['top3'][0]*100, pca_res['top10'][0]*100, pca_res['top30'][0]*100]
    # ml_scores = [ml_res['top3'][0]*100, ml_res['top10'][0]*100, ml_res['top30'][0]*100]

    x = np.arange(len(strategies))
    
    width = 0.2
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - 1.5*width, best_scores, width, label='Best Possible', color='#2ca02c', edgecolor='black') # Zielony
    bars2 = ax.bar(x - 0.5*width, hfs_scores, width, label='HFS', color='#1f77b4', edgecolor='black')          # Niebieski
    bars3 = ax.bar(x + 0.5*width, pca_scores, width, label='PCA', color='#d62728', edgecolor='black')          # Czerwony
    # bars4 = ax.bar(x + 1.5*width, ml_scores, width, label='ML', color='#9467bd', edgecolor='black')            # Fioletowy

    ax.axhline(0, color='black', linewidth=1)

    ax.set_ylabel(f'Roczna Stopa Zwrotu w roku {year} (%)', fontsize=12)
    ax.set_title(f'Symulacja Inwestycyjna: Porównanie Modeli w roku {year}', fontsize=14, pad=20)
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
                        ha='center', va=va_dir, weight='bold', fontsize=9)

    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    # add_labels(bars4)

    # Dynamiczne limity osi Y z uwzględnieniem wszystkich wyników
    all_scores = best_scores + hfs_scores + pca_scores # + ml_scores
    plt.ylim(min(all_scores) * 1.3 if min(all_scores) < 0 else -5, max(all_scores) * 1.3 if max(all_scores) > 0 else 5)

    plt.tight_layout()
    plt.show()

def run_final_simulation(year):
    raw_df = get_data_from_csv('company_esg_financial_dataset.csv')
    
    bestPossible_df = pd.read_csv(LOCAL_FOLDER / r'ML_dataset\ML_dataset_merged.csv', sep=',')
    hfs_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data_HFS.csv', sep=',')
    pca_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data_PCA_RULES.csv', sep=',')
    # ml_df = pd.read_csv(LOCAL_FOLDER / 'scored_company_data_ML.csv', sep=',')
    
    bestPossible_top3, bestPossible_top10, bestPossible_top30, all_market = create_concentration_portfolios(bestPossible_df)
    hfs_top3, hfs_top10, hfs_top30, _ = create_concentration_portfolios(hfs_df)
    pca_top3, pca_top10, pca_top30, _ = create_concentration_portfolios(pca_df)
    # ml_top3, ml_top10, ml_top30, _ = create_concentration_portfolios(ml_df)


    # WYNIKI
    bestPossible_res = {
        'top3': calculate_returns_in_year(year, bestPossible_top3, raw_df),
        'top10': calculate_returns_in_year(year, bestPossible_top10, raw_df),
        'top30': calculate_returns_in_year(year, bestPossible_top30, raw_df)
    }

    hfs_res = {
        'top3': calculate_returns_in_year(year, hfs_top3, raw_df),
        'top10': calculate_returns_in_year(year, hfs_top10, raw_df),
        'top30': calculate_returns_in_year(year, hfs_top30, raw_df)
    }
    
    pca_res = {
        'top3': calculate_returns_in_year(year, pca_top3, raw_df),
        'top10': calculate_returns_in_year(year, pca_top10, raw_df),
        'top30': calculate_returns_in_year(year, pca_top30, raw_df)
    }

    # ml_res = {
    #     'top3': calculate_returns_in_year(year, ml_top3, raw_df),
    #     'top10': calculate_returns_in_year(year, ml_top10, raw_df),
    #     'top30': calculate_returns_in_year(year, ml_top30, raw_df)
    # }
    
    market_res = calculate_returns_in_year(year, all_market, raw_df)

    print("=" * 105)
    print("PORÓWNANIE MODELI: Best Possible vs HFS vs PCA") # vs ML
    print(f"Kapitał początkowy: 100,000 PLN | Zysk rynku: {market_res[1]-100000:,.2f} PLN ({market_res[0]*100:.2f}%)")
    print("=" * 105)
    
    print(f"{'Portfel':<10} | {'Best Possible':<20} | {'HFS':<20} | {'PCA':<20}") # | {'ML':<20}")
    print("-" * 105)
    
    # Funkcja pomocnicza do ładnego formatowania komórek konsoli (żeby kod poniżej był krótszy)
    def fmt(res_tuple):
        return f"{res_tuple[1] - 100000:>10,.2f} ({res_tuple[0]*100:>5.2f}%)"

    print(f"{'TOP 3':<10} | {fmt(bestPossible_res['top3']):<20} | {fmt(hfs_res['top3']):<20} | {fmt(pca_res['top3']):<20}") # | {fmt(ml_res['top3']):<20}")
    print(f"{'TOP 10':<10} | {fmt(bestPossible_res['top10']):<20} | {fmt(hfs_res['top10']):<20} | {fmt(pca_res['top10']):<20}") # | {fmt(ml_res['top10']):<20}")
    print(f"{'TOP 30':<10} | {fmt(bestPossible_res['top30']):<20} | {fmt(hfs_res['top30']):<20} | {fmt(pca_res['top30']):<20}") # | {fmt(ml_res['top30']):<20}")
    print("=" * 105)
    
    plot_comparison_bar_chart(year, bestPossible_res, hfs_res, pca_res) #, ml_res)

if __name__ == '__main__':
    run_final_simulation(2025)
