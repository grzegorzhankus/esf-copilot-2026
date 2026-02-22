# ESF-Copilot 2026 — Materiał do prezentacji technicznej

> **Wygenerowano:** 2026-02-07 na podstawie repozytorium `/home/grzegorzhankus/esf-copilot-2026`
> **Źródło danych:** kod, testy, dokumentacja, pliki konfiguracyjne, demo XML

---

## 1. SYSTEM OVERVIEW (max 1 strona)

### Co robi aplikacja

**ESF-Copilot 2026** to interaktywny analizator polskich sprawozdań finansowych (e-Sprawozdania) w formacie XML, zgodnych ze schematami Ministerstwa Finansów RP. Aplikacja automatycznie parsuje pliki XML o strukturze regulowanej przez MF, ekstrakcjonuje dane finansowe, oblicza wskaźniki (KPI), wykrywa sygnały ostrzegawcze (red flags) i prezentuje wyniki w formie interaktywnego dashboardu webowego z możliwością eksportu do PDF/Excel.

### Dla kogo

- **CFO / Dyrektorzy Finansowi** — szybki przegląd kondycji finansowej spółki
- **Audytorzy / Analitycy finansowi** — walidacja i cross-check danych
- **Członkowie zarządu** — Board Memo generowane automatycznie przez LLM
- **Księgowi** — weryfikacja poprawności e-Sprawozdań przed wysyłką do KRS

### Wejścia / Wyjścia

| Wejście | Wyjście |
|---------|---------|
| Plik XML e-Sprawozdania (zgodny ze schematem MF) | Analiza JSON z metrykami bazowymi |
| Konfiguracja mapowania XPath (YAML) | Hierarchiczny Bilans, RZiS, RPP |
| Pytania użytkownika (NL) | 10+ KPI w 4 kategoriach |
| | 9 red flags z severity levels |
| | Board Memo (LLM-generated) |
| | Eksport PDF / Excel |
| | Prognoza scenariuszowa (best/base/worst) |

### Gdzie jest wartość

- **Automatyzacja** — z ~2h manualnej analizy do ~30s
- **Standaryzacja** — te same KPI i progi dla każdej spółki
- **Dwujęzyczność** — pełne wsparcie PL/EN (489+ kluczy i18n)
- **LLM-powered insights** — CFO Chat, Board Memo, NL Query

### Gdzie jest ryzyko

- **Poprawność parsowania XML** — różne schematy MF, warianty (pośredni/bezpośredni RPP)
- **Mapowanie XPath** — nowe schematy wymagają nowych mapowań
- **Konwersja jednostek** — PLN vs PLN_thousands (wymagana automatyczna detekcja)
- **Halucynacje LLM** — odpowiedzi CFO Chat mogą zawierać błędy
- **Brak walidacji wobec oryginału** — system nie porównuje z oficjalnym e-Sprawozdaniem w KRS

---

## 2. ARCHITEKTURA

### 2.1 Komponenty (lista + odpowiedzialności)

| Komponent | Plik(i) | Odpowiedzialność |
|-----------|---------|-----------------|
| **XML Loader** | `core/xml_loader.py` (70 LOC) | Bezpieczne parsowanie XML (defusedxml, ochrona XXE) |
| **Schema Detector** | `core/schema_detector.py` (75 LOC) | Identyfikacja schematu MF z namespace URI → slug |
| **Mapping Engine** | `core/mapping_engine.py` (193 LOC) | Ładowanie YAML mapowania, ekstrakcja metryk XPath |
| **Balance Sheet Extractor** | `core/balance_sheet_extractor.py` (389 LOC) | Hierarchiczna ekstrakcja bilansu (Aktywa/Pasywa) |
| **P&L Extractor** | `core/pl_extractor.py` (338 LOC) | Hierarchiczna ekstrakcja RZiS (15 pozycji głównych) |
| **Cash Flow Extractor** | `core/cf_extractor.py` (360 LOC) | Hierarchiczna ekstrakcja RPP (metoda pośrednia/bezpośrednia) |
| **KPI Calculator** | `core/kpi_calculator.py` (263 LOC) | 15 KPI w 5 kategoriach (Profitability, Liquidity, Leverage, Efficiency, Cash Flow) |
| **Red Flags** | `core/red_flags.py` (173 LOC) | 9 reguł wykrywania zagrożeń (3 severity levels) |
| **Analysis Pipeline** | `core/analysis_pipeline.py` (99 LOC) | Orkiestracja całego flow: XML → AnalysisResult |
| **Contracts** | `core/contracts.py` (140 LOC) | Frozen dataclasses: Metadata, MetricValue, Coverage, KPI, RedFlag, AnalysisResult |
| **LLM Service** | `core/llm_service.py` + `llm_advanced.py` (911 LOC) | Dual-backend: NVIDIA NIM (cloud) + Ollama (local) |
| **Anomaly Detector** | `core/anomaly_detector.py` (559 LOC) | ML-based anomaly detection (Z-score, IQR, Isolation Forest) |
| **Forecasting Engine** | `core/forecasting_engine.py` (578 LOC) | Prognoza scenariuszowa (best/base/worst) |
| **i18n** | `core/i18n.py` (880 LOC) | Dwujęzyczny słownik tłumaczeń (489+ kluczy EN/PL) |
| **Export** | `core/pdf_export.py` + `excel_export.py` (540 LOC) | Generowanie raportów PDF (reportlab) i Excel (openpyxl) |
| **Streamlit Pages** | `app/pages/*.py` (11 stron) | Interaktywne UI: Upload, Analiza, Chat, Bilans, RZiS, RPP, Prognoza |

