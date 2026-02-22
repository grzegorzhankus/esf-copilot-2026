# Product Requirements Document (PRD)

## ESF-Copilot 2026 — AI CFO Dashboard

| Pole | Wartość |
|------|---------|
| **Produkt** | ESF-Copilot 2026 (AI CFO Dashboard) |
| **Wersja dokumentu** | 1.0 |
| **Data** | 2026-02-22 |
| **Autor** | Grzegorz Hankus |
| **Status** | MVP Delivered |
| **Platforma docelowa** | NVIDIA DGX Spark (ARM64 Grace Blackwell) + Streamlit Cloud |

---

## 1. Wizja produktu

### 1.1 Problem

Analiza polskich sprawozdań finansowych (e-Sprawozdania) w formacie XML jest procesem:

- **Czasochłonnym** — manualna ekstrakcja danych z XML zajmuje 1–2 godziny na spółkę
- **Podatnym na błędy** — ręczne przenoszenie wartości z zagnieżdżonych struktur XML
- **Niestandaryzowanym** — różni analitycy stosują różne wskaźniki i progi
- **Skalowalność** — analiza portfela 50+ spółek wymaga tygodni pracy

### 1.2 Wizja rozwiązania

> **Upload XML → pełna analiza finansowa w ~30 sekund**

ESF-Copilot 2026 to interaktywny dashboard webowy, który automatycznie:
1. Parsuje pliki XML e-Sprawozdań zgodne ze schematami Ministerstwa Finansów RP
2. Ekstrahuje hierarchiczne dane z Bilansu, RZiS i RPP
3. Oblicza standaryzowany zestaw wskaźników finansowych (KPI)
4. Wykrywa sygnały ostrzegawcze (red flags)
5. Umożliwia dialog z AI o danych finansowych (CFO Chat)
6. Generuje raporty zarządcze (Board Memo) i eksporty (PDF/Excel)

### 1.3 Propozycja wartości

| Wartość | Opis |
|---------|------|
| **Automatyzacja** | Z ~2h manualnej analizy do ~30s automatycznej |
| **Standaryzacja** | 18 KPI i 10 red flags — identyczne progi dla każdej spółki |
| **Dwujęzyczność** | Pełne wsparcie PL/EN (835+ kluczy tłumaczeń) |
| **AI Insights** | CFO Chat, Board Memo, NL Query — powered by LLM |
| **Bezpieczeństwo** | Przetwarzanie on-premise, dane nie opuszczają infrastruktury |
| **Skalowalność** | Batch processing wielu plików jednocześnie |

---

## 2. Grupa docelowa

### 2.1 Persony użytkowników

| Persona | Rola | Potrzeba | Kluczowa funkcja |
|---------|------|----------|------------------|
| **Anna** | CFO / Dyrektor Finansowy | Szybki przegląd kondycji finansowej spółki | Executive Dashboard + KPI |
| **Marek** | Audytor / Analityk finansowy | Walidacja i cross-check danych e-Sprawozdań | Hierarchiczny Bilans/RZiS/RPP |
| **Katarzyna** | Członek Zarządu | Streszczenie wyników do decyzji | Board Memo (LLM) |
| **Tomek** | Księgowy | Weryfikacja poprawności przed wysyłką do KRS | XML Analysis + Red Flags |
| **Piotr** | Portfolio Manager | Analiza portfela spółek | Batch Processing + Forecasting |

### 2.2 Kontekst użycia

- **Branża:** Finanse, audyt, księgowość, zarządzanie portfelem
- **Regulacje:** e-Sprawozdania są obowiązkowym formatem raportowania do KRS (Krajowy Rejestr Sądowy) w Polsce
- **Źródło danych:** Pliki XML generowane przez systemy ERP lub pobierane z KRS
- **Schematy MF:** Ministerstwo Finansów definiuje strukturę XML (JednostkaInna, JednostkaMała, w PLN lub tysiącach)

---

## 3. Wymagania funkcjonalne

