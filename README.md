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

* **`[Nazwa]_WMA` (Średnia WAŻONA):** * Średnia ważona wartości danego wskaźnika obliczona z całego analizowanego okresu historycznego (np. 5 lat). Reprezentuje ogólny, uśredniony poziom firmy.
* **`[Nazwa]_std` (Odchylenie standardowe):** * Klasyczna miara rozrzutu pokazująca, jak bardzo w poszczególnych latach wartości odchylały się od średniej.
* **`[Nazwa]_cv` (Współczynnik Zmienności - *Coefficient of Variation*):** * Obliczony jako stosunek odchylenia standardowego do średniej (`std / WMA`). 
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
Zmienne wyrażane w skali punktowej (zazwyczaj 0-100), oceniające niefinansowe aspekty działalności (environment, social, governance). **Wyższy wynik jest zawsze korzystniejszy.**

* **`ESG_Overall`**: 
  * Zbiorcza, uśredniona ocena "odpowiedzialności" firmy.

---

## 4. Wyliczone Metryki Rynkowe i Wyceny (Dodatkowe)
Poniższe zmienne nie pochodzą bezpośrednio z surowych danych, lecz zostały wyliczone na etapie inżynierii cech (Feature Engineering), aby dostarczyć modelom głębszych informacji o rentowności i wycenie rynkowej spółek.

* **`PriceToSales`** *(Wskaźnik P/S - Cena do Przychodu)*:
  * **Wzór:** `MarketCap_mean / Revenue_mean`
  * **Interpretacja:** Wskaźnik określa, ile inwestorzy płacą za każdego dolara przychodów generowanych przez firmę. Niskie wartości mogą sugerować, że spółka jest niedowartościowana (tania okazja), podczas gdy bardzo wysokie wartości często cechują popularne spółki technologiczne (oczekiwanie na potężny wzrost w przyszłości).

* **`NetIncome`** *(Szacowany Zysk Netto)*:
  * **Wzór:** `Revenue_mean * (ProfitMargin_mean / 100)`
  * **Interpretacja:** Przychody to tylko miara skali biznesu (ile pieniędzy przeszło przez firmę), a zysk netto to miara realnego sukcesu (ile pieniędzy fizycznie zostało w kasie po opłaceniu kosztów). Jest to absolutna podstawa do oceny zyskowności.

* **`PriceToEarnings`** *(Wskaźnik P/E - Cena do Zysku)*:
  * **Wzór:** `MarketCap_mean / NetIncome`
  * **Interpretacja:** Najsłynniejszy wskaźnik na Wall Street. W uproszczeniu odpowiada na pytanie: "Ile lat zajęłoby firmie zarobienie na swoją własną wartość rynkową przy utrzymaniu obecnych zysków?". Optymalne wartości zależą od branży, ale zazwyczaj poziom 15-20 uważa się za zdrowy balans. (Uwaga: Ujemne wartości oznaczają, że firma przynosi straty).

* **`Risk-AdjustedGrowth`** *(Wzrost skorygowany ryzykiem)*:
  * **Wzór:** `GrowthRate_mean / GrowthRate_std`
  * **Interpretacja:** Miernik jakości wzrostu firmy. Sama wysoka średnia wzrostu nie jest idealna, jeśli firma w jednym roku rośnie o 30%, a w kolejnym traci 20% (duże odchylenie standardowe). Wysoka wartość tego wskaźnika nagradza firmy, które rosną w sposób stabilny, systematyczny i przewidywalny (np. stałe 5% z roku na rok).

* **`Earnings-to-Growth`** *(Wskaźnik PEG - Cena/Zysk do Wzrostu skorygowanego ryzykiem)*:
  * **Wzór:** `PriceToEarnings / Risk-AdjustedGrowth`
  * **Interpretacja:** Uzupełnia klasyczny wskaźnik P/E o tempo rozwoju firmy, pozwalając ocenić, czy wysoka wycena spółki jest uzasadniona jej szybkim wzrostem. Spółka z wysokim P/E (np. 40) może być wciąż atrakcyjną inwestycją, jeśli jej zyski rosną o 50% rocznie (co da niski PEG). Zazwyczaj przyjmuje się, że wskaźnik PEG w okolicach 1.0 oznacza uczciwą wycenę, wartości poniżej 1.0 sugerują niedowartościowanie (okazję inwestycyjną), a wartości powyżej 1.5 - 2.0 mogą wskazywać, że akcje są "przegrzane" w stosunku do ich realnego potencjału wzrostu. (Uwaga: Wskaźnik traci sens interpretacyjny w przypadku ujemnego wzrostu lub strat firmy).

* **`ESG_Signal-to-Noise`** *(Wskaźnik Sygnału do Szumu dla ESG)*:
  * **Wzór:** `ESG_Overall_slope / ESG_Overall_cv`
  * **Interpretacja:** Zaawansowana metryka inspirowana wskaźnikiem Information Ratio, używana w analizie ilościowej (Quant). Łączy ona dwa wymiary zrównoważonego rozwoju: siłę trendu oraz jego stabilność.
    * **Sygnał (Licznik - Slope):** Wskazuje kierunek i tempo zmian. Dodatni slope oznacza, że firma z roku na rok poprawia swoje standardy ESG.
    * **Szum (Mianownik - CV):** Wskazuje na chaos i wahania. Wysokie CV oznacza, że oceny firmy są nieprzewidywalne.
  * **Jak czytać ten wskaźnik?** Dzieląc sygnał przez szum, metryka ta bezlitośnie karze firmy, których polityka ESG jest chaotyczna. Bardzo wysoki, dodatni wynik oznacza spółkę, która konsekwentnie i stabilnie poprawia swoje standardy (idealna sytuacja). Wynik ujemny sygnalizuje stabilną degradację standardów, a wynik bliski zeru oznacza duży chaos informacyjny lub całkowitą stagnację.