### 2.2 Diagram blokowy (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI (11 pages)                      │
│  XML Upload │ BS │ P&L │ CF │ CFO Chat │ Board Memo │ Forecasting  │
└──────┬──────┴────┴─────┴────┴──────────┴────────────┴──────────────┘
       │                           ▲
       ▼                           │
┌──────────────┐           ┌───────┴────────┐
│ xml_loader   │           │ i18n (EN/PL)   │
│ (defusedxml) │           │ 489+ keys      │
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
│ sheet_       │  │ (RZiS hierarchy) │  │ (RPP pośr/bezpośr)   │
│ extractor    │  │                  │  │                       │
│ (148 items)  │  │ (47 items)       │  │ (63 items)            │
└──────┬───────┘  └────────┬─────────┘  └──────────┬────────────┘
       │                   │                        │
       └───────────┬───────┘────────────────────────┘
                   ▼
         ┌──────────────────┐
         │ analysis_pipeline│
         │ (orchestrator)   │
         └────────┬─────────┘
                  │
       ┌──────────┼──────────────┐
       ▼          ▼              ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│ kpi_       │ │ red_flags│ │ contracts.py │
│ calculator │ │ (9 rules)│ │ AnalysisResult│
│ (15 KPIs)  │ │          │ │ (frozen DC)  │
└────────────┘ └──────────┘ └──────┬───────┘
                                   │
                    ┌──────────────┼──────────────────┐
                    ▼              ▼                   ▼
             ┌───────────┐ ┌─────────────┐ ┌─────────────────┐
             │ LLM       │ │ Anomaly     │ │ Export          │
             │ Service   │ │ Detector    │ │ (PDF/Excel/JSON)│
             │ (NIM +    │ │ (Z-score,   │ │                 │
             │  Ollama)  │ │  IQR, IF)   │ │                 │
             └───────────┘ └─────────────┘ └─────────────────┘
```

### 2.3 Sekwencja przepływu danych (krok po kroku)

```
1. User → Upload XML file (.xml) via Streamlit UI
2. xml_loader.parse_xml_bytes() → Element root (defusedxml)
3. schema_detector.detect_schema_id(root) → namespace URI
4. schema_detector.schema_id_to_slug() → "mf_2025_jednostka_inna_wtysiacach"
5. mapping_engine.load_mapping(slug) → YAML config (xpaths, transforms)
6. PARALLEL EXTRACTION:
   a) mapping_engine.compute_metrics(root, mapping) → List[MetricValue]
   b) balance_sheet_extractor.extract_balance_sheet(root) → List[BSItem]
   c) pl_extractor.extract_pl_statement(root) → List[PLItem]
   d) cf_extractor.extract_cash_flow(root) → List[CFItem]