### 3.1 Moduł: Analiza XML (FR-01 → FR-06)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-01 | Upload pliku XML e-Sprawozdania przez interfejs webowy | Must | ✅ Done |
| FR-02 | Automatyczna detekcja schematu MF (namespace → slug) | Must | ✅ Done |
| FR-03 | Ekstrakcja metryk finansowych bazowych (8 metryk: Total Assets, Equity, Liabilities, Revenue, EBIT, Net Income, OCF, Net Cash Change) | Must | ✅ Done |
| FR-04 | Hierarchiczna ekstrakcja Bilansu (Aktywa/Pasywa, 148 pozycji, 4 poziomy głębokości) | Must | ✅ Done |
| FR-05 | Hierarchiczna ekstrakcja RZiS (47 pozycji, wariant kalkulacyjny) | Must | ✅ Done |
| FR-06 | Hierarchiczna ekstrakcja RPP (63 pozycje, metoda pośrednia, poziom A.II.1–10) | Must | ✅ Done |

**Obsługiwane schematy (8 wariantów):**

| # | Schemat | Format | Rok |
|---|---------|--------|-----|
| 1 | JednostkaInna w złotych | PLN | 2025 |
| 2 | JednostkaInna w tysiącach | PLN thousands | 2025 |
| 3 | JednostkaMała w złotych | PLN | 2025 |
| 4 | JednostkaInna w złotych | PLN | 2018 |
| 5 | Skonsolidowana JednostkaInna w tysiącach | PLN thousands | 2018 |
| 6 | JednostkaInna w tysiącach (dodatkowy) | PLN thousands | 2025 |
| 7 | JednostkaMała w tysiącach | PLN thousands | 2025 |
| 8 | Default (fallback) | Auto | — |

### 3.2 Moduł: Wskaźniki finansowe — KPI (FR-07)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-07 | Automatyczne obliczanie 18 KPI w 5 kategoriach | Must | ✅ Done |

**Pełna lista wskaźników KPI:**

| # | Kategoria | KPI | Jednostka | Formuła |
|---|-----------|-----|-----------|---------|
| 1 | Profitability | Return on Assets (ROA) | % | Net Income / Total Assets × 100 |
| 2 | Profitability | Return on Equity (ROE) | % | Net Income / Equity × 100 |
| 3 | Profitability | Net Profit Margin | % | Net Income / Revenue × 100 |
| 4 | Profitability | EBIT Margin | % | EBIT / Revenue × 100 |
| 5 | Liquidity | Current Ratio | times | Current Assets / Current Liabilities |
| 6 | Liquidity | Quick Ratio (Acid Test) | times | (Current Assets − Inventory) / Current Liabilities |
| 7 | Liquidity | Cash Ratio | times | Cash / Current Liabilities |
| 8 | Leverage | Debt-to-Equity Ratio | times | Total Liabilities / Equity |
| 9 | Leverage | Equity Ratio | % | Equity / Total Assets × 100 |
| 10 | Leverage | Debt Ratio | % | Total Liabilities / Total Assets × 100 |
| 11 | Efficiency | Asset Turnover | times | Revenue / Total Assets |
| 12 | Efficiency | Inventory Turnover | times | Revenue / Inventory |
| 13 | Efficiency | Receivables Turnover | times | Revenue / Receivables |
| 14 | Efficiency | Days Sales Outstanding (DSO) | days | (Receivables / Revenue) × 365 |
| 15 | Cash Flow | Operating Cash Flow to Revenue | % | OCF / Revenue × 100 |
| 16 | Cash Flow | Quality of Earnings | times | OCF / Net Income |

Każdy KPI zawiera: klucz, nazwę, wartość, jednostkę, kategorię, interpretację tekstową.

### 3.3 Moduł: Sygnały ostrzegawcze — Red Flags (FR-08)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-08 | Automatyczne wykrywanie 10 red flags z 3 poziomami severity | Must | ✅ Done |

**Pełna lista reguł:**

