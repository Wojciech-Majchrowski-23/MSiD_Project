import tkinter as tk
from tkinter import ttk, messagebox
from utils_gui import load_raw_data, get_unique_companies, calculate_custom_portfolio_returns

class InvestmentSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator Portfela Inwestycyjnego")
        self.root.geometry("650x750")
        
        # Inicjalizacja danych bazowych
        try:
            self.raw_df = load_raw_data()
            self.company_list = get_unique_companies(self.raw_df)
        except Exception as e:
            messagebox.showerror("Błąd danych", f"Nie udało się załadować bazy: {e}")
            self.raw_df = None
            self.company_list = []
            
        self.portfolio_rows = []
        self.setup_ui()

    def setup_ui(self):
        # --- Ramka górna (konfiguracja podstawowa) ---
        config_frame = ttk.LabelFrame(self.root, text="Podstawowe dane symulacji", padding=(10, 10))
        config_frame.pack(fill="x", padx=10, pady=10)

        # Rok inwestycji (2015-2024)
        ttk.Label(config_frame, text="Rok inwestycji:").grid(row=0, column=0, sticky="w", pady=5)
        self.year_var = tk.StringVar(value="2023")
        self.year_cb = ttk.Combobox(config_frame, textvariable=self.year_var, values=[str(y) for y in range(2015, 2025)], state="readonly", width=15)
        self.year_cb.grid(row=0, column=1, padx=10, pady=5)

        # Budżet
        ttk.Label(config_frame, text="Budżet (PLN):").grid(row=1, column=0, sticky="w", pady=5)
        self.budget_var = tk.StringVar(value="100000")
        ttk.Entry(config_frame, textvariable=self.budget_var, width=18).grid(row=1, column=1, padx=10, pady=5)

        # Liczba spółek
        ttk.Label(config_frame, text="Liczba spółek w portfelu:").grid(row=2, column=0, sticky="w", pady=5)
        self.num_companies_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.num_companies_var, width=18).grid(row=2, column=1, padx=10, pady=5)

        # Przycisk generowania
        ttk.Button(config_frame, text="Generuj formularz spółek", command=self.generate_portfolio_fields).grid(row=3, column=0, columnspan=2, pady=10)

        # --- Ramka środkowa ze scrollowaniem (Lista spółek) ---
        self.canvas_frame = ttk.LabelFrame(self.root, text="Konfiguracja Spółek", padding=(5, 5))
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Ramka dolna (Akcje główne) ---
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=15)

        ttk.Button(action_frame, text="Divide equally (Rozdziel po równo)", command=self.divide_equally).pack(side="left", padx=5)
        ttk.Button(action_frame, text="INWESTUJ!", command=self.run_simulation, style="Accent.TButton").pack(side="right", padx=5)

    def generate_portfolio_fields(self):
        """Generuje odpowiednią liczbę wierszy z wyborem spółki i kwotą."""
        # Wyczyść poprzednią listę
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

        # Nagłówki kolumn dynamicznych
        ttk.Label(self.scrollable_frame, text="#").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.scrollable_frame, text="Nazwa spółki").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.scrollable_frame, text="Kwota (PLN)").grid(row=0, column=2, padx=5, pady=5)

        # Generowanie n wierszy
        for i in range(n_companies):
            ttk.Label(self.scrollable_frame, text=f"{i+1}.").grid(row=i+1, column=0, padx=5, pady=5)
            
            cb = ttk.Combobox(self.scrollable_frame, values=self.company_list, state="readonly", width=35)
            cb.grid(row=i+1, column=1, padx=5, pady=5)
            
            amt_entry = ttk.Entry(self.scrollable_frame, width=15)
            amt_entry.grid(row=i+1, column=2, padx=5, pady=5)
            
            self.portfolio_rows.append({"company_cb": cb, "amount_entry": amt_entry})

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
        """Zebiera dane wejściowe z GUI i wysyła je do kalkulatora backendu."""
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

        # Weryfikacja czy użytkownik przekroczył budżet 
        if total_assigned > expected_budget + 0.01:
            messagebox.showwarning("Przekroczony budżet!", 
                                   f"Suma przypisanych kwot ({total_assigned:.2f}) jest większa niż Twój budżet ({expected_budget:.2f}).")
            return

        # Obliczenie wyników w module backendowym
        roi, final_value, details = calculate_custom_portfolio_returns(portfolio_data, self.raw_df, invest_year)

        # Wyświetlenie formatowanych wyników
        self.show_results(invest_year, total_assigned, final_value, roi, details)

    def show_results(self, year, initial, final, roi, details):
        """Wyświetla nowe okno ze szczegółowymi wynikami inwestycji."""
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Wyniki inwestycji (Rok bazowy: {year})")
        result_window.geometry("450x300")
        
        profit_pln = final - initial
        profit_color = "green" if profit_pln >= 0 else "red"
        
        ttk.Label(result_window, text="PODSUMOWANIE", font=("Arial", 12, "bold")).pack(pady=10)
        
        summary_text = (
            f"Zainwestowany kapitał: {initial:,.2f} PLN\n"
            f"Wartość na koniec roku {year + 1}: {final:,.2f} PLN\n"
        )
        ttk.Label(result_window, text=summary_text, justify="center").pack()
        
        roi_label = tk.Label(result_window, text=f"Zysk/Strata: {profit_pln:,.2f} PLN ({roi*100:.2f}%)", 
                             fg=profit_color, font=("Arial", 11, "bold"))
        roi_label.pack(pady=5)
        
        ttk.Separator(result_window, orient='horizontal').pack(fill='x', pady=10, padx=20)
        ttk.Button(result_window, text="Zamknij", command=result_window.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Dodanie drobnego, nieobowiązkowego stylu pod główne przyciski
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure("Accent.TButton", font=('Arial', 10, 'bold'), foreground='darkgreen')
    
    app = InvestmentSimulatorGUI(root)
    root.mainloop()