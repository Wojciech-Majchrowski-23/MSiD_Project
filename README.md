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
* **Create local folder after cloning repo and call it `local_folder`. Keep there your local files (e.g. dataset.txt)

# Słownik Danych: Interpretacja Atrybutów Spółek (ESG & Financials)

Poniższy dokument opisuje znaczenie poszczególnych zmiennych (kolumn) w zagregowanym zbiorze danych wejściowych. Zbiór ten stanowi podstawę do budowy systemów oceny atrakcyjności inwestycyjnej w oparciu o Logikę Rozmytą (Fuzzy Logic) oraz modele Uczenia Maszynowego (Machine Learning).

---

## 1. Agregacje Statystyczne (Sufiksy)
Z uwagi na to, że dane wejściowe dla algorytmów zostały przekształcone z formatu wieloletniego (panelowego) do postaci zagregowanej (jeden wiersz reprezentujący całą historię danej spółki), nazwy atrybutów zostały wzbogacone o odpowiednie sufiksy:

* **`[Nazwa]_mean` (Średnia):** * Średnia wartość danego wskaźnika obliczona z całego analizowanego okresu historycznego (np. 5 lat). Reprezentuje ogólny, uśredniony poziom firmy.
* **`[Nazwa]_std` (Odchylenie standardowe):** * Klasyczna miara rozrzutu pokazująca, jak bardzo w poszczególnych latach wartości odchylały się od średniej.
* **`[Nazwa]_cv` (Współczynnik Zmienności - *Coefficient of Variation*):** * Obliczony jako stosunek odchylenia standardowego do średniej (`std / mean`). 
  * **Interpretacja biznesowa:** Jest to absolutnie kluczowa miara **ryzyka i stabilności**. 
    * **Niskie CV (bliskie 0):** Wskazuje, że dany parametr (np. przychody) jest niezwykle stabilny i przewidywalny z roku na rok.
    * **Wysokie CV:** Oznacza duże wahania, brak stabilności i wyższe ryzyko inwestycyjne.

---

## 2. Wskaźniki Finansowe i Skali Biznesu
Zmienne opisujące kondycję ekonomiczną i wielkość przedsiębiorstwa.

* **`Revenue`** *(Przychody)*: 
  * Całkowita kwota wygenerowana ze sprzedaży towarów lub usług. 
  * Wskazuje na skalę działalności operacyjnej.
* **`MarketCap`** *(Kapitalizacja rynkowa)*: 
  * Aktualna wartość giełdowa całej firmy (cena pojedynczej akcji pomnożona przez liczbę wyemitowanych akcji). 
  * Służy do klasyfikacji wielkości (np. *Small-cap*, *Large-cap*).
* **`ProfitMargin`** *(Marża zysku)*: 
  * Wyrażona w procentach. Określa, jaka część przychodów pozostaje w firmie jako zysk netto po odliczeniu kosztów.
  * **Interpretacja:** Kluczowy wskaźnik rentowności. Wyższa marża oznacza bardziej dochodowy i bezpieczny biznes.
* **`GrowthRate`** *(Tempo wzrostu)*: 
  * Procentowy wzrost przychodów rok do roku (YoY). 
  * **Interpretacja:** Miernik dynamiki rozwoju i potencjału ekspansji.

  GrowthRate nie należy traktować jako tendencji całkowitej (można traktować tylko jako tendencję finansową), ponieważ nie uwzględia ESG.

  Można dorobić tutaj współczynnik nachylenia regresji (a > 0 - tendencja wzrostowa)

---

## 3. Wskaźniki ESG (Zrównoważony Rozwój)
Zmienne wyrażane w skali punktowej (zazwyczaj 0-100), oceniające niefinansowe aspekty działalności. **Wyższy wynik jest zawsze korzystniejszy.**

* **`ESG_Overall`**: 
  * Zbiorcza, uśredniona ocena "odpowiedzialności" firmy.
* **`ESG_Environmental`** *(Środowisko - E)*: 
  * Ocena wpływu na naturę. Punktuje działania takie jak: wykorzystanie energii odnawialnej, redukcja śladu węglowego i gospodarka obiegu zamkniętego.
* **`ESG_Social`** *(Społeczeństwo - S)*: 
  * Ocena relacji społecznych. Punktuje: warunki pracy (BHP), równość i różnorodność, relacje ze związkami zawodowymi oraz wpływ na społeczności lokalne.
* **`ESG_Governance`** *(Ład korporacyjny - G)*: 
  * Ocena struktury i etyki zarządzania. Punktuje: przejrzystość finansową, brak korupcji, niezależność zarządu oraz poszanowanie praw mniejszościowych akcjonariuszy.

---

## 4. Bezwzględne Wskaźniki Środowiskowe
Surowe dane ilościowe dotyczące zużycia zasobów i emisji. 

> **Uwaga analityczna:** Wskaźniki te są silnie skorelowane z rozmiarem firmy (większa korporacja naturalnie zużywa więcej). W modelowaniu często ocenia się je w relacji do przychodów (np. `CarbonEmissions` / `Revenue`).

* **`CarbonEmissions`** *(Emisje dwutlenku węgla)*: 
  * Ilość wyemitowanych gazów cieplarnianych, zazwyczaj wyrażona w tonach (ekwiwalent CO2).
* **`WaterUsage`** *(Zużycie wody)*: 
  * Całkowite zużycie wody, zazwyczaj w metrach sześciennych. Krytyczny wskaźnik dla branż takich jak rolnictwo, produkcja napojów czy przemysł odzieżowy.
* **`EnergyConsumption`** *(Zużycie energii)*: 
  * Łączna energia (np. w gigadżulach) wykorzystana do prowadzenia operacji biznesowych i produkcyjnych.