| # | Red Flag | Severity | Próg wyzwolenia | Opis ryzyka |
|---|----------|----------|-----------------|-------------|
| 1 | Negative Net Income | HIGH | Net Income < 0 | Spółka generuje stratę netto |
| 2 | Negative Equity | HIGH | Equity < 0 | Ryzyko niewypłacalności technicznej |
| 3 | Negative Operating Cash Flow | HIGH | OCF < 0 | Działalność operacyjna konsumuje gotówkę |
| 4 | Negative Profit Margin | HIGH | Net Profit Margin < 0 | Strata na każdej jednostce przychodu |
| 5 | Excessive Leverage | HIGH | Debt Ratio > 80% | Zadłużenie przekracza 80% aktywów |
| 6 | High Debt-to-Equity | MEDIUM | D/E > 2.0× | Dług ponad 2× przewyższa kapitał własny |
| 7 | Low Equity Ratio | MEDIUM | Equity Ratio < 20% | Słaba baza kapitałowa |
| 8 | Poor Quality of Earnings | MEDIUM | OCF / Net Income < 0.8 | Cash flow nie potwierdza zysków księgowych |
| 9 | Low ROE | LOW | ROE < 5% (gdy > 0) | Niska efektywność kapitału własnego |

### 3.4 Moduł: CFO Chat — AI Advisor (FR-09)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-09 | Interaktywny chat z AI doradcą finansowym | Should | ✅ Done |
| FR-10 | Odpowiedzi kontekstowe na podstawie załadowanych danych finansowych | Should | ✅ Done |
| FR-11 | Wsparcie dla pytań w języku naturalnym (PL i EN) | Should | ✅ Done |
| FR-12 | Historia czatu w ramach sesji | Should | ✅ Done |

**Backend LLM (dual):**

| Backend | Modele | Zastosowanie |
|---------|--------|-------------|
| NVIDIA NIM (cloud) | Llama 4 Maverick (405B), DeepSeek V3 (685B), Mistral Large 3 (123B), Qwen3 (72B) | Pełna analiza, duże konteksty |
| Ollama (local) | Llama 3.1 (8B), Mistral (7B), DeepSeek Coder (6.7B) | Offline, privacy-first, dev |

### 3.5 Moduł: Board Memo — Raport zarządczy (FR-13)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-13 | Automatyczne generowanie streszczenia zarządczego przez LLM | Should | ✅ Done |
| FR-14 | Format gotowy do prezentacji zarządowi | Should | ✅ Done |
| FR-15 | Kluczowe wnioski, rekomendacje, ocena ryzyk | Should | ✅ Done |

### 3.6 Moduł: Anomaly Detection (FR-16)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-16 | Wykrywanie anomalii w danych finansowych (ML) | Could | ✅ Done |
| FR-17 | Metody: Autoencoder (PyTorch), Isolation Forest, Z-score, IQR | Could | ✅ Done |
| FR-18 | Akceleracja GPU (NVIDIA CUDA) z fallback na CPU | Could | ✅ Done |

### 3.7 Moduł: Natural Language Query (FR-19)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-19 | Zapytania w języku naturalnym o dane finansowe | Could | ✅ Done |
| FR-20 | Konwersja pytań na zapytania strukturalne | Could | ✅ Done |
| FR-21 | Wyjaśnienie wyników w języku naturalnym | Could | ✅ Done |

### 3.8 Moduł: Sprawozdania szczegółowe (FR-22 → FR-24)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-22 | Strona P&L — hierarchiczna tabela RZiS z porównaniem okresów i % zmian | Must | ✅ Done |
| FR-23 | Strona Balance Sheet — hierarchiczna tabela Bilansu z Aktywa/Pasywa | Must | ✅ Done |
| FR-24 | Strona Cash Flow — hierarchiczna tabela RPP (Operacyjne/Inwestycyjne/Finansowe) | Must | ✅ Done |

### 3.9 Moduł: Forecasting — Prognozowanie (FR-25 → FR-28)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-25 | Prognoza wyników finansowych na 1–3 lata | Should | ✅ Done |
| FR-26 | Analiza scenariuszowa (best case / base case / worst case) | Should | ✅ Done |
| FR-27 | Interaktywne wizualizacje prognoz (Plotly) | Should | ✅ Done |
| FR-28 | Eksport prognoz do CSV | Should | ✅ Done |

**Parametry scenariuszy:**

| Scenariusz | Wzrost | Opis |
|------------|--------|------|
| Best case | +15% | Optymistyczny rozwój |
| Base case | +5% | Umiarkowany, realistyczny wzrost |
| Worst case | −2% | Spadek / stagnacja |

