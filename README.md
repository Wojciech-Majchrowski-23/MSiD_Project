# MSiD_Project

## Collaborators:
- Karolewski Jakub
- Majchrowski Wojciech
- Wieczorek Alicja

---

## Repository Rules:

* **1 branch = 1 feature** (apply common sense, avoid over-fragmentation).
* **No direct pushes to `main`** – all changes must go through branches, which makes reverting errors much easier.
* **Branch naming convention:** `feature_name/action` (e.g., `algorithmA/fix`, `classB/update`).
* **Create local folder after cloning repo and call it `local_folder`.** Keep there your local files (e.g. dataset.txt).

---

## Zbiór Danych (Dataset)
W projekcie wykorzystujemy zbiór danych: **[ESG and Financial Performance Dataset](https://www.kaggle.com/datasets/shriyashjagtap/esg-and-financial-performance-dataset/data)** autorstwa Shriyash Jagtap. 

**Opis od twórcy:**
Zbiór ten symuluje wyniki finansowe i ESG (Environmental, Social, and Governance) 1000 globalnych firm z 9 branż i 7 regionów w latach 2015-2025. Zawiera realistyczne wskaźniki finansowe (np. przychody, marże zysku, kapitalizacja rynkowa) wraz z kompleksowymi wskaźnikami ESG, takimi jak emisja dwutlenku węgla, zużycie zasobów i szczegółowe oceny ESG.

### Zawartość zbioru danych:
| Nazwa kolumny | Opis kolumny |
|---|---|
| **CompanyID** | Unikalny identyfikator każdej firmy |
| **CompanyName** | Syntetyczna nazwa firmy |
| **Industry** | Sektor działalności (np. Finanse, Technologie) |
| **Region** | Region geograficzny |
| **Year** | Rok sprawozdawczy (2015–2025) |
| **Revenue** | Roczny przychód (w mln USD) |
| **ProfitMargin** | Marża zysku netto wyrażona w procentach |
| **MarketCap** | Kapitalizacja rynkowa (w mln USD) |
| **GrowthRate** | Procentowy wskaźnik wzrostu przychodów rok do roku |
| **ESG_Overall** | Ogólny wynik zrównoważonego rozwoju ESG (0–100) |
| **ESG_Environmental** | Ocena w kategorii zrównoważonego rozwoju środowiska (0–100) |
| **ESG_Social** | Ocena odpowiedzialności społecznej (0–100) |
| **ESG_Governance** | Ocena jakości zarządzania korporacyjnego (0–100) |
| **CarbonEmissions** | Roczna emisja dwutlenku węgla w tonach |
| **WaterUsage** | Roczne zużycie wody (w metrach sześciennych) |
| **EnergyConsumption** | Roczne zużycie energii (w MWh) |

**Z jakich kolumn korzystamy:**
Na potrzeby oceny inwestycyjnej i budowy modeli logiki rozmytej wykorzystaliśmy oraz poddaliśmy odpowiedniej agregacji główne kolumny, czyli: **Revenue, ProfitMargin, MarketCap, GrowthRate** oraz **ESG_Overall**. Posiłkowo (do wyliczeń modyfikatorów wyceny) wykorzystywany jest również zysk netto (**NetIncome**), wyliczany w sposób przedstawony w "Wyliczanych Metrykach Inwestycyjnych"

---

## 1. Agregacje Statystyczne (Sufiksy)
Ze względu na fakt, że dane wejściowe dla algorytmów zostały przekształcone z formatu wieloletniego (panelowego) do postaci zagregowanej (gdzie jeden wiersz reprezentuje całą historię danej spółki), wprowadzono niezbędne sufiksy oznaczające zastosowany model agregacji:

* **`[Nazwa]_WMA` (Weighted Moving Average - Średnia Ważona):** Średnia ważona wartości danego wskaźnika obliczona z całego analizowanego okresu historycznego. Metoda ta przypisuje większe wagi danym najnowszym, co pozwala na bardziej trafną ocenę obecnej kondycji firmy.
* **`[Nazwa]_std` (Standard Deviation - Odchylenie Standardowe):** Statystyczna miara zmienności i rozproszenia wyników firmy na przestrzeni analizowanych lat.
* **`[Nazwa]_cv` (Coefficient of Variation - Współczynnik Zmienności):** Stosunek odchylenia standardowego do średniej arytmetycznej. Pozwala na znormalizowane porównanie "szumu" i wahań wyników pomiędzy firmami o różnej wielkości operacyjnej.
* **`[Nazwa]_slope` (Slope - Wskaźnik Nachylenia Regresji Liniowej):** Pokazuje jednoznaczny kierunek oraz dynamikę trendu. Dodatni wynik wskazuje na historyczny trend wzrostowy dla danej metryki na przestrzeni badanego okresu.

### a) Rozkłady średnich ważonych podstawowych metryk spółek
![WMA_metrics_histograms](local_folder\Plots\WMA_metrics_histograms.png)

### b) Rozkłady tendencji podstawowych metryk spółek
![SLOPE_metrics_histograms](local_folder\Plots\SLOPE_metrics_histograms.png)

### c) Rozkłady współczynników zmienności podstawowych metryk spółek
![CV_metrics_histograms](local_folder\Plots\CV_metrics_histograms.png)

---

## 2. Wyliczane Metryki Inwestycyjne
Aby precyzyjnie odwzorować warunki rynkowe, na podstawie zagregowanych wartości, wyliczyliśmy autorskie, syntetyczne metryki służące jako wejście do modeli Fuzzy Logic.

* **`ProfitMargin_WMA`** *(Średnia Ważona Marża Zysku)*:
  * **Interpretacja:** Wyznacza ogólną zyskowność i wieloletnią efektywność operacyjną firmy po odliczeniu kosztów.
  * **Zasada w modelu:** Im **WYŻSZY** wynik metryki, tym lepsza firma.

* **`PriceToSales`** *(Wskaźnik Ceny do Przychodu - P/S)*:
  * **Wzór:** `MarketCap_mean / Revenue_mean`
  * **Interpretacja:** Obliczany jako stosunek kapitalizacji rynkowej do średnich ważonych przychodów firmy. Pozwala rynkowo ocenić czy dana firma jest relatywnie tania, czy znajduje się w bańce spekulacyjnej.
  * **Zasada w modelu:** Im **NIŻSZY** wynik metryki, tym lepsza firma.

  * **`NetIncome`** *(Szacowany Zysk Netto)*:
  * **Wzór:** `Revenue_mean * (ProfitMargin_mean / 100)`
  * **Interpretacja:** Przychody to tylko miara skali biznesu (ile pieniędzy przeszło przez firmę), a zysk netto to miara realnego sukcesu (ile pieniędzy fizycznie zostało w kasie po opłaceniu kosztów). Jest to absolutna podstawa do oceny zyskowności.

* **`EarningsYield`** *(Rentowność Zysków)*:
  * **Interpretacja:** Odwrotność wskaźnika P/E (Ceny do Zysku), liczona jako NetIncome / MarketCap_mean. Wskazuje procentową rentowność inwestycji. Spółki generujące straty przyjmują tu wartości ujemne, naturalnie spadając na dół skali.
  * **Zasada w modelu:** Im **WYŻSZY** wynik metryki, tym lepsza firma.

* **`Risk-AdjustedGrowth`** *(Wzrost Skorygowany o Ryzyko)*:
  * **Wzór:** `GrowthRate_mean / GrowthRate_std`
  * **Interpretacja:** Miernik wyliczany jako stosunek średniego tempa wzrostu do odchylenia standardowego tego wzrostu. Premiuje spółki, których rozwój jest wysoce przewidywalny i systematyczny, jednocześnie karząc te, które rosną chaotycznie (wysokie ryzyko inwestycyjne).
  * **Zasada w modelu:** Im **WYŻSZY** wynik metryki, tym lepsza firma.

* **`Earnings-to-Growth`** *(Zmodyfikowany PEG Ratio)*:
  * **Interpretacja:** Syntetyczne zestawienie, w którym wycena P/E firmy zderza się ze wzrostem skorygowanym o ryzyko. Odpowiada na pytanie: "Ile płacimy za bezpieczny wzrost spółki?".
  * **Zasada w modelu:** Im **NIŻSZY** wynik metryki, tym lepsza firma. 
  * *UWAGA (Poprawka analityczna):* Dla firm posiadających ujemny zysk netto (stratę) lub ujemny współczynnik wzrostu, algorytm nadaje z góry narzuconą, olbrzymią karę (maksymalną na osi X). Zabezpiecza to system przed "pułapką podwójnego minusa" – w przeciwnym razie dzielenie dwóch ujemnych wartości dałoby niską wartość dodatnią, sprawiając, że deficytowa i kurcząca się spółka wydawałaby się świetną okazją.

* **`ESG_Signal-to-Noise`** *(Wskaźnik Sygnału do Szumu dla ESG)*:
  * **Interpretacja:** Dynamika i stabilność poprawy standardów zrównoważonego rozwoju. Obliczany przez podzielenie wskaźnika "slope" (siła poprawy polityki ESG) przez współczynnik zmienności "cv" (szum/chaos). Wskaźnik ten wyłapuje "greenwashing", uderzając w firmy o pozornie dobrych, lecz szarpanych standardach.
  * **Zasada w modelu:** Im **WYŻSZY** wynik metryki, tym lepsza firma.

### d) Rozkłady wyliczonych metryk spółek
![CALCULATED_metrics_histograms](local_folder\Plots\CALC_metrics_histograms.png)

---

## 3. Zastosowane Podejścia: Fuzzy Logic

Podczas oceny atrakcyjności przetestowaliśmy i porównaliśmy dwa oddzielne systemy logiki rozmytej.

### Podejście 1: Model Zredukowany, 3-czynnikowy (`fuzzy_rules_27.ipynb`)
System oparty jest o 3 wejścia silnie nieskorelowanych metryk kompozytowych: `EarningsYield`, `Risk-AdjustedGrowth` oraz `ESG_Signal-to-Noise`.
* Zastosowano pełną, ujednoliconą spójność wejść: dla każdej zmiennej system czyta "im wyższa liczba, tym wyższa jakość". 
* Udało się bez problemu zdefiniować klasyczną bazę wiedzy z precyzyjnie rozpisanymi **27 regułami**, co zapewnia przejrzystość logiczną bez obciążania systemu klątwą wymiarowości. Ostateczny wynik płynnie uśrednia ocenę z 3 kategorii jakościowych spółki.

### Podejście 2: Model Zaawansowany i Wielokryterialny (`fuzzy_rules.ipynb`)
Bardziej złożona architektura, korzystająca z **4 zmiennych** o zróżnicowanych kierunkach logicznych: `Earnings-to-Growth` (waga decyzyjna 3, im mniej tym lepiej), `ESG_Signal-to-Noise` (waga 2, im więcej tym lepiej), `PriceToSales` (waga 2, im mniej tym lepiej) i pomocniczego modyfikatora marży `ProfitMargin_WMA` (waga 1, im więcej tym lepiej). 
* Ręczne wypisywanie 625 reguł dla tej architektury mogłoby skutkować *Rule Explosion*. Wdrożono kompresję bazy wiedzy, redukując reguły z użyciem logicznych spójników `OR` oraz pomijaniem skrajnych modyfikatorów w "pewnych" przypadkach inwestycyjnych (technika tzw. *Don't Care states*). 
* Zmienne typu `PriceToSales` i `ETG` przeszły "odwrócenie osi" na macierzach Gaussa (najniższe wartości liczbowe są mapowane na trójkąty High/Very High), a odpowiedni preprocessing danych ucina szum z niedziałających biznesów przed wejściem w sam system.

---