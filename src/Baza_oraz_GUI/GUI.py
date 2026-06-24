import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Baza_oraz_GUI.utils_gui import load_raw_data, get_unique_companies, calculate_custom_portfolio_returns
import sys

class InvestmentSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator Portfela Inwestycyjnego z Analizą Historyczną")

        try:
            self.root.state('zoomed')  # Standard dla Windows
        except tk.TclError:
            self.root.attributes('-zoomed', True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.option_add("*TCombobox*Listbox.font", ("Arial", 14))
        
        try:
            self.raw_df = load_raw_data()
            self.company_list = get_unique_companies(self.raw_df)
        except Exception as e:
            messagebox.showerror("Błąd danych", f"Nie udało się załadować bazy surowej: {e}")
            self.raw_df = None
            self.company_list = []
            
        try:
            LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"
            hist_path = LOCAL_FOLDER / "company_esg_financial_dataset.csv"
            if not hist_path.exists():
                hist_path = Path("company_esg_financial_dataset.csv")
                
            self.history_df = pd.read_csv(hist_path)
        except Exception as e:
            messagebox.showwarning("Błąd danych historycznych", f"Nie znaleziono 'company_esg_financial_dataset.csv': {e}")
            self.history_df = None

        self.current_selected_company = None
        self.portfolio_rows = []
        self.setup_ui()

    def setup_ui(self):
        # Główny kontener dzielący okno na lewą i prawą stronę
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)

        # --- LEWA STRONA (Formularz i konfiguracja portfela) ---
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        # --- PRAWA STRONA (Dynamiczne wykresy historyczne) ---
        self.right_frame = ttk.LabelFrame(main_container, text="Historyczna analiza metryk spółki (od 2016 r.)",  padding=(10, 10))
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.fig, self.axes = plt.subplots(3, 2, figsize=(7, 7))
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        for ax in self.axes.flat:
            ax.text(0.5, 0.5, "Wybierz spółkę z listy\naby zobaczyć historię", ha='center', va='center', color='gray')
            ax.grid(True, linestyle='--', alpha=0.5)
        self.fig.tight_layout()

        # --- Ramka górna (wewnątrz left_frame) ---
        config_frame = ttk.LabelFrame(left_frame, text="Podstawowe dane symulacji", padding=(10, 10))
        config_frame.pack(fill="x", padx=5, pady=5)

        # Rok inwestycji
        ttk.Label(config_frame, text="Rok inwestycji:", font = ("Arial", 18)).grid(row=0, column=0, sticky="w", pady=5)
        self.year_var = tk.StringVar(value="2023")
        self.year_cb = ttk.Combobox(config_frame, textvariable=self.year_var, values=[str(y) for y in range(2015, 2025)], state="readonly", width=15, font = ("Arial", 18))
        self.year_cb.grid(row=0, column=1, padx=10, pady=5)
        # Zmiana roku również powinna odświeżyć wykres
        self.year_cb.bind("<<ComboboxSelected>>", self.on_year_changed)

        ttk.Label(config_frame, text="Budżet (PLN):", font = ("Arial", 18)).grid(row=1, column=0, sticky="w", pady=5)
        self.budget_var = tk.StringVar(value="100000")
        ttk.Entry(config_frame, textvariable=self.budget_var, width=18, font = ("Arial", 18)).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(config_frame, text="Liczba spółek w portfelu:", font = ("Arial", 18)).grid(row=2, column=0, sticky="w", pady=5)
        self.num_companies_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.num_companies_var, width=18, font = ("Arial", 18)).grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(config_frame, text="Generuj formularz spółek", command=self.generate_portfolio_fields).grid(row=3, column=0, columnspan=2, pady=10)

        # --- Ramka środkowa ze scrollowaniem (wewnątrz left_frame) ---
        self.canvas_frame = ttk.LabelFrame(left_frame, text="Konfiguracja Spółek", padding=(5, 5))
        self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, borderwidth=0, highlightthickness=0, width=420)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Ramka dolna (wewnątrz left_frame) ---
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill="x", padx=5, pady=15)

        ttk.Button(action_frame, text="Divide equally", command=self.divide_equally).pack(side="left", padx=5)
        ttk.Button(action_frame, text="INVEST", command=self.run_simulation, style="Accent.TButton").pack(side="right", padx=5)

    def generate_portfolio_fields(self):
        """Generuje odpowiednią liczbę wierszy z wyborem spółki i kwotą."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.portfolio_rows.clear()

        try:
            n_companies = int(self.num_companies_var.get())
            if n_companies <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd wejścia", "Liczba spółek musi być liczbą całkowitą większą od zera.")
            return

        ttk.Label(self.scrollable_frame, text="#", font = ("Arial", 14)).grid(row=0, column=0, padx=3, pady=3)
        ttk.Label(self.scrollable_frame, text="Nazwa spółki", font = ("Arial", 14)).grid(row=0, column=1, padx=3, pady=3)
        ttk.Label(self.scrollable_frame, text="Kwota (PLN)", font = ("Arial", 14)).grid(row=0, column=2, padx=3, pady=3)

        for i in range(n_companies):
            ttk.Label(self.scrollable_frame, text=f"{i+1}.", font = ("Arial", 16)).grid(row=i+1, column=0, padx=3, pady=3)
            
            cb = ttk.Combobox(self.scrollable_frame, values=self.company_list, state="readonly", width=20, font = ("Arial", 16))
            cb.grid(row=i+1, column=1, padx=3, pady=3)
            # Podpinamy akcję kliknięcia / wyboru spółki pod rysowanie wykresu
            cb.bind("<<ComboboxSelected>>", self.on_company_selected)
            
            amt_entry = ttk.Entry(self.scrollable_frame, width=16, font = ("Arial", 16))
            amt_entry.grid(row=i+1, column=2, padx=3, pady=3)
            
            self.portfolio_rows.append({"company_cb": cb, "amount_entry": amt_entry})

    def on_company_selected(self, event):
        """Wywoływane automatycznie przy wyborze firmy z dowolnego Comboboxa."""
        selected_company = event.widget.get()
        if selected_company:
            self.current_selected_company = selected_company
            self.update_charts(selected_company)

    def on_year_changed(self, event):
        """Wywoływane przy zmianie roku inwestycji w panelu głównym."""
        if self.current_selected_company:
            self.update_charts(self.current_selected_company)

    def update_charts(self, company_name):
        """Filtruje dane historyczne i aktualizuje wykresy."""
        if self.history_df is None:
            return

        try:
            max_year = int(self.year_var.get())
        except ValueError:
            max_year = 2024

        # Rozpoznanie nazw kolumn dla elastyczności
        comp_col = 'CompanyName' if 'CompanyName' in self.history_df.columns else self.history_df.columns[0]
        year_col = 'Year' if 'Year' in self.history_df.columns else 'year'

        # Filtrowanie danych: od roku 2016 do wybranego roku inwestycji
        df_filtered = self.history_df[
            (self.history_df[comp_col] == company_name) & 
            (self.history_df[year_col] >= 2016) & 
            (self.history_df[year_col] <= max_year)
        ].sort_values(by=year_col)

        # Wyczyszczenie poprzednich wykresów
        for ax in self.axes.flat:
            ax.clear()

        metrics = ['Revenue', 'ProfitMargin', 'MarketCap', 'GrowthRate', 'ESG_Overall']
        titles = ['Revenue', 'ProfitMargin', 'MarketCap', 'GrowthRate', 'ESG_Overall']

        for i, metric in enumerate(metrics):
            row = i // 2
            col = i % 2
            ax = self.axes[row, col]
            ax.grid(True, linestyle='--', alpha=0.5)

            if df_filtered.empty:
                ax.text(0.5, 0.5, "Brak danych w tym przedziale", ha='center', va='center', fontsize=8, color='red')
                continue

            if metric in df_filtered.columns:
                ax.plot(df_filtered[year_col], df_filtered[metric], marker='o', color='#1f77b4', linewidth=2, markersize=4)
                ax.set_title(titles[i], fontsize=9, fontweight='bold')
                ax.set_xticks(df_filtered[year_col].unique())
                ax.tick_params(axis='both', labelsize=8)
            else:
                ax.text(0.5, 0.5, f"Brak metryki:\n{metric}", ha='center', va='center', fontsize=8, color='orange')

        self.fig.suptitle(f"Historia metryk dla: {company_name} (2016-{max_year})", fontsize=11, fontweight='bold', color='#0f4c81')
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        self.plot_canvas.draw()

    def divide_equally(self):
        """Dzieli zadeklarowany budżet równo między wygenerowane pola firm."""
        if not self.portfolio_rows:
            messagebox.showinfo("Informacja", "Najpierw wygeneruj formularz spółek.")
            return

        try:
            budget = float(self.budget_var.get())
        except ValueError:
            messagebox.showwarning("Błąd", "Budżet musi być wartością liczbową.")
            return

        n = len(self.portfolio_rows)
        equal_amount = round(budget / n, 2)

        for row_dict in self.portfolio_rows:
            entry = row_dict["amount_entry"]
            entry.delete(0, tk.END)
            entry.insert(0, str(equal_amount))

    def run_simulation(self):
        """Zbiera dane wejściowe z GUI i wysyła je do kalkulatora backendu."""
        if self.raw_df is None:
            messagebox.showerror("Błąd krytyczny", "Brak danych bazy do symulacji.")
            return

        if not self.portfolio_rows:
            messagebox.showwarning("Błąd", "Musisz wygenerować listę spółek i wpisać kwoty przed inwestycją.")
            return

        try:
            invest_year = int(self.year_var.get())
            expected_budget = float(self.budget_var.get())
        except ValueError:
            messagebox.showwarning("Błąd", "Sprawdź poprawność wpisanego roku i budżetu.")
            return

        portfolio_data = []
        total_assigned = 0.0

        for idx, row_dict in enumerate(self.portfolio_rows, start=1):
            comp_name = row_dict["company_cb"].get()
            amt_str = row_dict["amount_entry"].get()

            if not comp_name:
                messagebox.showwarning("Błąd", f"Nie wybrano nazwy spółki w wierszu {idx}.")
                return
            
            try:
                amt = float(amt_str)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Błąd", f"Niepoprawna kwota inwestycji w wierszu {idx}. Podaj liczbę większą od zera.")
                return

            total_assigned += amt
            portfolio_data.append({"name": comp_name, "amount": amt})

        if total_assigned > expected_budget + 0.01:
            messagebox.showwarning("Przekroczony budżet!", 
                                   f"Suma przypisanych kwot ({total_assigned:.2f}) jest większa niż Twój budżet ({expected_budget:.2f}).")
            return

        roi, final_value, details = calculate_custom_portfolio_returns(portfolio_data, self.raw_df, invest_year)
        self.show_results(invest_year, total_assigned, final_value, roi, details)

    def show_results(self, year, initial, final, roi, details):
        """Wyświetla nowe okno ze szczegółowymi wynikami inwestycji."""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Wyniki inwestycji (Rok bazowy: {year})")
        
        window_width = 600
        window_height = 300

        screen_width = result_window.winfo_screenwidth()
        screen_height = result_window.winfo_screenheight()
        
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        result_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        profit_pln = final - initial
        profit_color = "green" if profit_pln >= 0 else "red"
        
        ttk.Label(result_window, text="PODSUMOWANIE", font=("Arial", 22, "bold")).pack(pady=10)
        
        summary_text = (
            f"Zainwestowany kapitał: {initial:,.2f} PLN\n"
            f"Wartość na koniec roku {year + 1}: {final:,.2f} PLN\n"
        )
        ttk.Label(result_window, text=summary_text, justify="center", font=("Arial", 18)).pack()
        
        roi_label = tk.Label(result_window, text=f"Zysk/Strata: {profit_pln:,.2f} PLN ({roi*100:.2f}%)", 
                             fg=profit_color, font=("Arial", 22, "bold"))
        roi_label.pack(pady=5)
        
        ttk.Separator(result_window, orient='horizontal').pack(fill='x', pady=10, padx=20)
        ttk.Button(result_window, text="Zamknij", command=result_window.destroy).pack(pady=10)

    def on_closing(self):
        """Bezpieczne zamykanie aplikacji, czyszczenie pamięci i odblokowanie terminala."""
        # 1. Zamyka wszystkie aktywne figury Matplotlib
        plt.close('all')
        
        # 2. Zatrzymuje pętlę Tkinter i niszczy główne okno
        self.root.quit()
        self.root.destroy()
        
        # 3. Definitywnie kończy proces Pythona
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    
    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure("TButton", font = ('Arial', 14, 'bold'))
    style.configure("Accent.TButton", font = ('Arial', 18, 'bold'), foreground='darkgreen')
    style.configure("TLabelframe.Label", font = ('Arial', 16, 'bold', 'italic'), foreground='#333333')

    
    app = InvestmentSimulatorGUI(root)
    root.mainloop()