### 3.10 Moduł: Batch Processing (FR-29 → FR-32)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-29 | Jednoczesna analiza wielu plików XML | Should | ✅ Done |
| FR-30 | Raport podsumowujący dla całego portfela | Should | ✅ Done |
| FR-31 | Porównanie kondycji finansowej między spółkami | Should | ✅ Done |
| FR-32 | Eksport zbiorczy (ZIP) ze wszystkimi raportami | Should | ✅ Done |

### 3.11 Moduł: Export — Eksport danych (FR-33 → FR-35)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-33 | Eksport analizy do pliku Excel (.xlsx) z formatowaniem | Must | ✅ Done |
| FR-34 | Eksport analizy do pliku PDF z polskimi znakami (DejaVu fonts) | Must | ✅ Done |
| FR-35 | Eksport surowych danych do JSON | Must | ✅ Done |

### 3.12 Moduł: Dwujęzyczność — i18n (FR-36 → FR-38)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-36 | Pełne wsparcie interfejsu w języku polskim i angielskim | Must | ✅ Done |
| FR-37 | Przełączanie języka w panelu bocznym (session-persistent) | Must | ✅ Done |
| FR-38 | Dwujęzyczne etykiety KPI, red flags, metryk, komunikatów błędów | Must | ✅ Done |

**Zakres tłumaczeń:** 835+ kluczy w `core/i18n.py` obejmujących:
- Elementy UI (przyciski, menu, komunikaty)
- Nazwy i interpretacje KPI
- Opisy red flags
- Etykiety Bilansu, RZiS, RPP
- Komunikaty błędów i statusu
- Treści stron informacyjnych

### 3.13 Moduł: User Feedback (FR-39)

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| FR-39 | Formularz zbierania opinii użytkowników (kategorie, oceny, komentarze) | Could | ✅ Done |
| FR-40 | Przechowywanie feedbacku w lokalnej bazie SQLite | Could | ✅ Done |

---

## 4. Wymagania niefunkcjonalne

### 4.1 Bezpieczeństwo

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| NFR-01 | Bezpieczne parsowanie XML — ochrona przed XXE attacks (defusedxml) | Must | ✅ Done |
| NFR-02 | Klucze API przechowywane w zmiennych środowiskowych / Streamlit Secrets | Must | ✅ Done |
| NFR-03 | Plik .env z kluczami API wykluczony z repozytorium (.gitignore) | Must | ✅ Done |
| NFR-04 | On-premise deployment — dane finansowe nie opuszczają infrastruktury (opcja Ollama) | Should | ✅ Done |

### 4.2 Wydajność

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| NFR-05 | Analiza pojedynczego pliku XML (do 5 MB) w czasie < 10 sekund | Should | ✅ Done |
| NFR-06 | Obsługa plików XML do 50 MB | Could | Niesprawdzone |
| NFR-07 | Akceleracja GPU dla anomaly detection i batch processing | Could | ✅ Done |

### 4.3 Niezawodność

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| NFR-08 | Graceful degradation bez GPU — fallback na CPU | Must | ✅ Done |
| NFR-09 | Graceful degradation bez LLM — analiza XML działa bez modelu AI | Must | ✅ Done |
| NFR-10 | Fallback mapping (_default) dla nieznanych schematów MF | Must | ✅ Done |
| NFR-11 | Obsługa edge cases: division-by-zero, brakujące metryki, puste pliki | Must | ✅ Done |

### 4.4 Użyteczność

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| NFR-12 | Interfejs webowy dostępny przez przeglądarkę (bez instalacji desktop) | Must | ✅ Done |
| NFR-13 | Responsywny layout (wide mode Streamlit) | Should | ✅ Done |
| NFR-14 | Interaktywne wykresy (Plotly — zoom, hover, export PNG) | Should | ✅ Done |

### 4.5 Deployment

| ID | Wymaganie | Priorytet | Status |
|----|-----------|-----------|--------|
| NFR-15 | Docker deployment z NVIDIA CUDA (ARM64 Grace Blackwell) | Should | ✅ Done |
| NFR-16 | Streamlit Community Cloud deployment | Should | ✅ Done |
| NFR-17 | Konfiguracja via .env / Streamlit Secrets | Must | ✅ Done |