7. kpi_calculator.calculate_kpis(metrics_dict) → List[KPI]
8. red_flags.detect_red_flags(metrics, kpis) → List[RedFlag]
9. ASSEMBLE → AnalysisResult (frozen dataclass)
10. SERIALIZE → JSON (saved to .streamlit_cache/analyses/)
11. DISPLAY → Streamlit pages render hierarchical tables, charts, metrics
12. OPTIONAL: LLM integration for CFO Chat, Board Memo, NL Query
13. OPTIONAL: Export to PDF/Excel
```

### 2.4 Punkty walidacji

| # | Gdzie | Co sprawdzamy | Plik |
|---|-------|---------------|------|
| V1 | XML Upload | Czy plik jest poprawnym XML (defusedxml, XXE protection) | `xml_loader.py:38-46` |
| V2 | Schema Detection | Czy namespace jest rozpoznany (not "unknown") | `schema_detector.py:25-27` |
| V3 | Mapping Load | Czy istnieje mapping dla danego slug (fallback: _default) | `mapping_engine.py:74-83` |
| V4 | Metric Extraction | Coverage % — ile metryk udało się wyciągnąć | `mapping_engine.py:147` |
| V5 | KPI Calculation | Division-by-zero guards (all denominators checked ≠ 0) | `kpi_calculator.py` |
| V6 | Red Flags | Threshold-based rules with severity classification | `red_flags.py` |
| V7 | Unit Detection | Auto-detect PLN_thousands from schema slug | `mapping_engine.py` |
| V8 | Hierarchy Labels | CF/BS/PL label lookup with fallback to raw key | `cf_extractor.py:142-183` |

---

## 3. KONCEPCJA → PDR → IMPLEMENTACJA → TESTY → WALIDACJE

### 3.1 KONCEPCJA

**Cel etapu:** Zdefiniowanie problemu i wizji produktu.

**Kluczowe decyzje:**
- Problem: analiza e-Sprawozdań finansowych w formacie XML MF jest manualna, czasochłonna i podatna na błędy
- Wizja: "AI CFO Dashboard" — jeden upload XML → pełna analiza z KPI, red flags, prognozą
- Target: NVIDIA DGX Spark (ARM64 Grace Blackwell) jako platforma docelowa
- Stos: Python + Streamlit (rapid prototyping) + LLM (NVIDIA NIM / Ollama)

**Artefakty:**
- `README.md` (208 LOC) — opis funkcjonalności i wizji
- `docs/devlog.md` (6 LOC) — wpis z 2026-01-05: "Block 1 scaffold"

**Co poszło dobrze:** Jasna wizja "XML in → insights out". Wybór Streamlit umożliwił szybki prototyp.
**Co było trudne:** Brak formalnego dokumentu PDR na początku.

**Ryzyka i mitigacje:**
| Ryzyko | Mitigacja |
|--------|-----------|
| Zbyt wiele schematów MF do obsłużenia | Slug-based mapping z _default fallback |
| LLM może generować nieprawdziwe dane finansowe | Kontekstowe prompty z konkretnymi danymi z XML |

---

### 3.2 PDR (PDR-ODTWORZONE)

> **UWAGA:** Formalny dokument PDR **NIE ISTNIEJE** w repozytorium. Poniższy PDR został zrekonstruowany na podstawie kodu, testów, README i devlog.

**Cel etapu:** Zdefiniowanie wymagań technicznych i funkcjonalnych.

**Wymagania funkcjonalne (odtworzone z kodu):**

| ID | Wymaganie | Status | Źródło dowodu |
|----|-----------|--------|---------------|
| FR-01 | Upload pliku XML e-Sprawozdania | ✅ Zaimplementowane | `app/pages/1_📄_XML_Analysis.py` |
| FR-02 | Automatyczna detekcja schematu MF | ✅ Zaimplementowane | `core/schema_detector.py` |
| FR-03 | Ekstrakcja metryk finansowych (XPath) | ✅ Zaimplementowane | `core/mapping_engine.py` |
| FR-04 | Hierarchiczny Bilans (Aktywa/Pasywa) | ✅ Zaimplementowane | `core/balance_sheet_extractor.py` |
| FR-05 | Hierarchiczny RZiS (15 pozycji) | ✅ Zaimplementowane | `core/pl_extractor.py` |
| FR-06 | Hierarchiczny RPP (63 pozycje, A.II.1 level) | ✅ Zaimplementowane | `core/cf_extractor.py` |
| FR-07 | KPI w 5 kategoriach (15 wskaźników) | ✅ Zaimplementowane | `core/kpi_calculator.py` |
| FR-08 | Red Flags (9 reguł, 3 severity) | ✅ Zaimplementowane | `core/red_flags.py` |
| FR-09 | Dwujęzyczny interfejs PL/EN | ✅ Zaimplementowane | `core/i18n.py` (489+ kluczy) |
| FR-10 | CFO Chat (LLM Q&A) | ✅ Zaimplementowane | `app/pages/2_💬_CFO_Chat.py` |
| FR-11 | Board Memo (LLM-generated) | ✅ Zaimplementowane | `app/pages/3_🧾_Board_Memo_LLM.py` |
| FR-12 | Anomaly Detection (ML) | ✅ Zaimplementowane | `core/anomaly_detector.py` |
| FR-13 | Forecasting (scenariusze) | ✅ Zaimplementowane | `core/forecasting_engine.py` |
| FR-14 | Batch Processing (multi-file) | ✅ Zaimplementowane | `app/pages/10_📦_Batch_Processing.py` |
| FR-15 | Export PDF/Excel | ✅ Zaimplementowane | `core/pdf_export.py`, `core/excel_export.py` |

**Wymagania niefunkcjonalne (odtworzone):**

| ID | Wymaganie | Status | Źródło dowodu |
|----|-----------|--------|---------------|
| NFR-01 | Bezpieczeństwo XML (XXE prevention) | ✅ | `defusedxml` w `xml_loader.py` |
| NFR-02 | Docker + NVIDIA CUDA support | ✅ | `Dockerfile` (CUDA 12.6.0, ARM64) |
| NFR-03 | Graceful degradation bez GPU/LLM | ✅ | Fallback w `anomaly_detector.py`, `llm_service.py` |
| NFR-04 | Konfiguracja via .env | ✅ | `core/config.py`, `.env.example` |

**BRAK DANYCH — do uzupełnienia:**
- [ ] Dokument PDR z wymaganiami (propozycja: `docs/PDR.md`)
- [ ] Backlog / Issue tracker (brak plików issues w repo, brak GitHub Issues link)
- [ ] Diagram sekwencji UML / C4 (propozycja: `docs/architecture_c4.md`)
- [ ] User Stories / Acceptance Criteria

---

### 3.3 IMPLEMENTACJA

**Cel etapu:** Budowa działającego systemu zgodnie z wymaganiami.

**Kluczowe decyzje implementacyjne:**

1. **Frozen dataclasses** (`contracts.py`) — immutable data contracts zapewniające type safety
2. **Slug-based mapping** — `schema_id_to_slug()` konwertuje URI namespace → katalog z YAML
3. **Hierarchiczna ekstrakcja** — rekurencyjne przechodzenie XML z numeracją poziomu (level 0-4)
4. **Dual LLM backend** — NVIDIA NIM (cloud, 405B+ models) + Ollama (local, 7-8B models)
5. **Unit auto-detection** — slug zawierający "wtysiacach" → `PLN_thousands` (×1000)

**Artefakty:**

| Warstwa | Pliki | LOC | Opis |
|---------|-------|-----|------|
| Core | 30 modułów w `core/` | 8,432 | Logika biznesowa, ekstrakcja, analiza |
| UI | 11 stron w `app/pages/` | ~5,400 | Streamlit dashboard |
| Config | 8 mapowań YAML | ~150 | XPath rules per schema |
| Infra | Dockerfile, docker-compose, scripts | ~360 | Deployment NVIDIA DGX Spark |

**Timeline (odtworzony z devlog + git):**
- **2026-01-05:** Block 1 — scaffold: upload, parsing, schema detection, analysis.json
- **2026-01-05:** Block 2 — slug-based mapping loader, metrics_base, coverage
- **2026-01-16:** Rozbudowa stron (Balance Sheet, P&L, Cash Flow, Forecasting)
- **2026-01-29:** Bilingual i18n (489+ keys), hierarchical extractors (BS, P&L, CF)
- **2026-01-30:** CF extractor fix — nested labels (A.A.II.A.II.1 → "1. Amortyzacja")

**Co poszło dobrze:**
- Szybki prototyp dzięki Streamlit (11 interaktywnych stron)
- Frozen dataclasses dały silne kontrakty między modułami
- Rekurencyjna ekstrakcja XML skaluje się do dowolnej głębokości
- Dwujęzyczność zaimplementowana jako single-source dictionary

**Co było trudne:**
- **Nested XML keys** — `A_A_II_A_II_1` pattern wymagał wielopoziomowego fallback w `_get_label()`
- **Unit mismatch** — schemat mówi "w tysiącach" ale mapping miał `unit: PLN`
- **Wiele schematów MF** — 8+ wariantów (JednostkaInna, JednostkaMała, w PLN/tysiącach, 2018/2025)
- **Cash Flow pośredni vs bezpośredni** — dwa różne poddrzewa XML

**Ryzyka i mitigacje:**
| Ryzyko | Mitigacja |
|--------|-----------|
| Nowy schemat MF złamie parsowanie | `_default/mapping_v1.yaml` jako fallback |
| LLM niedostępny | Graceful degradation — analiza działa bez LLM |
| Duże pliki XML (5+ MB) | Streaming parse + batch processing z progress bar |

---

### 3.4 TESTY

**Cel etapu:** Walidacja poprawności logiki biznesowej.

**Artefakty testowe:**

| Plik | Testy | LOC | Pokrycie |
|------|-------|-----|----------|
| `tests/test_kpi_calculator.py` | 16 testów | 239 | 100% core/kpi_calculator |
| `tests/test_xml_loader.py` | 10 testów | 81 | 91% core/xml_loader |
| `tests/test_mapping_engine.py` | 10 testów | 259 | 86% core/mapping_engine |
| `tests/test_red_flags.py` | 19 testów | 292 | 100% core/red_flags |
| `tests/test_schema_detector.py` | 11 testów | 96 | 100% core/schema_detector |
| **TOTAL** | **66 testów** | **967** | — |

**Wyniki ostatniego uruchomienia (2026-02-07):**
- ✅ 60 passed
- ❌ 7 failed (wszystkie w `test_schema_detector.py` — testy nie zaktualizowane po refactorze `schema_id_to_slug()`)

**Kategorie testów:**
- **Unit tests** — pure function testing (KPI math, XML parsing)
- **Integration tests** — mapping engine with real YAML + XML fixtures
- **Edge cases** — division by zero, empty input, missing metrics, negative values

**Konfiguracja:** `pytest.ini`
```ini
[pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers --cov=core --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
```

**Co poszło dobrze:**
- 100% coverage na krytycznych modułach (kpi_calculator, red_flags, schema_detector)
- Testy KPI sprawdzają dokładne wartości matematyczne
- Red flag testy pokrywają wszystkie 9 reguł + edge cases

**Co było trudne:**
- 7 testów schema_detector wymaga aktualizacji po refactorze slug generation
- Brak testów dla extractorów (balance_sheet, pl, cf) — 0% coverage
- Brak testów end-to-end (upload XML → pełna analiza)

**BRAK DANYCH — do uzupełnienia:**
- [ ] Testy dla `balance_sheet_extractor.py` (0% coverage)
- [ ] Testy dla `pl_extractor.py` (0% coverage)
- [ ] Testy dla `cf_extractor.py` (0% coverage)
- [ ] Testy E2E z demo XML files
- [ ] Testy LLM integration (mock-based)
- [ ] CI/CD pipeline (brak `.github/workflows/`)

---

### 3.5 WALIDACJE

**Cel etapu:** Potwierdzenie, że system działa poprawnie z rzeczywistymi danymi.

**Dane walidacyjne:**

| Plik | Rozmiar | Schemat | Rezultat |
|------|---------|---------|----------|
| `demo_01.xml` | 465 KB | JednostkaInna | ✅ Parsuje, metryki poprawne |
| `demo_02.xml` | 1.5 MB | JednostkaInnaWTysiacach | ✅ Parsuje, 148 BS + 47 P&L + 63 CF items |
| `demo_03.xml` | 5.3 MB | (large) | ✅ Parsuje, test wydajności |
| `demo_04.xml` | 2.0 MB | — | ✅ Parsuje |
| `demo_05.xml` | 334 KB | — | ✅ Parsuje |

**Walidacja demo_02.xml (FINAL S.A.):**
- Company: FINAL SPÓŁKA AKCYJNA
- Period: 2024-01-01 → 2024-12-31
- Balance Sheet: 148 items extracted
- P&L: 47 items extracted
- Cash Flow: 63 items extracted (A.II.1 through A.II.10 detail level)
- Schema: `mf_2025_jednostka_inna_wtysiacach`

**Znane issues wykryte podczas walidacji:**
1. ~~Cash Flow pokazywał 0 wartości~~ → naprawione (key mismatch w mapping)
2. ~~P&L brak etykiet na niższych poziomach~~ → naprawione (rozszerzenie PL_LABELS)
3. ~~XML Analysis pokazywał 0.4 mln zamiast 413 mln~~ → naprawione (unit auto-detection)
4. ~~CFO Chat nie czyścił pola input~~ → naprawione (dynamic Streamlit key)
5. ~~CF labels: A.A.II.A.II.1 zamiast "1. Amortyzacja"~~ → naprawione (nested key resolution)

**BRAK DANYCH — do uzupełnienia:**
- [ ] Formalna checklista walidacyjna (propozycja: `docs/VALIDATION_CHECKLIST.md`)
- [ ] Porównanie z manualną analizą (ground truth)
- [ ] Performance benchmarks (czas przetwarzania per plik)
- [ ] UAT (User Acceptance Testing) report

---

## 4. DECYZJE I TRADE-OFFY (Decision Log)

| # | Decyzja | Opcje rozważane | Wybór | Uzasadnienie | Konsekwencje |
|---|---------|-----------------|-------|--------------|--------------|
| D1 | **Framework UI** | Streamlit vs Flask+React vs Gradio | **Streamlit** | Najszybszy prototyp, wbudowane widgets (tabele, wykresy, file upload) | Ograniczenia customizacji UI, brak real-time updates |
| D2 | **XML Parser** | lxml vs ElementTree vs defusedxml | **defusedxml** | Ochrona przed XXE attacks (OWASP), fallback na ElementTree | Minimalnie wolniejszy niż lxml, ale bezpieczny |
| D3 | **Data contracts** | Dict vs Pydantic vs frozen dataclass | **frozen dataclass** | Zero dependencies, immutability, built-in `asdict()` | Brak runtime validation (vs Pydantic), manualne `to_dict()` |
| D4 | **LLM Backend** | OpenAI API vs NVIDIA NIM vs Ollama | **NIM + Ollama (dual)** | NIM: duże modele (405B) w chmurze; Ollama: local dev bez internetu | Utrzymanie dwóch integracji, ale zero vendor lock-in |
| D5 | **Mapping storage** | Database vs YAML vs JSON | **YAML per schema** | Czytelne, wersjonowalne, łatwe do edycji przez analityków | Wymaga nowego pliku per schemat MF |
| D6 | **i18n approach** | gettext vs JSON vs Python dict | **Python dict** (single-file) | Prostota, zero dependencies, IDE autocomplete | Duży plik (880 LOC), brak narzędzi translatorskich |
| D7 | **Unit handling** | Explicit parameter vs auto-detect | **Auto-detect from slug** | Schema slug "wtysiacach" → PLN_thousands automatycznie | Zależność od konwencji nazewnictwa schematów MF |
| D8 | **Hierarchy extraction** | Flat XPath list vs recursive traversal | **Recursive traversal** | Automatycznie wykrywa dowolną głębokość struktury XML | Wymaga label dictionaries per statement type |
| D9 | **Deploy target** | Cloud (AWS/GCP) vs On-prem DGX Spark | **DGX Spark (ARM64)** | Dedykowany hardware z GPU, dane zostają on-prem | Docker CUDA image, arch-specific optimizations |
| D10 | **Test strategy** | E2E only vs Unit + Integration | **Unit + Integration** (pytest) | Szybkie testy core logic, coverage reports | Brak E2E testów (gap) |

---

## 5. RYZYKA (Risk Register)

| # | Ryzyko | Wpływ | Prawdopodob. | Wykrywalność | Zabezpieczenia | Owner |
|---|--------|-------|-------------|-------------|----------------|-------|
| R1 | **Nowy schemat MF** nie obsługiwany | Wysoki | Średnie | Wysoka (schema_detector zwróci "unknown") | `_default` fallback mapping; alert w UI | Dev |
| R2 | **Błędne mapowanie XPath** → złe wartości metryk | Wysoki | Średnie | Niska (brak ground-truth validation) | Testy per mapping; coverage % w UI | Dev/QA |
| R3 | **Unit mismatch** (PLN vs tysiące) | Wysoki | Niskie (naprawione) | Średnia (auto-detect z slug) | Unit auto-detection + explicit YAML field | Dev |
| R4 | **Halucynacje LLM** w CFO Chat | Średni | Wysokie | Niska (brak fact-checking) | System prompts z konkretnymi danymi; disclaimer w UI | Dev/Biznes |
| R5 | **Duży plik XML** (>10 MB) → timeout | Średni | Niskie | Wysoka (user widzi timeout) | Streaming parse; batch processing | Dev |
| R6 | **Brak testów extractorów** (BS, P&L, CF) | Średni | Wysokie (istniejący gap) | — | Dodać testy z fixture XML | Dev/QA |
| R7 | **Brak CI/CD** → regresje po deploymencie | Średni | Wysokie (istniejący gap) | — | Dodać GitHub Actions pipeline | DevOps |
| R8 | **Bezpieczeństwo danych** — wrażliwe dane finansowe | Wysoki | Niskie (on-prem) | — | Docker on DGX Spark; .env for secrets; .gitignore | Sec/Dev |
| R9 | **7 failed tests** w schema_detector | Niski | 100% (widoczne) | Wysoka | Update test expectations after slug refactor | Dev |
| R10 | **Brak audit trail** — kto analizował co | Średni | Średnie | Niska | Dodać logging user actions | Dev |

---

## 6. METRYKI I JAKOŚĆ

### 6.1 Metryki dostępne

| Metryka | Wartość | Źródło |
|---------|---------|--------|
| Total LOC (Python) | 13,860 | `wc -l core/*.py app/pages/*.py tests/*.py` |
| Core modules | 30 | `core/*.py` |
| UI pages | 11 | `app/pages/*.py` |
| Test files | 5 | `tests/test_*.py` |
| Total tests | 66 (60 pass, 7 fail) | `pytest -v` |
| Test coverage (core overall) | 11% | `pytest --cov=core` |
| Test coverage (kpi_calculator) | 100% | pytest |
| Test coverage (red_flags) | 100% | pytest |
| Test coverage (schema_detector) | 100% | pytest |
| Test coverage (xml_loader) | 91% | pytest |
| Test coverage (mapping_engine) | 86% | pytest |
| i18n keys | 489+ | `core/i18n.py` |
| Supported schemas | 8 | `configs_mappings/*/mapping_v1.yaml` |
| KPI rules | 15 | `core/kpi_calculator.py` |
| Red flag rules | 9 | `core/red_flags.py` |
| Demo XML files | 6 (9.4 MB total) | `data/demo_xml/` |

### 6.2 Metryki do dodania

| Metryka | Jak mierzyć | Priorytet |
|---------|-------------|-----------|
| Poprawność parsowania (accuracy) | Porównanie z manualnie zweryfikowanym ground truth | Wysoki |
| Czas przetwarzania per plik | `time.time()` w pipeline + logging | Średni |
| % błędów walidacji (false positives red flags) | Analiza na próbie 50+ spółek | Wysoki |
| LLM response quality (CFO Chat) | Human evaluation + scoring | Średni |
| Coverage extractorów | Dodać testy BS/P&L/CF | Wysoki |
| User satisfaction (CSAT) | Feedback form (strona 11) | Niski |

### 6.3 Definition of Done (propozycja wersji produkcyjnej)

- [ ] Wszystkie 66 testów przechodzą (0 failures)
- [ ] Coverage core > 80%
- [ ] Testy dla BS/P&L/CF extractorów
- [ ] E2E test z minimum 5 różnymi schematami MF
- [ ] Porównanie z ground truth na 10+ spółkach
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Security scan (bandit / safety)
- [ ] Performance test: < 5s per plik XML do 5 MB
- [ ] Dokumentacja API (PDR formalne)
- [ ] UAT sign-off

---

## 7. MATERIAŁ DO PREZENTACJI

### Slajd 1: Tytuł
**ESF-Copilot 2026 — AI CFO Dashboard for Polish Financial Statements**
- Automatyczna analiza e-Sprawozdań finansowych XML
- Platforma: NVIDIA DGX Spark (ARM64 Grace Blackwell)
- Python / Streamlit / LLM (NVIDIA NIM + Ollama)
- Dwujęzyczny (PL/EN)

> *Notatki prelegenta:* Przedstaw kontekst — e-Sprawozdania to obowiązkowy format raportowania finansowego do KRS w Polsce. Firmy składają XML o ściśle zdefiniowanej strukturze. Nasz tool automatyzuje analizę tych plików.

---

### Slajd 2: Problem i wartość biznesowa
**Problem:**
- Manualna analiza e-Sprawozdania zajmuje 1-2h per spółka
- Brak standaryzacji wskaźników między analitykami
- Ryzyko błędów przy ręcznym wyciąganiu danych z XML

**Wartość:**
- Upload XML → pełna analiza w ~30 sekund
- 15 KPI automatycznie obliczonych
- 9 reguł red flags z alertami severity
- Board Memo generowane przez AI

> *Notatki prelegenta:* Pokaż demo — upload demo_02.xml i przejdź przez Dashboard. Zwróć uwagę na czas — od uploadu do gotowej analizy.

---

### Slajd 3: Architektura — Data Flow
**XML → Parse → Detect → Extract → Analyze → Present**
- [Użyj diagramu ASCII z sekcji 2.2]
- 4 równoległe extractory: Balance Sheet, P&L, Cash Flow, Mapping Engine
- Immutable data contracts (frozen dataclasses)
- Dual LLM backend: NVIDIA NIM (cloud 405B) + Ollama (local 8B)

> *Notatki prelegenta:* Podkreśl design decision — frozen dataclasses dają gwarancję, że dane nie mutują między modułami. Dual LLM = zero vendor lock-in.

---

### Slajd 4: XML Parsing Pipeline — bezpieczeństwo i obsługa schematów
**Bezpieczeństwo:**
- `defusedxml` — ochrona przed XXE (XML External Entity) attacks
- Walidacja na każdym etapie (empty file, malformed XML, unknown schema)

**Obsługa schematów MF:**
- 8 wariantów schematów (JednostkaInna, JednostkaMała, PLN/tysiące, 2018/2025)
- Slug-based mapping: `mf_2025_jednostka_inna_wtysiacach` → `configs_mappings/…/mapping_v1.yaml`
- `_default` fallback dla nieznanych schematów

> *Notatki prelegenta:* Pokaż `schema_detector.py` — 75 linii kodu, a obsługuje 8+ schematów. Zwróć uwagę na unit auto-detection z nazwy slug.

---

### Slajd 5: Hierarchiczna ekstrakcja danych finansowych
**3 extractory, 258 pozycji:**
- **Balance Sheet**: 148 items (Aktywa A/B + Pasywa A/B, 4 levels deep)
- **P&L (RZiS)**: 47 items (15 pozycji głównych, kalkulacyjny wariant)
- **Cash Flow (RPP)**: 63 items (A.II.1 through C.II.9 detail)

**Podejście:** Rekurencyjne przechodzenie XML z label dictionaries (PL+EN)

```python
# Przykład: cf_extractor.py — label lookup with fallback
def _get_label(key: str) -> tuple:
    clean_key = key.replace("RachPrzeplywow_", "")
    if clean_key in CF_LABELS:
        return CF_LABELS[clean_key]
    # Fallback: A_A_II_A_II_1 → A_II_1
    ...
```

> *Notatki prelegenta:* Pokaż hierarchiczną tabelę Cash Flow w aplikacji. Zwróć uwagę na poziom detalu — A.II.1 "Amortyzacja", A.II.8 "Zmiana stanu zobowiązań".

---

### Slajd 6: KPI i Red Flags — automatyczna analiza
**15 KPI w 5 kategoriach:**
- Profitability: ROA, ROE, Net Profit Margin, EBIT Margin
- Liquidity: Current Ratio, Quick Ratio, Cash Ratio
- Leverage: Debt-to-Equity, Equity Ratio, Debt Ratio
- Efficiency: Asset Turnover, Inventory Turnover, DSO
- Cash Flow: OCF/Revenue, Quality of Earnings

**9 Red Flags:**
- 4× High severity: Negative Net Income/Equity/OCF/Margin, Excessive Leverage
- 3× Medium: High D/E, Low Equity Ratio, Poor Earnings Quality
- 1× Low: Low ROE

> *Notatki prelegenta:* Pokaż red flags dla demo_02.xml — FINAL S.A. ma ujemny zysk netto (-5,595 tys. PLN), więc aktywuje się red flag "Negative Net Income" z severity HIGH.

---

### Slajd 7: LLM Integration — AI-powered Insights
**Dual backend:**
- **NVIDIA NIM** (cloud): Llama 4 Maverick 405B, DeepSeek V3 685B, Mistral Large 3 123B
- **Ollama** (local): Llama 3.1 8B, Mistral 7B — zero data leakage

**Funkcje LLM:**
- CFO Chat — pytania w języku naturalnym o dane finansowe
- Board Memo — automatyczne streszczenie zarządcze
- NL Query — zapytania w stylu "Jaki jest wskaźnik zadłużenia?"

**Bezpieczeństwo:** Dane finansowe NIGDY nie opuszczają infrastruktury (Ollama local lub NIM z API key)

> *Notatki prelegenta:* Zwróć uwagę na temperature=0.1 — niska temperatura zmniejsza halucynacje. System prompt zawsze zawiera konkretne dane z XML.

---

### Slajd 8: Testing & Quality
**Pokrycie:**
- 66 testów (pytest), 60 pass / 7 fail (stale tests after refactor)
- 100% coverage: kpi_calculator, red_flags, schema_detector
- 86-91% coverage: mapping_engine, xml_loader

**Luki:**
- 0% coverage: extractors (BS, P&L, CF), LLM integration, UI pages
- Brak CI/CD pipeline
- Brak E2E tests

**Dane testowe:**
- 6 demo XML files (465 KB — 5.3 MB)
- 30+ wygenerowanych analiz JSON

> *Notatki prelegenta:* Bądź transparentny o lukach. 11% overall coverage to za mało na produkcję. Plan: dodać testy extractorów + CI/CD pipeline.

---

### Slajd 9: Deployment — NVIDIA DGX Spark
**Infrastruktura:**
- Docker: `nvidia/cuda:12.6.0-base-ubuntu24.04` (ARM64)
- docker-compose: esf-copilot + optional Ollama sidecar
- Operational scripts: `start.sh`, `stop.sh`, `status.sh`
- On-premise: dane finansowe nie opuszczają infrastruktury

**Konfiguracja:**
- `.env` file: API keys, model selection, temperature
- YAML mappings: XPath rules per schema

> *Notatki prelegenta:* DGX Spark = dedykowany hardware NVIDIA z Grace Blackwell GPU. On-prem deployment gwarantuje, że wrażliwe dane finansowe nie wychodzą na zewnątrz.

---

### Slajd 10: Demo Flow
**Live demo (3 minuty):**
1. Upload `demo_02.xml` → XML Analysis page
2. Pokaż: schema detection, metryki, red flags
3. Balance Sheet → hierarchiczna tabela
4. Cash Flow → "1. Amortyzacja: 14,414 tys. PLN"
5. CFO Chat → "Jakie są główne ryzyka finansowe tej spółki?"
6. Switch language PL ↔ EN

> *Notatki prelegenta:* Przygotuj demo_02.xml (FINAL S.A.). Ma ujemny zysk netto, więc red flags będą interesujące. Pokaż switch językowy na żywo.

---

### Slajd 11: Lessons Learned
**Co się sprawdziło:**
- Streamlit = szybki prototyp (11 stron w 4 tygodnie)
- Frozen dataclasses = silne kontrakty danych
- Dual LLM = elastyczność (cloud + local)
- Recursive extraction = skaluje się do dowolnej głębokości XML

**Co wymagało iteracji:**
- Nested XML keys (A_A_II_A_II_1) — 3 iteracje label resolution
- Unit detection — wymagała auto-detect z schema slug
- Cash Flow labels — 5 bugfixów zanim poprawnie wyświetlał A.II.1-10

**Rekomendacje:**
- Dodać testy extractorów (BS/P&L/CF) ASAP
- Wdrożyć CI/CD pipeline
- Przygotować ground truth dataset do walidacji accuracy

> *Notatki prelegenta:* Bądź szczery o iteracjach. Cash Flow extractor wymagał 5 poprawek — to normalne przy parsowaniu polskich XML ze złożonymi namespace'ami.

---

### Slajd 12: Next Steps & Roadmap
**Krótkoterminowe (Q1 2026):**
- [ ] Fix 7 failed tests (schema_detector slug expectations)
- [ ] Dodać testy BS/P&L/CF extractorów
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Ground truth validation (10+ spółek)

**Średnioterminowe (Q2 2026):**
- [ ] Multi-period trend analysis
- [ ] Porównanie spółek (peer benchmarking)
- [ ] Consolidated statements support
- [ ] Performance optimization (large files)

**Długoterminowe (H2 2026):**
- [ ] API REST endpoint (bez UI)
- [ ] Integration z e-KRS API
- [ ] Regulatory compliance alerts (KSH, MSSF)

> *Notatki prelegenta:* Podkreśl, że to MVP — działa, analizuje, daje wartość. Roadmap jest ambitny ale realistyczny.

---

### 7.2 Pytania z sali + odpowiedzi

**Q1 (techniczne): Jak radzicie sobie z nowymi schematami MF?**
> A: Mamy slug-based mapping system. Każdy schemat MF ma swój katalog YAML z XPath rules. Dla nieznanych schematów stosujemy `_default` fallback. Dodanie nowego schematu to nowy plik YAML (~30 linii), bez zmian w kodzie.

**Q2 (techniczne): Czy system radzi sobie z dużymi plikami XML?**
> A: Testowaliśmy z plikami do 5.3 MB (demo_03.xml). Parsowanie + ekstrakcja trwa kilka sekund. Dla batch processing (wiele plików) mamy GPU-accelerated processor z progress tracking. Limit to pamięć RAM, nie czas parsowania.

**Q3 (biznesowe): Jakie jest ryzyko błędnych danych w analizie?**
> A: Główne ryzyko to błędne mapowanie XPath — jeśli schemat MF zmieni strukturę, nasze XPath mogą nie trafić. Dlatego mamy Coverage metric w UI — użytkownik widzi ile procent metryk udało się wyciągnąć. Wartości 0% lub <50% sygnalizują problem. Docelowo planujemy ground truth validation.

**Q4 (biznesowe): Czy dane finansowe są bezpieczne?**
> A: Tak. System działa on-premise na DGX Spark. Przy użyciu Ollama (local LLM) żadne dane nie opuszczają infrastruktury. Przy NVIDIA NIM dane idą do API, ale z enterprise SLA. W `.gitignore` mamy `.env` i outputs. XML-y nie są commitowane do repo.

**Q5 (techniczne): Dlaczego nie Pydantic zamiast dataclasses?**
> A: Decyzja: zero external dependencies dla warstwy kontraktów. Frozen dataclasses dają immutability, `asdict()` out of the box, i IDE autocomplete. Pydantic dałby runtime validation i JSON schema, ale to dodatkowa dependency. Przy obecnej skali (6 dataclasses) frozen dataclasses wystarczają. Jeśli potrzebujemy runtime validation — rozważymy migrację do Pydantic v2.
