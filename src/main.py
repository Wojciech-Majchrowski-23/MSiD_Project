import pandas as pd
import numpy as np
import skfuzzy as fuzz
from pathlib import Path
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

LOCAL_FOLDER = Path(__file__).parent.parent / "local_folder"

def create_fuzzy_system():
    # Ryzyko (na podstawie Risk-AdjustedGrowth) - im wyższy RAG, tym NIŻSZE ryzyko
    ryzyko = ctrl.Antecedent(np.arange(0, 3.1, 0.1), 'ryzyko')
    # Zysk (na podstawie Earnings-to-Growth / PEG) - celujemy w okolice 1.0
    zysk = ctrl.Antecedent(np.arange(0, 51, 1), 'zysk')
    # ESG (ESG_Overall_mean)
    esg = ctrl.Antecedent(np.arange(0, 101, 1), 'esg')
    
    # Wyjście: Ocena końcowa
    ocena = ctrl.Consequent(np.arange(0, 101, 1), 'ocena')

    ryzyko['wysokie'] = fuzz.trapmf(ryzyko.universe, [0, 0, 0.3, 0.7])
    ryzyko['srednie'] = fuzz.trimf(ryzyko.universe, [0.5, 1.0, 1.5])
    ryzyko['niskie'] = fuzz.trapmf(ryzyko.universe, [1.2, 1.8, 3.0, 3.0])

    zysk['wysoki'] = fuzz.trapmf(zysk.universe, [0, 0, 8, 15])
    zysk['sredni'] = fuzz.trimf(zysk.universe, [10, 20, 35])
    zysk['niski'] = fuzz.trapmf(zysk.universe, [25, 40, 50, 50])

    esg['niskie'] = fuzz.trapmf(esg.universe, [0, 0, 35, 45])
    esg['srednie'] = fuzz.trimf(esg.universe, [40, 55, 70])
    esg['wysokie'] = fuzz.trapmf(esg.universe, [65, 80, 100, 100])

    ocena['bardzo_slaba'] = fuzz.trimf(ocena.universe, [0, 0, 25])
    ocena['slaba'] = fuzz.trimf(ocena.universe, [20, 35, 50])
    ocena['przecietna'] = fuzz.trimf(ocena.universe, [45, 55, 65])
    ocena['dobra'] = fuzz.trimf(ocena.universe, [60, 75, 85])
    ocena['swietna'] = fuzz.trimf(ocena.universe, [80, 100, 100])

    rules = [
        ctrl.Rule(ryzyko['niskie'] & zysk['wysoki'] & esg['wysokie'], ocena['swietna']),
        ctrl.Rule(ryzyko['niskie'] & zysk['wysoki'] & esg['srednie'], ocena['swietna']),
        ctrl.Rule(ryzyko['srednie'] & zysk['wysoki'] & esg['wysokie'], ocena['dobra']),
        ctrl.Rule(ryzyko['niskie'] & zysk['sredni'] & esg['wysokie'], ocena['dobra']),
        ctrl.Rule(ryzyko['srednie'] & zysk['sredni'] & esg['srednie'], ocena['przecietna']),
        ctrl.Rule(ryzyko['wysokie'] & zysk['wysoki'] & esg['wysokie'], ocena['przecietna']),
        ctrl.Rule(zysk['niski'], ocena['slaba']),
        ctrl.Rule(ryzyko['wysokie'] & zysk['niski'], ocena['bardzo_slaba']),
        ctrl.Rule(ryzyko['wysokie'] & esg['niskie'], ocena['bardzo_slaba']),
        ctrl.Rule(esg['niskie'] & zysk['sredni'], ocena['slaba'])
    ]

    scoring_ctrl = ctrl.ControlSystem(rules)
    
    fig, axes = plt.subplots(2, 2, figsize=(6, 4))

    for label in ryzyko.terms:
        axes[0, 0].plot(ryzyko.universe, ryzyko[label].mf, label=label)
    axes[0, 0].set_title("Ryzyko (RAG)", fontsize=10)
    axes[0, 0].legend(fontsize=7)

    for label in zysk.terms:
        axes[0, 1].plot(zysk.universe, zysk[label].mf, label=label)
    axes[0, 1].set_title("Zysk (PEG)", fontsize=10)
    axes[0, 1].legend(fontsize=7)

    for label in esg.terms:
        axes[1, 0].plot(esg.universe, esg[label].mf, label=label)
    axes[1, 0].set_title("ESG", fontsize=10)
    axes[1, 0].legend(fontsize=7)

    for label in ocena.terms:
        axes[1, 1].plot(ocena.universe, ocena[label].mf, label=label)
    axes[1, 1].set_title("Ocena Końcowa", fontsize=10)
    axes[1, 1].legend(fontsize=7, loc='upper left')

    plt.tight_layout() 
    plt.show()

    return ctrl.ControlSystemSimulation(scoring_ctrl)

def main():
    try:
        df = pd.read_csv(LOCAL_FOLDER / 'aggregated_company_data.csv')
    except FileNotFoundError:
        print("Błąd: Nie znaleziono pliku aggregated_company_data.csv")
        return

    system = create_fuzzy_system()
    results = []

    for index, row in df.iterrows():
        try:
            rag = np.clip(row['Risk-AdjustedGrowth'], 0, 3) 
            peg = np.clip(row['Earnings-to-Growth'], 0, 50) 
            esg_val = np.clip(row['ESG_Overall_mean'], 0, 100)

            system.input['ryzyko'] = rag
            system.input['zysk'] = peg
            system.input['esg'] = esg_val

            system.compute()
            score = system.output['ocena']
            results.append(round(score, 2))
        except Exception as e:
            results.append(np.nan)

    df['Final_Score'] = results
    df.to_csv(LOCAL_FOLDER / 'company_scored_results.csv', index=False)
    print("Sukces! Wyniki zostały zapisane do pliku company_scored_results.csv")

if __name__ == "__main__":
    main()