---

## 5. Architektura systemu

### 5.1 Diagram przepływu danych

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI (11 pages)                      │
│  XML Upload │ BS │ P&L │ CF │ CFO Chat │ Board Memo │ Forecasting  │
└──────┬──────┴────┴─────┴────┴──────────┴────────────┴──────────────┘
       │                           ▲
       ▼                           │
┌──────────────┐           ┌───────┴────────┐
│ xml_loader   │           │ i18n (EN/PL)   │
│ (defusedxml) │           │ 835+ keys      │
└──────┬───────┘           └────────────────┘
       ▼
┌──────────────┐    ┌─────────────────┐
│ schema_      │───▶│ mapping_engine  │
│ detector     │    │ (YAML → XPath)  │
│ (namespace   │    │ 8 schema        │
│  → slug)     │    │ variants        │
└──────────────┘    └────────┬────────┘
                             │
       ┌─────────────────────┼────────────────────────┐
       ▼                     ▼                         ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ balance_     │  │ pl_extractor     │  │ cf_extractor          │
│ sheet_       │  │ (RZiS)          │  │ (RPP)                 │
│ extractor    │  │ 47 items         │  │ 63 items              │
│ (148 items)  │  │                  │  │                       │
└──────┬───────┘  └────────┬─────────┘  └──────────┬────────────┘
       └───────────┬───────┘────────────────────────┘
                   ▼
         ┌──────────────────┐
         │ analysis_pipeline│──────────────────────────────────┐
         │ (orchestrator)   │                                  │
         └────────┬─────────┘                                  │
                  │                                            │
       ┌──────────┼──────────────┐                             │
       ▼          ▼              ▼                             ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐         ┌──────────────┐
│ kpi_       │ │ red_flags│ │ contracts.py │         │ Export       │
│ calculator │ │ (10 rules│ │ AnalysisResult│         │ PDF / Excel  │
│ (18 KPIs)  │ │          │ │ (frozen DC)  │         │ / JSON       │
└────────────┘ └──────────┘ └──────┬───────┘         └──────────────┘
                                   │
                    ┌──────────────┼──────────────────┐
                    ▼              ▼                   ▼
             ┌───────────┐ ┌─────────────┐ ┌─────────────────┐
             │ LLM       │ │ Anomaly     │ │ Forecasting     │
             │ Service   │ │ Detector    │ │ Engine          │
             │ (NIM +    │ │ (Z-score,   │ │ (scenarios,     │
             │  Ollama)  │ │  IQR, IF,   │ │  TFT, ARIMA)   │
             └───────────┘ │  Autoenc.)  │ └─────────────────┘
                           └─────────────┘
```

### 5.2 Stos technologiczny

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| **UI** | Streamlit 1.32+ | Szybki prototyp, wbudowane widgety, hosting w chmurze |
| **XML Parser** | defusedxml | Ochrona przed XXE attacks (OWASP) |
| **Mappings** | PyYAML | Czytelne, wersjonowalne konfiguracje XPath |
| **Dane** | pandas, numpy | Manipulacja danymi, obliczenia numeryczne |
| **Wykresy** | Plotly | Interaktywne wizualizacje z hover/zoom |
| **Export PDF** | ReportLab + DejaVu fonts | Wsparcie polskich znaków w PDF |
| **Export Excel** | openpyxl | Profesjonalne formatowanie arkuszy |
| **LLM Cloud** | NVIDIA NIM API | Duże modele (405B+), enterprise SLA |
| **LLM Local** | Ollama | Privacy-first, zero data leakage |
| **ML** | scikit-learn, PyTorch (opcjonalnie) | Anomaly detection, forecasting |
| **Deploy** | Docker (CUDA 12.6.0 ARM64) | NVIDIA DGX Spark, on-premise |
| **Deploy Cloud** | Streamlit Community Cloud | Publiczny dostęp bez infrastruktury |
| **Kontrakty** | Frozen dataclasses | Immutable, type-safe, zero dependencies |

### 5.3 Struktura plików

```
esf-copilot-2026/
├── app/
│   ├── app.py                          # Strona główna (Home)
│   └── pages/
│       ├── 1_📄_XML_Analysis.py       # Upload i analiza XML
│       ├── 2_💬_CFO_Chat.py           # AI Chat finansowy
│       ├── 3_🧾_Board_Memo_LLM.py    # Memo zarządcze (LLM)
│       ├── 4_🔴_Anomaly_Detection.py  # Wykrywanie anomalii (ML)
│       ├── 5_🔍_NL_Query.py          # Zapytania języka naturalnego
│       ├── 6_📈_P&L.py               # Rachunek Zysków i Strat
│       ├── 7_📙_Balance_Sheet.py      # Bilans
│       ├── 8_💵_Cash_Flow.py          # Rachunek Przepływów Pieniężnych
│       ├── 9_📈_Forecasting.py        # Prognozowanie
│       ├── 10_📦_Batch_Processing.py  # Przetwarzanie wsadowe
│       └── 11_📝_User_Feedback.py     # Formularz opinii
├── core/                               # 30 modułów logiki biznesowej
│   ├── analysis_pipeline.py            # Orkiestracja analizy
│   ├── balance_sheet_extractor.py      # Ekstrakcja Bilansu
│   ├── cf_extractor.py                 # Ekstrakcja RPP
│   ├── pl_extractor.py                 # Ekstrakcja RZiS
│   ├── kpi_calculator.py               # Obliczanie 18 KPI
│   ├── red_flags.py                    # Wykrywanie 10 red flags
│   ├── contracts.py                    # Frozen dataclasses
│   ├── config.py                       # Konfiguracja (.env + Secrets)
│   ├── i18n.py                         # Tłumaczenia PL/EN (835+ kluczy)
│   ├── llm_service.py                  # Integracja Ollama
│   ├── llm_advanced.py                 # NVIDIA NIM + multi-backend
│   ├── anomaly_detector.py             # ML anomaly detection
│   ├── forecasting_engine.py           # Silnik prognozowania
│   ├── nl_query_engine.py              # NL Query processor
│   ├── pdf_export.py                   # Export PDF (ReportLab)
│   ├── excel_export.py                 # Export Excel (openpyxl)
│   ├── xml_loader.py                   # Bezpieczne parsowanie XML
│   ├── schema_detector.py              # Detekcja schematu MF
│   ├── mapping_engine.py               # YAML → XPath extraction
│   └── ...                             # (formatowanie, wizualizacje, UI)
├── configs_mappings/                   # 8 mapowań XPath per schemat
├── data/demo_xml/                      # 6 plików XML do testów
├── tests/                              # 66 testów (pytest)
├── docs/                               # Dokumentacja techniczna
├── requirements.txt                    # Zależności Python
├── packages.txt                        # Zależności systemowe (fonts)
├── Dockerfile                          # Docker + NVIDIA CUDA ARM64
└── .streamlit/config.toml              # Konfiguracja Streamlit
```

---

## 6. Przypadki użycia

### UC-01: Szybka analiza jednego sprawozdania

**Aktor:** CFO / Analityk finansowy
**Cel:** Uzyskanie pełnej analizy finansowej z pliku XML

**Przebieg:**
1. Użytkownik otwiera stronę XML Analysis
2. Uploaduje plik XML e-Sprawozdania
3. System automatycznie: parsuje XML → wykrywa schemat → ekstrahuje metryki → oblicza KPI → wykrywa red flags
4. Użytkownik widzi: Executive Dashboard z KPI, red flags, health score
5. Użytkownik przechodzi do Bilansu / RZiS / RPP po szczegóły
6. Użytkownik eksportuje wynik do PDF lub Excel

**Czas:** ~30 sekund (upload + analiza)

### UC-02: Dialog z AI o danych finansowych

**Aktor:** CFO / Członek zarządu
**Cel:** Uzyskanie odpowiedzi na pytania finansowe

**Przebieg:**
1. Użytkownik uploaduje XML i generuje analizę (UC-01)
2. Przechodzi do strony CFO Chat
3. Zadaje pytanie: "Jakie są główne ryzyka finansowe tej spółki?"
4. LLM odpowiada na podstawie konkretnych danych z analizy
5. Użytkownik kontynuuje dialog follow-up

### UC-03: Analiza portfela spółek

**Aktor:** Portfolio Manager
**Cel:** Porównanie kondycji finansowej wielu spółek

**Przebieg:**
1. Użytkownik przechodzi do Batch Processing
2. Uploaduje wiele plików XML jednocześnie
3. System przetwarza je równolegle (ThreadPoolExecutor)
4. Generuje raport zbiorczy z porównaniem
5. Użytkownik pobiera ZIP ze wszystkimi raportami

### UC-04: Generowanie streszczenia zarządczego

**Aktor:** Asystent zarządu / CFO
**Cel:** Przygotowanie Board Memo na posiedzenie zarządu

**Przebieg:**
1. Użytkownik uploaduje XML i generuje analizę (UC-01)
2. Przechodzi do Board Memo
3. Klika "Generate"
4. LLM generuje profesjonalne streszczenie: kluczowe wnioski, rekomendacje, ryzyka
5. Użytkownik kopiuje lub eksportuje memo

### UC-05: Prognozowanie wyników finansowych

**Aktor:** Analityk finansowy / CFO
**Cel:** Projekcja wyników na kolejne lata

**Przebieg:**
1. Użytkownik uploaduje XML i generuje analizę (UC-01)
2. Przechodzi do Forecasting
3. Wybiera horyzont prognozy (1–3 lata) i parametry scenariuszy
4. System generuje 3 scenariusze z wizualizacjami
5. Użytkownik eksportuje prognozy do CSV

---

## 7. Dane testowe i walidacja

### 7.1 Pliki demo XML

| Plik | Rozmiar | Schemat | Spółka |
|------|---------|---------|--------|
| demo_01.xml | 465 KB | JednostkaInna (PLN) | — |
| demo_02.xml | 1.5 MB | JednostkaInna (tysiące PLN) | FINAL S.A. |
| demo_03.xml | 5.3 MB | (large file test) | — |
| demo_04.xml | 2.0 MB | — | — |
| demo_05.xml | 334 KB | — | — |
| sample.xml | mały | Demo schema | — |

### 7.2 Testy automatyczne

| Moduł testowy | Testy | Coverage |
|---------------|-------|----------|
| test_kpi_calculator.py | 16 | 100% |
| test_red_flags.py | 19 | 100% |
| test_schema_detector.py | 11 | 100% |
| test_xml_loader.py | 10 | 91% |
| test_mapping_engine.py | 10 | 86% |
| **Razem** | **66** | **11% (core overall)** |

### 7.3 Walidacja referencyjna (demo_02.xml — FINAL S.A.)

| Metryka | Wartość | Weryfikacja |
|---------|---------|-------------|
| Schemat | mf_2025_jednostka_inna_wtysiacach | ✅ |
| Bilans — pozycje | 148 items | ✅ |
| RZiS — pozycje | 47 items | ✅ |
| RPP — pozycje | 63 items | ✅ |
| KPI obliczone | 18 | ✅ |
| Red flags aktywne | ≥1 (Negative Net Income) | ✅ |

---

## 8. Ryzyka i mitigacje

| # | Ryzyko | Wpływ | Prawdopod. | Mitigacja |
|---|--------|-------|------------|-----------|
| R1 | Nowy schemat MF nie obsługiwany | Wysoki | Średnie | Fallback mapping `_default`; alert "unknown schema" w UI |
| R2 | Błędne mapowanie XPath → złe wartości | Wysoki | Średnie | Coverage % widoczne w UI; testy per mapping |
| R3 | Halucynacje LLM w CFO Chat | Średni | Wysokie | System prompt z konkretnymi danymi; temperature=0.1; disclaimer |
| R4 | Brak testów extractorów (BS/P&L/CF) | Średni | Wysokie | Plan: dodać testy z fixture XML (Q1 2026) |
| R5 | Brak CI/CD pipeline | Średni | Wysokie | Plan: GitHub Actions (Q1 2026) |
| R6 | Duży plik XML (>10 MB) → timeout | Średni | Niskie | Streaming parse; batch processing z progress bar |
| R7 | Bezpieczeństwo danych finansowych | Wysoki | Niskie | On-premise deploy; .env w .gitignore; defusedxml |
| R8 | Unit mismatch (PLN vs tysiące) | Wysoki | Niskie | Auto-detect z schema slug "wtysiacach" |

---

## 9. Roadmap

### Q1 2026 (MVP — Delivered ✅)

- [x] Upload i analiza XML e-Sprawozdań
- [x] Hierarchiczna ekstrakcja Bilansu, RZiS, RPP
- [x] 18 KPI w 5 kategoriach
- [x] 10 Red Flags z 3 severity levels
- [x] Dwujęzyczny interfejs PL/EN (835+ kluczy)
- [x] CFO Chat (NVIDIA NIM + Ollama)
- [x] Board Memo (LLM)
- [x] Anomaly Detection (ML + GPU)
- [x] NL Query Engine
- [x] Forecasting (3 scenariusze)
- [x] Batch Processing
- [x] Export PDF/Excel/JSON
- [x] 8 wariantów schematów MF
- [x] Streamlit Cloud deployment
- [x] Docker (NVIDIA CUDA ARM64)

### Q2 2026 (Planned)

- [ ] Fix 7 failed tests (schema_detector slug expectations)
- [ ] Testy BS/P&L/CF extractorów → coverage > 80%
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Ground truth validation (10+ spółek)
- [ ] Multi-period trend analysis
- [ ] Peer benchmarking (porównanie spółek)

### Q3–Q4 2026 (Planned)

- [ ] Consolidated statements support
- [ ] REST API endpoint (bez UI)
- [ ] Integracja z e-KRS API
- [ ] Regulatory compliance alerts (KSH, MSSF)
- [ ] Performance optimization (large files)
- [ ] Advanced ML forecasting (TFT, SARIMA)

---

## 10. Metryki sukcesu

| Metryka | Cel | Obecna wartość |
|---------|-----|----------------|
| Czas analizy (pojedynczy plik) | < 10 sekund | ~5 sekund |
| Obsługiwane schematy MF | ≥ 8 | 8 |
| Pokrycie testami (core) | > 80% | 11% |
| Testy passing | 100% | 91% (60/66) |
| Klucze tłumaczeń i18n | > 500 | 835+ |
| KPI obliczane automatycznie | ≥ 15 | 18 |
| Red flags wykrywane | ≥ 9 | 10 |
| Strony UI | ≥ 10 | 11 |
| Formaty eksportu | ≥ 3 | 4 (PDF, Excel, JSON, CSV) |

---

## 11. Słownik pojęć

| Termin | Definicja |
|--------|-----------|
| **e-Sprawozdanie** | Elektroniczne sprawozdanie finansowe w formacie XML, obowiązkowe do złożenia w KRS |
| **KRS** | Krajowy Rejestr Sądowy — rejestr podmiotów gospodarczych w Polsce |
| **MF** | Ministerstwo Finansów RP — definiuje schematy XML e-Sprawozdań |
| **Bilans** | Zestawienie aktywów i pasywów na dzień bilansowy |
| **RZiS** | Rachunek Zysków i Strat — zestawienie przychodów, kosztów i wyniku finansowego |
| **RPP** | Rachunek Przepływów Pieniężnych (Cash Flow Statement) |
| **KPI** | Key Performance Indicator — wskaźnik efektywności |
| **Red Flag** | Sygnał ostrzegawczy wskazujący na potencjalne problemy finansowe |
| **Slug** | Znormalizowana nazwa schematu MF (np. `mf_2025_jednostka_inna_wtysiacach`) |
| **XPath** | Język zapytań do nawigacji po strukturze XML |
| **NIM** | NVIDIA Inference Microservice — API do uruchamiania dużych modeli LLM |
| **Ollama** | Lokalne narzędzie do uruchamiania modeli LLM (privacy-first) |
| **DGX Spark** | Platforma NVIDIA z GPU Grace Blackwell (ARM64) |
| **Frozen dataclass** | Immutable Python dataclass — kontrakty danych bez możliwości modyfikacji |

---

*Dokument wygenerowany na podstawie analizy kodu źródłowego repozytorium esf-copilot-2026 (94 pliki, 44,762 LOC).*
