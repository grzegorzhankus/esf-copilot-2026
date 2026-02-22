"""
Internationalization (i18n) utilities for cfo-copilot.

Bilingual support for English (EN) and Polish (PL).
Translation dictionary with ~200 keys for complete UI coverage.
"""

from typing import Dict

# Translation dictionary - all UI strings
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Common UI elements
    "language_selector": {"en": "UI Language", "pl": "Język interfejsu"},
    "select_language_help": {"en": "Select user interface language", "pl": "Wybierz język interfejsu"},
    "settings": {"en": "Settings", "pl": "Ustawienia"},
    "display_units": {"en": "Display Units", "pl": "Jednostki wyświetlania"},
    "currency_display": {"en": "Currency display", "pl": "Wyświetlanie waluty"},
    "unit_millions": {"en": "m PLN", "pl": "mln PLN"},
    "unit_thousands": {"en": "thousands PLN", "pl": "tys. PLN"},
    "unit_pln": {"en": "PLN", "pl": "PLN"},

    # App title and branding
    "app_title": {"en": "CFO Copilot", "pl": "CFO Copilot"},
    "app_subtitle": {"en": "Polish Financial Statement Analyzer", "pl": "Analizator Sprawozdań Finansowych"},
    "app_tagline": {"en": "Offline-first • Deterministic • KPIs • Red Flags",
                    "pl": "Offline-first • Deterministyczny • KPI • Czerwone Flagi"},

    # Upload section
    "upload_header": {"en": "Upload Polish Financial Statement (XML)",
                     "pl": "Prześlij Polskie Sprawozdanie Finansowe (XML)"},
    "supported_formats": {"en": "Supported formats:", "pl": "Obsługiwane formaty:"},
    "xml_formats_desc": {"en": "Polish e-Sprawozdania XML files (JednostkaInna, JednostkaMała in PLN or thousands PLN)",
                        "pl": "Polskie pliki XML e-Sprawozdania (JednostkaInna, JednostkaMała w PLN lub tysiącach PLN)"},
    "what_you_get": {"en": "What you'll get:", "pl": "Co otrzymasz:"},
    "feature_kpis": {"en": "Financial KPIs (12+ ratios)", "pl": "Finansowe KPI (12+ wskaźników)"},
    "feature_red_flags": {"en": "Red flags (7+ risk indicators)", "pl": "Czerwone flagi (7+ wskaźników ryzyka)"},
    "feature_analysis": {"en": "P&L, Balance Sheet, Cash Flow analysis",
                        "pl": "Analiza RZiS, Bilansu, Przepływów pieniężnych"},
    "feature_excel": {"en": "Excel export with detailed reports", "pl": "Eksport do Excel ze szczegółowymi raportami"},
    "choose_file": {"en": "Choose XML file", "pl": "Wybierz plik XML"},
    "analyze_button": {"en": "Analyze (deterministic)", "pl": "Analizuj (deterministycznie)"},

    # Status messages
    "analyzing": {"en": "Analyzing financial statement...", "pl": "Analizuję sprawozdanie finansowe..."},
    "parse_error": {"en": "Failed to parse XML file. Please check if it's a valid Polish e-Sprawozdanie.",
                   "pl": "Nie udało się przetworzyć pliku XML. Sprawdź czy to poprawne polskie e-Sprawozdanie."},
    "analysis_complete": {"en": "Analysis complete! Navigate to other pages to view results.",
                         "pl": "Analiza zakończona! Przejdź do innych stron aby zobaczyć wyniki."},
    "analysis_ready": {"en": "Analysis Ready", "pl": "Analiza Gotowa"},
    "no_file_selected": {"en": "No file selected", "pl": "Nie wybrano pliku"},

    # Metrics labels
    "kpis_calculated": {"en": "KPIs Calculated", "pl": "Obliczone KPI"},
    "red_flags_metric": {"en": "Red Flags", "pl": "Czerwone Flagi"},
    "company": {"en": "Company", "pl": "Firma"},
    "period_end": {"en": "Period End", "pl": "Koniec Okresu"},

    # Pages - Overview
    "overview_title": {"en": "Financial Overview", "pl": "Przegląd Finansowy"},
    "no_analysis_warning": {"en": "No analysis loaded. Please upload and analyze an XML file first.",
                           "pl": "Brak załadowanej analizy. Najpierw prześlij i przeanalizuj plik XML."},
    "go_to_home": {"en": "Go to the Home page to upload a file.", "pl": "Przejdź do strony głównej aby przesłać plik."},
    "go_home_upload": {"en": "Go to the **Home** page to upload a file.", "pl": "Przejdź do strony **głównej** aby przesłać plik."},
    "quick_ratios": {"en": "Quick Ratios (Current Period)", "pl": "Szybkie Wskaźniki (Obecny Okres)"},
    "liquidity": {"en": "Liquidity", "pl": "Płynność"},
    "capital_structure": {"en": "Capital Structure", "pl": "Struktura Kapitału"},
    "profitability": {"en": "Profitability", "pl": "Rentowność"},
    "all_kpis": {"en": "All Calculated KPIs", "pl": "Wszystkie Obliczone KPI"},
    "red_flags_section": {"en": "Red Flags", "pl": "Czerwone Flagi"},
    "red_flags_detected": {"en": "red flag(s) detected:", "pl": "wykrytych czerwonych flag:"},
    "no_red_flags": {"en": "No red flags detected. All metrics look healthy.",
                    "pl": "Nie wykryto czerwonych flag. Wszystkie wskaźniki wyglądają dobrze."},
    "financial_summary": {"en": "Financial Summary", "pl": "Podsumowanie Finansowe"},
    "revenue": {"en": "Revenue", "pl": "Przychody"},
    "net_profit": {"en": "Net Profit", "pl": "Zysk Netto"},
    "equity": {"en": "Equity", "pl": "Kapitał Własny"},
    "as_of": {"en": "As of", "pl": "Na dzień"},
    "currency": {"en": "Currency", "pl": "Waluta"},
    "line_item": {"en": "Line Item", "pl": "Pozycja"},
    "current": {"en": "Current", "pl": "Bieżący"},
    "prior": {"en": "Prior", "pl": "Poprzedni"},
    "change": {"en": "Change", "pl": "Zmiana"},
    "positive": {"en": "Positive", "pl": "Dodatni"},
    "negative": {"en": "Negative", "pl": "Ujemny"},

    # Pages - P&L
    "pl_title": {"en": "Profit & Loss Statement", "pl": "Rachunek Zysków i Strat"},
    "pl_subtitle": {"en": "Rachunek Zysków i Strat (RZiS)", "pl": "Rachunek Zysków i Strat (RZiS)"},
    "no_pl_data": {"en": "No P&L data available in this financial statement.",
                  "pl": "Brak danych RZiS w tym sprawozdaniu finansowym."},
    "key_pl_metrics": {"en": "Key P&L Metrics", "pl": "Kluczowe Wskaźniki RZiS"},
    "data_source_rzis": {"en": "Data source: Polish e-Sprawozdanie XML (RZiS)",
                        "pl": "Źródło danych: Polskie e-Sprawozdanie XML (RZiS)"},

    # Pages - Balance Sheet
    "balance_sheet_title": {"en": "Balance Sheet", "pl": "Bilans"},
    "balance_sheet_subtitle": {"en": "Bilans", "pl": "Bilans"},
    "balance_sheet_summary": {"en": "Balance Sheet Summary", "pl": "Podsumowanie Bilansu"},
    "key_balance_sheet_metrics": {"en": "Key Balance Sheet Metrics", "pl": "Kluczowe Wskaźniki Bilansu"},
    "no_balance_sheet_data": {"en": "No Balance Sheet data available in this financial statement.",
                             "pl": "Brak danych Bilansu w tym sprawozdaniu finansowym."},
    "data_source_balance_sheet": {"en": "Data source: Polish e-Sprawozdanie XML (Bilans)",
                                 "pl": "Źródło danych: Polskie e-Sprawozdanie XML (Bilans)"},
    "bs_title": {"en": "Balance Sheet", "pl": "Bilans"},
    "bs_subtitle": {"en": "Bilans", "pl": "Bilans"},
    "total_assets_label": {"en": "Total Assets (Aktywa razem)", "pl": "Aktywa razem"},
    "equity_label": {"en": "Equity (Kapitał własny)", "pl": "Kapitał własny"},
    "total_liabilities_label": {"en": "Total Liabilities (Zobowiązania razem)",
                               "pl": "Zobowiązania razem"},
    "current_assets_label": {"en": "Current Assets (Aktywa obrotowe)", "pl": "Aktywa obrotowe"},
    "current_liabilities_label": {"en": "Current Liabilities (Zobowiązania krótkoterminowe)",
                                 "pl": "Zobowiązania krótkoterminowe"},
    "key_bs_metrics": {"en": "Key Balance Sheet Metrics", "pl": "Kluczowe Wskaźniki Bilansu"},
    "total_assets": {"en": "Total Assets (Aktywa razem)", "pl": "Aktywa razem"},
    "total_liabilities": {"en": "Total Liabilities (Zobowiązania razem)", "pl": "Zobowiązania razem"},
    "total_equity": {"en": "Total Equity (Kapitał własny)", "pl": "Kapitał własny"},
    "current_assets": {"en": "Current Assets (Aktywa obrotowe)", "pl": "Aktywa obrotowe"},
    "current_liabilities": {"en": "Current Liabilities (Zobowiązania krótkoterminowe)", "pl": "Zobowiązania krótkoterminowe"},
    "net_assets": {"en": "Net Assets", "pl": "Aktywa Netto"},

    # Pages - Analysis Log
    "analysis_log_title": {"en": "Analysis Log", "pl": "Dziennik Analizy"},
    "analysis_log_subtitle": {"en": "Technical Details & Metadata", "pl": "Szczegóły Techniczne i Metadane"},
    "analysis_metadata": {"en": "Analysis Metadata", "pl": "Metadane Analizy"},
    "company_information": {"en": "Company Information:", "pl": "Informacje o firmie:"},
    "period_from": {"en": "Period From:", "pl": "Okres Od:"},
    "period_to": {"en": "Period To:", "pl": "Okres Do:"},
    "schema_information": {"en": "Schema Information:", "pl": "Informacje o Schemacie:"},
    "schema_id": {"en": "Schema ID:", "pl": "ID Schematu:"},
    "schema_namespace": {"en": "Schema Namespace:", "pl": "Namespace Schematu:"},
    "mapping_path": {"en": "Mapping Path:", "pl": "Ścieżka Mappingu:"},
    "fallback_mapping": {"en": "Fallback Mapping:", "pl": "Fallback Mapping:"},
    "data_coverage": {"en": "Data Coverage", "pl": "Pokrycie Danych"},
    "coverage": {"en": "Coverage", "pl": "Pokrycie"},
    "metrics_present": {"en": "Metrics Present", "pl": "Metryki Obecne"},
    "metrics_missing": {"en": "Metrics Missing", "pl": "Brakujące Metryki"},
    "raw_data_inspection": {"en": "Raw Data Inspection", "pl": "Inspekcja Surowych Danych"},
    "export_options": {"en": "Export Options", "pl": "Opcje Eksportu"},
    "analysis_timestamp": {"en": "Analysis Timestamp", "pl": "Znacznik Czasowy Analizy"},
    "view_missing_metrics": {"en": "View Missing Metrics", "pl": "Zobacz Brakujące Metryki"},
    "missing_metrics_desc": {"en": "The following metrics were not found in the XML:",
                            "pl": "Następujące metryki nie zostały znalezione w XML:"},
    "tab_analysis_result": {"en": "Analysis Result", "pl": "Wynik Analizy"},
    "tab_parsed_data": {"en": "Parsed Data", "pl": "Przetworzone Dane"},
    "tab_metadata": {"en": "Metadata", "pl": "Metadane"},
    "full_analysis_result": {"en": "Full Analysis Result (JSON):", "pl": "Pełny Wynik Analizy (JSON):"},
    "parsed_financial_data": {"en": "Parsed Financial Statement Data:", "pl": "Przetworzone Dane Sprawozdania Finansowego:"},
    "metadata_details": {"en": "Metadata Details:", "pl": "Szczegóły Metadanych:"},
    "download_analysis_json": {"en": "Download Analysis JSON", "pl": "Pobierz Analizę JSON"},
    "download_parsed_json": {"en": "Download Parsed Data JSON", "pl": "Pobierz Przetworzone Dane JSON"},
    "download_json_button": {"en": "Download JSON", "pl": "Pobierz JSON"},
    "download_parsed_data_button": {"en": "Download Parsed Data", "pl": "Pobierz Przetworzone Dane"},
    "cfo_copilot_version": {"en": "CFO Copilot v2.0.0 • Analysis Engine", "pl": "CFO Copilot v2.0.0 • Silnik Analizy"},
    "yes_warning": {"en": "Yes", "pl": "Tak"},
    "no_ok": {"en": "No", "pl": "Nie"},

    # Pages - Board Memo
    "board_memo_title": {"en": "Board Memo", "pl": "Board Memo"},
    "board_memo_subtitle": {"en": "AI-Generated Executive Summary", "pl": "Podsumowanie Wykonawcze Generowane przez AI"},
    "board_memo_coming_soon": {"en": "Board Memo Feature (Coming Soon)",
                              "pl": "Funkcja Board Memo (Wkrótce)"},
    "planned_features": {"en": "Planned features:", "pl": "Planowane funkcje:"},
    "feature_exec_summary": {"en": "Executive summary of financial performance",
                            "pl": "Podsumowanie wykonawcze wyników finansowych"},
    "feature_highlights": {"en": "Key highlights and concerns", "pl": "Kluczowe osiągnięcia i obawy"},
    "feature_recommendations": {"en": "Strategic recommendations", "pl": "Rekomendacje strategiczne"},
    "feature_llm_powered": {"en": "Powered by local LLM (Ollama)", "pl": "Zasilane przez lokalny LLM (Ollama)"},

    # Pages - CFO Chat
    "cfo_chat_title": {"en": "CFO Chat", "pl": "Chat CFO"},
    "cfo_chat_subtitle": {"en": "Interactive Q&A About Your Financials",
                         "pl": "Interaktywne Q&A o Twoich Finansach"},
    "cfo_chat_coming_soon": {"en": "CFO Chat Feature (Coming Soon)", "pl": "Funkcja Chat CFO (Wkrótce)"},
    "install_ollama": {"en": "To use this feature, install Ollama:", "pl": "Aby użyć tej funkcji, zainstaluj Ollama:"},
    "cfo_chat_qa_about_financials": {"en": "Interactive Q&A About Your Financials (LLM)",
                                      "pl": "Interaktywne Q&A o Twoich Finansach (LLM)"},
    "chatting_about": {"en": "Chatting about", "pl": "Rozmawiamy o"},
    "analyzed_at": {"en": "analyzed", "pl": "przeanalizowano"},
    "chat_interface_title": {"en": "Chat Interface", "pl": "Interfejs Czatu"},
    "you_label": {"en": "You", "pl": "Ty"},
    "cfo_assistant_label": {"en": "CFO Assistant", "pl": "Asystent CFO"},
    "cfo_chat_coming_feature": {"en": "CFO Chat Feature (Coming Soon)", "pl": "Funkcja Chat CFO (Wkrótce)"},
    "cfo_chat_description": {"en": "This page will provide an interactive chat interface to ask questions about your financial statements using a local LLM (Ollama).",
                            "pl": "Ta strona będzie zawierać interaktywny interfejs czatu do zadawania pytań o Twoje sprawozdania finansowe za pomocą lokalnego LLM (Ollama)."},
    "example_questions": {"en": "Example questions you'll be able to ask:", "pl": "Przykładowe pytania, które będziesz mógł zadać:"},
    "example_q1": {"en": "\"What is the company's liquidity position?\"", "pl": "\"Jaka jest płynność finansowa firmy?\""},
    "example_q2": {"en": "\"Explain the trend in profitability\"", "pl": "\"Wyjaśnij trend w rentowności\""},
    "example_q3": {"en": "\"What are the main concerns in this financial statement?\"", "pl": "\"Jakie są główne obawy w tym sprawozdaniu finansowym?\""},
    "example_q4": {"en": "\"Compare revenue vs prior period\"", "pl": "\"Porównaj przychody z poprzednim okresem\""},
    "example_q5": {"en": "\"Is the company at risk of insolvency?\"", "pl": "\"Czy firma jest zagrożona niewypłacalnością?\""},
    "to_enable_feature": {"en": "To enable this feature:", "pl": "Aby włączyć tę funkcję:"},
    "step_1_install": {"en": "Install Ollama: `https://ollama.ai`", "pl": "Zainstaluj Ollama: `https://ollama.ai`"},
    "step_2_pull_model": {"en": "Pull a model: `ollama pull llama3.1:8b` or `ollama pull nemotron-3-nano`", "pl": "Pobierz model: `ollama pull llama3.1:8b` lub `ollama pull nemotron-3-nano`"},
    "step_3_env_vars": {"en": "Set environment variables: `OLLAMA_URL=http://localhost:11434` and `OLLAMA_MODEL=llama3.1:8b` (or `nemotron-3-nano`)", "pl": "Ustaw zmienne środowiskowe: `OLLAMA_URL=http://localhost:11434` i `OLLAMA_MODEL=llama3.1:8b` (lub `nemotron-3-nano`)"},
    "step_4_restart": {"en": "Restart the application", "pl": "Uruchom ponownie aplikację"},
    "for_now_explore": {"en": "For now, you can explore the data in other pages:", "pl": "Na razie możesz eksplorować dane na innych stronach:"},
    "page_overview": {"en": "Overview - KPIs and red flags", "pl": "Przegląd - KPI i czerwone flagi"},
    "page_pl": {"en": "P&L - Income statement", "pl": "RZiS - Rachunek zysków i strat"},
    "page_bs": {"en": "Balance Sheet - Assets and liabilities", "pl": "Bilans - Aktywa i zobowiązania"},
    "page_log": {"en": "Analysis Log - Raw data", "pl": "Dziennik Analizy - Surowe dane"},
    "chat_interface": {"en": "Chat Interface (Placeholder)", "pl": "Interfejs Czatu (Placeholder)"},
    "ask_question": {"en": "Ask a question about the financials:", "pl": "Zadaj pytanie o finanse:"},
    "your_question": {"en": "Your question:", "pl": "Twoje pytanie:"},
    "ask_placeholder": {"en": "Ask anything about your financial statements...", "pl": "Zapytaj o cokolwiek dotyczące sprawozdań finansowych..."},
    "send_button": {"en": "Send", "pl": "Wyślij"},
    "thinking_label": {"en": "Thinking", "pl": "Myślę"},
    "load_analysis_instruction": {"en": "Please load an analysis file from the sidebar to start chatting", "pl": "Wczytaj plik analizy z panelu bocznego, aby rozpocząć rozmowę"},
    "powered_by_ollama": {"en": "Powered by Ollama LLM", "pl": "Zasilane przez Ollama LLM"},
    "llm_integration_note": {"en": "LLM integration not yet enabled. Please install Ollama to use this feature.",
                            "pl": "Integracja LLM nie jest jeszcze włączona. Zainstaluj Ollama, aby użyć tej funkcji."},
    "note_full_llm": {"en": "Note: Full LLM integration requires Ollama installation (optional).",
                     "pl": "Uwaga: Pełna integracja LLM wymaga instalacji Ollama (opcjonalne)."},

    # KPI Names - Official Polish Terms
    "kpi_current_ratio": {"en": "Current Ratio", "pl": "Wskaźnik Bieżącej Płynności"},
    "kpi_quick_ratio": {"en": "Quick Ratio", "pl": "Wskaźnik Szybkiej Płynności"},
    "kpi_debt_to_equity": {"en": "Debt-to-Equity", "pl": "Zadłużenie do Kapitału Własnego"},
    "kpi_roe": {"en": "ROE (Return on Equity)", "pl": "ROE (Zwrot z Kapitału Własnego)"},
    "kpi_roa": {"en": "ROA (Return on Assets)", "pl": "ROA (Zwrot z Aktywów)"},
    "kpi_net_margin": {"en": "Net Margin", "pl": "Marża Zysku Netto"},
    "kpi_ebit_margin": {"en": "EBIT Margin", "pl": "Marża EBIT"},
    "kpi_gross_margin": {"en": "Gross Margin", "pl": "Marża Brutto"},
    "kpi_interest_coverage": {"en": "Interest Coverage", "pl": "Pokrycie Odsetek"},
    "kpi_dso": {"en": "DSO (Days Sales Outstanding)", "pl": "DSO (Dni Zaległości Należności)"},
    "kpi_inventory_days": {"en": "Inventory Days", "pl": "Dni Zapasów"},
    "kpi_net_debt_to_ebitda": {"en": "Net Debt / EBITDA", "pl": "Zadłużenie Netto / EBITDA"},

    # Red Flags - Descriptions
    "rf_001_neg_equity": {"en": "Negative Equity", "pl": "Ujemny Kapitał Własny"},
    "rf_001_neg_equity_desc": {"en": "Equity is negative.", "pl": "Kapitał własny jest ujemny."},

    "rf_002_low_liquidity": {"en": "Low Liquidity", "pl": "Niska Płynność"},
    "rf_002_low_liquidity_desc": {"en": "Current ratio below 1.0 indicates short-term liquidity pressure.",
                                 "pl": "Wskaźnik bieżącej płynności poniżej 1.0 wskazuje na presję płynnościową."},

    "rf_003_weak_interest_cover": {"en": "Weak Interest Coverage", "pl": "Słabe Pokrycie Odsetek"},
    "rf_003_weak_interest_cover_desc": {"en": "EBIT does not cover interest expense adequately.",
                                       "pl": "EBIT nie pokrywa odpowiednio wydatków odsetkowych."},

    "rf_004_high_leverage": {"en": "High Leverage", "pl": "Wysokie Zadłużenie"},
    "rf_004_high_leverage_desc": {"en": "Net debt to EBITDA is above 4.0.",
                                 "pl": "Zadłużenie netto do EBITDA jest powyżej 4.0."},

    "rf_005_accruals": {"en": "Accruals Warning", "pl": "Ostrzeżenie Memoriałowe"},
    "rf_005_accruals_desc": {"en": "Net income is positive but operating cash flow is negative.",
                            "pl": "Zysk netto jest dodatni, ale przepływy z działalności operacyjnej ujemne."},

    "rf_006_cash_burn": {"en": "Cash Burn", "pl": "Spalanie Gotówki"},
    "rf_006_cash_burn_desc": {"en": "Cash is declining and cash buffer is low.",
                             "pl": "Gotówka maleje, a bufor gotówkowy jest niski."},

    "rf_007_dso_high": {"en": "High DSO", "pl": "Wysokie DSO"},
    "rf_007_dso_high_desc": {"en": "Days Sales Outstanding above 90 days.",
                            "pl": "Dni zaległości należności powyżej 90 dni."},

    "rf_008_inventory_days_high": {"en": "High Inventory Days", "pl": "Wysokie Dni Zapasów"},
    "rf_008_inventory_days_high_desc": {"en": "Inventory days above 120.",
                                       "pl": "Dni zapasów powyżej 120."},

    "rf_009_gross_margin_low": {"en": "Low Gross Margin", "pl": "Niska Marża Brutto"},
    "rf_009_gross_margin_low_desc": {"en": "Gross margin below 5%.",
                                    "pl": "Marża brutto poniżej 5%."},

    "rf_010_low_coverage": {"en": "Low Data Coverage", "pl": "Niskie Pokrycie Danych"},
    "rf_010_low_coverage_desc": {"en": "Coverage below 80%; KPIs may be incomplete.",
                                "pl": "Pokrycie poniżej 80%; KPI mogą być niekompletne."},

    "rf_012_ebitda_quality": {"en": "EBITDA Quality", "pl": "Jakość EBITDA"},
    "rf_012_ebitda_quality_desc": {"en": "Operating cash flow is weak versus EBITDA.",
                                  "pl": "Przepływy z działalności operacyjnej są słabe w stosunku do EBITDA."},

    # Traffic Light Labels
    "traffic_light_ok": {"en": "OK", "pl": "OK"},
    "traffic_light_watch": {"en": "Watch", "pl": "Obserwuj"},
    "traffic_light_risk": {"en": "Risk", "pl": "Ryzyko"},
    "traffic_light_na": {"en": "n/a", "pl": "b/d"},

    # P&L Labels (RZiS - Kalkulacyjny variant)
    "rzis_label_a": {"en": "Net revenue (A)", "pl": "Przychody netto (A)"},
    "rzis_label_b": {"en": "Cost of goods sold (B)", "pl": "Koszt wytworzenia sprzedanych produktów (B)"},
    "rzis_label_c": {"en": "Gross profit (C = A - B)", "pl": "Zysk brutto ze sprzedaży (C = A - B)"},
    "rzis_label_d": {"en": "Operating expenses (D)", "pl": "Koszty ogólnego zarządu (D)"},
    "rzis_label_e": {"en": "Other operating income (E)", "pl": "Pozostałe przychody operacyjne (E)"},
    "rzis_label_f": {"en": "Other operating expenses (F)", "pl": "Pozostałe koszty operacyjne (F)"},
    "rzis_label_g": {"en": "EBIT (G = C - D + E - F)", "pl": "EBIT (G = C - D + E - F)"},
    "rzis_label_h": {"en": "Financial income (H)", "pl": "Przychody finansowe (H)"},
    "rzis_label_i": {"en": "Financial expenses (I)", "pl": "Koszty finansowe (I)"},
    "rzis_label_j": {"en": "EBT (J = G + H - I)", "pl": "EBT (J = G + H - I)"},
    "rzis_label_k": {"en": "Tax (K)", "pl": "Podatek dochodowy (K)"},
    "rzis_label_l": {"en": "Net income (L = J - K)", "pl": "Zysk netto (L = J - K)"},

    # Common buttons
    "ok": {"en": "OK", "pl": "OK"},
    "cancel": {"en": "Cancel", "pl": "Anuluj"},
    "save": {"en": "Save", "pl": "Zapisz"},
    "export": {"en": "Export", "pl": "Eksportuj"},
    "download": {"en": "Download", "pl": "Pobierz"},
    "upload": {"en": "Upload", "pl": "Prześlij"},
    "close": {"en": "Close", "pl": "Zamknij"},
    "back": {"en": "Back", "pl": "Wstecz"},
    "next": {"en": "Next", "pl": "Dalej"},
    "yes": {"en": "Yes", "pl": "Tak"},
    "no": {"en": "No", "pl": "Nie"},

    # LLM Integration - Board Memo
    "generate_board_memo": {"en": "Generate Board Memo", "pl": "Generuj Board Memo"},
    "generated_board_memo": {"en": "Generated Board Memo", "pl": "Wygenerowane Board Memo"},
    "generating_board_memo": {"en": "Generating Board Memo...", "pl": "Generuję Board Memo..."},

    # LLM Integration - CFO Chat
    "thinking": {"en": "Thinking...", "pl": "Myślę..."},
    "clear_chat_history": {"en": "Clear Chat History", "pl": "Wyczyść Historię Czatu"},
    "llm_settings": {"en": "LLM Settings", "pl": "Ustawienia LLM"},
    "model": {"en": "Model", "pl": "Model"},
    "ollama_connected": {"en": "Ollama connected", "pl": "Ollama połączona"},
    "models_available": {"en": "models available", "pl": "dostępnych modeli"},

    # esf-copilot-2026 Specific Translations
    # Home Page
    "welcome_title": {"en": "Welcome to e-SF Copilot v2.0", "pl": "Witaj w e-SF Copilot v2.0"},
    "welcome_subtitle": {"en": "Your AI-powered assistant for analyzing Polish financial statements (e-Sprawozdania).",
                         "pl": "Twój asystent AI do analizy polskich sprawozdań finansowych (e-Sprawozdania)."},
    "analysis_processing": {"en": "Analysis & Processing", "pl": "Analiza i Przetwarzanie"},
    "ai_powered_insights": {"en": "AI-Powered Insights", "pl": "Wnioski Wspomagane AI"},
    "detailed_views": {"en": "Detailed Views (from v2.0.0)", "pl": "Szczegółowe Widoki (z v2.0.0)"},
    "getting_started_title": {"en": "Getting Started", "pl": "Rozpoczęcie Pracy"},
    "built_with": {"en": "Built with Streamlit and AI | Integrated v2.0.0 + v2026 Features",
                   "pl": "Zbudowane za pomocą Streamlit i AI | Zintegrowane funkcje v2.0.0 + v2026"},
    "select_page_sidebar": {"en": "Select a page from the sidebar to get started",
                           "pl": "Wybierz stronę z panelu bocznego, aby rozpocząć"},

    # Feature Descriptions
    "feature_xml_analysis": {"en": "XML Analysis: Upload and analyze e-Sprawozdania XML files with KPIs and red flags",
                             "pl": "Analiza XML: Prześlij i analizuj pliki XML e-Sprawozdania z KPI i czerwonymi flagami"},
    "feature_batch_processing": {"en": "Batch Processing: Process multiple XML files simultaneously",
                                 "pl": "Przetwarzanie wsadowe: Przetwarzaj wiele plików XML jednocześnie"},
    "feature_forecasting": {"en": "Forecasting: Project future financial performance with scenario analysis",
                           "pl": "Prognozowanie: Przewiduj przyszłe wyniki finansowe z analizą scenariuszy"},
    "feature_cfo_chat": {"en": "CFO Chat: Interactive chat with AI financial advisor (Ollama-powered)",
                        "pl": "Chat CFO: Interaktywny czat z doradcą finansowym AI (zasilany przez Ollama)"},
    "feature_overview_desc": {"en": "Overview: KPIs and red flags dashboard",
                             "pl": "Przegląd: Panel KPI i czerwonych flag"},
    "feature_pl_desc": {"en": "P&L: Profit & Loss statement analysis",
                       "pl": "RZiS: Analiza rachunku zysków i strat"},
    "feature_bs_desc": {"en": "Balance Sheet: Asset and liability breakdown",
                       "pl": "Bilans: Rozbicie aktywów i zobowiązań"},
    "feature_log_desc": {"en": "Analysis Log: Raw data and parsing details",
                        "pl": "Dziennik Analizy: Surowe dane i szczegóły parsowania"},
    "feature_memo_desc": {"en": "Board Memo: Executive summary generator",
                         "pl": "Board Memo: Generator podsumowania wykonawczego"},

    # Getting Started Steps
    "step_upload_xml": {"en": "Upload XML: Go to XML Analysis page and upload a financial statement",
                       "pl": "Prześlij XML: Przejdź do strony Analiza XML i prześlij sprawozdanie finansowe"},
    "step_view_reports": {"en": "View Reports: Navigate to Overview, P&L, or Balance Sheet for detailed analysis",
                         "pl": "Zobacz Raporty: Przejdź do Przeglądu, RZiS lub Bilansu dla szczegółowej analizy"},
    "step_ai_chat": {"en": "AI Chat: Use CFO Chat to ask questions about your data",
                    "pl": "Chat AI: Użyj Chat CFO, aby zadawać pytania o swoje dane"},
    "step_batch_process": {"en": "Batch Process: Upload multiple files for comparative analysis",
                          "pl": "Przetwarzanie wsadowe: Prześlij wiele plików do analizy porównawczej"},
    "step_forecast": {"en": "Forecast: Project future performance based on current data",
                     "pl": "Prognozuj: Przewiduj przyszłe wyniki na podstawie bieżących danych"},

    # XML Analysis Page
    "xml_analysis_title": {"en": "XML Analysis", "pl": "Analiza XML"},
    "upload_analyze_xml": {"en": "Upload one XML to detect schema_id and generate minimal analysis.json.",
                          "pl": "Prześlij jeden plik XML, aby wykryć schema_id i wygenerować minimalną analizę.json."},
    "xml_file": {"en": "XML file", "pl": "Plik XML"},
    "analyze_button_text": {"en": "Analyze", "pl": "Analizuj"},
    "please_upload_xml": {"en": "Please upload an XML file first.", "pl": "Najpierw prześlij plik XML."},
    "analysis_complete_msg": {"en": "Analysis complete.", "pl": "Analiza zakończona."},
    "saved": {"en": "Saved", "pl": "Zapisano"},
    "no_mapping_found": {"en": "No mapping found for this schema_id_slug. Add mapping_v1.yaml to configs/mappings/<slug>/.",
                        "pl": "Nie znaleziono mapowania dla tego schema_id_slug. Dodaj mapping_v1.yaml do configs/mappings/<slug>/."},
    "xml_error": {"en": "XML error", "pl": "Błąd XML"},
    "unexpected_error": {"en": "Unexpected error", "pl": "Nieoczekiwany błąd"},
    "export_options_title": {"en": "Export Options", "pl": "Opcje Eksportu"},
    "download_excel_report": {"en": "Download Excel Report", "pl": "Pobierz Raport Excel"},
    "download_pdf": {"en": "Download PDF", "pl": "Pobierz PDF"},
    "download_json_file": {"en": "Download JSON", "pl": "Pobierz JSON"},
    "financial_health_score": {"en": "Financial Health Score", "pl": "Wynik Zdrowia Finansowego"},
    "financial_visualizations": {"en": "Financial Visualizations", "pl": "Wizualizacje Finansowe"},
    "key_performance_indicators": {"en": "Key Performance Indicators", "pl": "Kluczowe Wskaźniki Wydajności"},
    "base_metrics_title": {"en": "Base Metrics", "pl": "Podstawowe Metryki"},
    "red_flags_analysis": {"en": "Red Flags Analysis", "pl": "Analiza Czerwonych Flag"},
    "high_severity": {"en": "High Severity", "pl": "Wysoka Dotkliwość"},
    "medium_severity": {"en": "Medium Severity", "pl": "Średnia Dotkliwość"},
    "low_severity": {"en": "Low Severity", "pl": "Niska Dotkliwość"},
    "red_flags_detected_count": {"en": "red flag(s) detected!", "pl": "wykrytych czerwonych flag!"},
    "no_red_flags_all_checks_passed": {"en": "No red flags detected! All checks passed.",
                                       "pl": "Nie wykryto czerwonych flag! Wszystkie testy przeszły pomyślnie."},
    "view_all_checks": {"en": "View All Checks", "pl": "Zobacz Wszystkie Testy"},

    # Batch Processing Page
    "batch_processing_title": {"en": "Batch Processing", "pl": "Przetwarzanie Wsadowe"},
    "upload_analyze_multiple": {"en": "Upload and analyze multiple XML files at once.",
                               "pl": "Prześlij i analizuj wiele plików XML jednocześnie."},
    "upload_xml_files": {"en": "Upload XML files", "pl": "Prześlij pliki XML"},
    "files_selected": {"en": "file(s) selected", "pl": "wybranych plików"},
    "selected_files": {"en": "Selected Files", "pl": "Wybrane Pliki"},
    "filename": {"en": "Filename", "pl": "Nazwa pliku"},
    "size_kb": {"en": "Size (KB)", "pl": "Rozmiar (KB)"},
    "processing_options": {"en": "Processing Options", "pl": "Opcje Przetwarzania"},
    "save_json_outputs": {"en": "Save JSON outputs", "pl": "Zapisz wyjścia JSON"},
    "create_excel_reports": {"en": "Create Excel reports", "pl": "Utwórz raporty Excel"},
    "create_summary_report": {"en": "Create summary report", "pl": "Utwórz raport podsumowujący"},
    "create_batch_export_zip": {"en": "Create batch export (ZIP)", "pl": "Utwórz eksport wsadowy (ZIP)"},
    "analyze_all_files": {"en": "Analyze All Files", "pl": "Analizuj Wszystkie Pliki"},
    "processing_file": {"en": "Processing", "pl": "Przetwarzanie"},
    "completed_processed": {"en": "Completed! Processed", "pl": "Zakończono! Przetworzono"},
    "files_successfully": {"en": "files successfully", "pl": "plików pomyślnie"},
    "files_had_errors": {"en": "file(s) had errors", "pl": "plików miało błędy"},
    "view_errors": {"en": "View Errors", "pl": "Zobacz Błędy"},
    "summary_report_title": {"en": "Summary Report", "pl": "Raport Podsumowujący"},
    "schema": {"en": "Schema", "pl": "Schemat"},
    "coverage_percent": {"en": "Coverage (%)", "pl": "Pokrycie (%)"},
    "kpis_calculated_count": {"en": "KPIs Calculated", "pl": "Obliczone KPI"},
    "red_flags_count": {"en": "Red Flags", "pl": "Czerwone Flagi"},
    "total_files": {"en": "Total Files", "pl": "Łączna liczba plików"},
    "avg_coverage": {"en": "Avg Coverage", "pl": "Średnie Pokrycie"},
    "total_red_flags": {"en": "Total Red Flags", "pl": "Łączna liczba czerwonych flag"},
    "files_with_flags": {"en": "Files with Flags", "pl": "Pliki z Flagami"},
    "download_summary_csv": {"en": "Download Summary CSV", "pl": "Pobierz Podsumowanie CSV"},
    "batch_export_title": {"en": "Batch Export", "pl": "Eksport Wsadowy"},
    "creating_batch_export": {"en": "Creating batch export...", "pl": "Tworzenie eksportu wsadowego..."},
    "download_batch_export_zip": {"en": "Download Batch Export (ZIP)", "pl": "Pobierz Eksport Wsadowy (ZIP)"},
    "individual_results": {"en": "Individual Results", "pl": "Indywidualne Wyniki"},
    "please_upload_xml_files": {"en": "Please upload XML files to begin batch processing",
                               "pl": "Prześlij pliki XML, aby rozpocząć przetwarzanie wsadowe"},
    "how_to_use_batch": {"en": "How to use Batch Processing", "pl": "Jak korzystać z Przetwarzania Wsadowego"},
    "batch_benefits": {"en": "Benefits", "pl": "Korzyści"},
    "time_saving": {"en": "Time-Saving: Analyze multiple companies at once",
                   "pl": "Oszczędność czasu: Analizuj wiele firm jednocześnie"},
    "comparison": {"en": "Comparison: Compare financial health across multiple entities",
                  "pl": "Porównanie: Porównaj zdrowie finansowe w wielu podmiotach"},
    "batch_export_desc": {"en": "Batch Export: Download all reports in one ZIP file",
                         "pl": "Eksport wsadowy: Pobierz wszystkie raporty w jednym pliku ZIP"},
    "summary_report_desc": {"en": "Summary Report: Get high-level overview of all analyzed files",
                           "pl": "Raport podsumowujący: Uzyskaj przegląd wysokiego poziomu wszystkich analizowanych plików"},

    # Forecasting Page
    "forecasting_title": {"en": "Financial Forecasting", "pl": "Prognozowanie Finansowe"},
    "project_future_performance": {"en": "Project future financial performance based on current data.",
                                  "pl": "Przewiduj przyszłe wyniki finansowe na podstawie bieżących danych."},
    "load_analysis_title": {"en": "Load Analysis", "pl": "Załaduj Analizę"},
    "select_analysis_file": {"en": "Select analysis file:", "pl": "Wybierz plik analizy:"},
    "load_analysis_button": {"en": "Load Analysis", "pl": "Załaduj Analizę"},
    "no_analysis_files_found": {"en": "No analysis files found.", "pl": "Nie znaleziono plików analizy."},
    "no_outputs_directory": {"en": "No outputs directory found.", "pl": "Nie znaleziono katalogu outputs."},
    "parameters": {"en": "Parameters", "pl": "Parametry"},
    "expected_growth_rate": {"en": "Expected Growth Rate (%)", "pl": "Oczekiwana Stopa Wzrostu (%)"},
    "forecasting_for": {"en": "Forecasting for", "pl": "Prognozowanie dla"},
    "no_metrics_for_forecasting": {"en": "No metrics available for forecasting.",
                                  "pl": "Brak metryk dostępnych do prognozowania."},
    "forecast_summary_title": {"en": "Forecast Summary", "pl": "Podsumowanie Prognozy"},
    "forecasts_generated": {"en": "Forecasts Generated", "pl": "Wygenerowane Prognozy"},
    "avg_growth_rate": {"en": "Avg Growth Rate", "pl": "Średnia Stopa Wzrostu"},
    "high_confidence": {"en": "High Confidence", "pl": "Wysoka Pewność"},
    "medium_confidence": {"en": "Medium Confidence", "pl": "Średnia Pewność"},
    "forecast_charts": {"en": "Forecast Charts", "pl": "Wykresy Prognoz"},
    "current_value": {"en": "Current", "pl": "Bieżąca"},
    "year_1": {"en": "Year 1", "pl": "Rok 1"},
    "year_2": {"en": "Year 2", "pl": "Rok 2"},
    "year_3": {"en": "Year 3", "pl": "Rok 3"},
    "method": {"en": "Method", "pl": "Metoda"},
    "confidence": {"en": "Confidence", "pl": "Pewność"},
    "growth_rate": {"en": "Growth Rate", "pl": "Stopa Wzrostu"},
    "scenario_analysis_title": {"en": "Scenario Analysis", "pl": "Analiza Scenariuszy"},
    "select_metric_for_scenario": {"en": "Select metric for scenario comparison:",
                                  "pl": "Wybierz metrykę do porównania scenariuszy:"},
    "best_case": {"en": "Best Case (+15%)", "pl": "Najlepszy Przypadek (+15%)"},
    "base_case": {"en": "Base Case (+5%)", "pl": "Przypadek Bazowy (+5%)"},
    "worst_case": {"en": "Worst Case (-2%)", "pl": "Najgorszy Przypadek (-2%)"},
    "scenario": {"en": "Scenario", "pl": "Scenariusz"},
    "year_1_forecast": {"en": "Year 1 Forecast", "pl": "Prognoza Rok 1"},
    "year_2_forecast": {"en": "Year 2 Forecast", "pl": "Prognoza Rok 2"},
    "year_3_forecast": {"en": "Year 3 Forecast", "pl": "Prognoza Rok 3"},
    "export_forecasts": {"en": "Export Forecasts", "pl": "Eksportuj Prognozy"},
    "download_forecasts_csv": {"en": "Download Forecasts CSV", "pl": "Pobierz Prognozy CSV"},
    "please_load_analysis_sidebar": {"en": "Please load an analysis file from the sidebar to generate forecasts.",
                                    "pl": "Załaduj plik analizy z panelu bocznego, aby wygenerować prognozy."},
    "how_to_use_forecasting": {"en": "How to use Forecasting", "pl": "Jak korzystać z Prognozowania"},
    "forecasting_methods": {"en": "Forecasting Methods", "pl": "Metody Prognozowania"},
    "important_notes": {"en": "Important Notes", "pl": "Ważne Uwagi"},
    "linear_growth": {"en": "Linear Growth: Simple projection based on growth rate assumptions",
                     "pl": "Wzrost Liniowy: Prosta projekcja oparta na założeniach stopy wzrostu"},
    "conservative_model": {"en": "Conservative Model: More cautious forecasts for net income",
                          "pl": "Model Konserwatywny: Bardziej ostrożne prognozy dla zysku netto"},
    "asset_accumulation": {"en": "Asset Accumulation: Models asset growth based on reinvestment",
                          "pl": "Akumulacja Aktywów: Modeluje wzrost aktywów na podstawie reinwestycji"},
    "scenario_analysis_desc": {"en": "Scenario Analysis: Best case (+15%), base case (+5%), worst case (-2%)",
                              "pl": "Analiza Scenariuszy: Najlepszy przypadek (+15%), bazowy (+5%), najgorszy (-2%)"},
    "forecasts_disclaimer": {"en": "Disclaimer: Forecasts are estimates and should not be used as sole basis for financial decisions",
                            "pl": "Zastrzeżenie: Prognozy są szacunkami i nie powinny być używane jako jedyna podstawa decyzji finansowych"},

    # KPI Interpretations (bilingual)
    "kpi_interp_debt_to_equity": {
        "en": "Lower is generally better. Shows debt relative to equity.",
        "pl": "Niższy jest ogólnie lepszy. Pokazuje zadłużenie w stosunku do kapitału własnego."
    },
    "kpi_interp_equity_ratio": {
        "en": "Higher is better. Shows portion of assets financed by equity.",
        "pl": "Wyższy jest lepszy. Pokazuje część aktywów finansowaną kapitałem własnym."
    },
    "kpi_interp_debt_ratio": {
        "en": "Lower is generally better. Shows portion of assets financed by debt.",
        "pl": "Niższy jest ogólnie lepszy. Pokazuje część aktywów finansowaną długiem."
    },
    "kpi_interp_current_ratio": {
        "en": "Above 1.0 is healthy. Shows ability to pay short-term obligations.",
        "pl": "Powyżej 1,0 jest zdrowe. Pokazuje zdolność do spłaty krótkoterminowych zobowiązań."
    },
    "kpi_interp_quick_ratio": {
        "en": "Above 1.0 is healthy. Measures immediate liquidity excluding inventory.",
        "pl": "Powyżej 1,0 jest zdrowe. Mierzy natychmiastową płynność bez zapasów."
    },
    "kpi_interp_roe": {
        "en": "Higher is better. Shows return generated on shareholders' equity.",
        "pl": "Wyższy jest lepszy. Pokazuje zwrot generowany z kapitału własnego akcjonariuszy."
    },
    "kpi_interp_roa": {
        "en": "Higher is better. Shows how efficiently assets generate profit.",
        "pl": "Wyższy jest lepszy. Pokazuje, jak efektywnie aktywa generują zysk."
    },
    "kpi_interp_net_margin": {
        "en": "Higher is better. Shows net profit as percentage of revenue.",
        "pl": "Wyższy jest lepszy. Pokazuje zysk netto jako procent przychodów."
    },
    "kpi_interp_gross_margin": {
        "en": "Higher is better. Shows gross profit as percentage of revenue.",
        "pl": "Wyższy jest lepszy. Pokazuje zysk brutto jako procent przychodów."
    },
    "kpi_interp_ebit_margin": {
        "en": "Higher is better. Shows operating profit as percentage of revenue.",
        "pl": "Wyższy jest lepszy. Pokazuje zysk operacyjny jako procent przychodów."
    },
    "no_liquidity_kpis": {
        "en": "No liquidity KPIs available",
        "pl": "Brak dostępnych wskaźników płynności"
    },
    "no_leverage_kpis": {
        "en": "No leverage KPIs available",
        "pl": "Brak dostępnych wskaźników zadłużenia"
    },
    "kpi_interpretations": {
        "en": "KPI Interpretations",
        "pl": "Interpretacje KPI"
    },
    "leverage_ratios": {
        "en": "Leverage Ratios",
        "pl": "Wskaźniki Zadłużenia"
    },
    "liquidity_ratios": {
        "en": "Liquidity Ratios",
        "pl": "Wskaźniki Płynności"
    },
    "all_balance_sheet_data": {
        "en": "All Balance Sheet Data",
        "pl": "Wszystkie Dane Bilansowe"
    },
    "all_pl_data": {
        "en": "All P&L Data",
        "pl": "Wszystkie Dane RZiS"
    },
    "all_cash_flow_data": {
        "en": "All Cash Flow Data",
        "pl": "Wszystkie Dane Przepływów Pieniężnych"
    },
    "balance_sheet_verification": {
        "en": "Balance Sheet Verification",
        "pl": "Weryfikacja Bilansu"
    },
    "balance_is_balanced": {
        "en": "Balance sheet is balanced: Assets = Equity + Liabilities",
        "pl": "Bilans jest zrównoważony: Aktywa = Kapitał własny + Zobowiązania"
    },
    "difference": {
        "en": "Difference",
        "pl": "Różnica"
    },
    "equity_plus_liabilities": {
        "en": "Equity + Liabilities",
        "pl": "Kapitał Własny + Zobowiązania"
    },
    "balance_discrepancy": {
        "en": "Balance sheet discrepancy",
        "pl": "Rozbieżność bilansu"
    },
    "cannot_verify_balance": {
        "en": "Cannot verify balance - insufficient data",
        "pl": "Nie można zweryfikować - brak wystarczających danych"
    },
    "data_source_bilans": {
        "en": "Data source: Bilans (Balance Sheet)",
        "pl": "Źródło danych: Bilans"
    },
    "data_source_rzis": {
        "en": "Data source: Rachunek Zysków i Strat (RZiS)",
        "pl": "Źródło danych: Rachunek Zysków i Strat (RZiS)"
    },
    "data_source_cashflow": {
        "en": "Data source: Rachunek Przepływów Pieniężnych",
        "pl": "Źródło danych: Rachunek Przepływów Pieniężnych"
    },
    "income_statement": {
        "en": "Income Statement",
        "pl": "Rachunek Zysków i Strat"
    },
    "profitability_kpis": {
        "en": "Profitability KPIs",
        "pl": "Wskaźniki Rentowności"
    },
    "no_profitability_kpis": {
        "en": "No profitability KPIs calculated.",
        "pl": "Brak obliczonych wskaźników rentowności."
    },
    "period": {
        "en": "Period",
        "pl": "Okres"
    },
    "profit": {
        "en": "Profit",
        "pl": "Zysk"
    },
    "loss": {
        "en": "Loss",
        "pl": "Strata"
    },
    "available_metrics_expander": {
        "en": "Available metrics in this analysis",
        "pl": "Dostępne metryki w tej analizie"
    },
    "no_metrics_extracted": {
        "en": "No metrics extracted",
        "pl": "Brak wyodrębnionych metryk"
    },
    "no_cash_flow_kpis": {
        "en": "No Cash Flow KPIs calculated.",
        "pl": "Brak obliczonych wskaźników przepływów pieniężnych."
    },
    "cash_flow_kpis": {
        "en": "Cash Flow KPIs",
        "pl": "Wskaźniki Przepływów Pieniężnych"
    },
    "free_cash_flow_analysis": {
        "en": "Free Cash Flow Analysis",
        "pl": "Analiza Wolnych Przepływów Pieniężnych"
    },
    "operating_cash_flow": {
        "en": "Operating Cash Flow",
        "pl": "Przepływy Operacyjne"
    },
    "investing_cash_flow": {
        "en": "Investing Cash Flow",
        "pl": "Przepływy Inwestycyjne"
    },
    "financing_cash_flow": {
        "en": "Financing Cash Flow",
        "pl": "Przepływy Finansowe"
    },
    "net_change": {
        "en": "Net Change",
        "pl": "Zmiana Netto"
    },
    "capital_expenditures": {
        "en": "Capital Expenditures",
        "pl": "Nakłady Inwestycyjne"
    },
    "free_cash_flow": {
        "en": "Free Cash Flow",
        "pl": "Wolne Przepływy Pieniężne"
    },
    "positive_fcf_message": {
        "en": "Positive Free Cash Flow indicates the company generates more cash than needed for investments.",
        "pl": "Dodatni wolny przepływ pieniężny oznacza, że firma generuje więcej gotówki niż potrzebuje na inwestycje."
    },
    "negative_fcf_message": {
        "en": "Negative Free Cash Flow may indicate the company needs external financing for growth.",
        "pl": "Ujemny wolny przepływ pieniężny może oznaczać, że firma potrzebuje zewnętrznego finansowania na rozwój."
    },
    "increased": {
        "en": "Increased",
        "pl": "Wzrost"
    },
    "decreased": {
        "en": "Decreased",
        "pl": "Spadek"
    },
    "analyze_cash_flows_subtitle": {
        "en": "Analyze operating, investing, and financing cash flows",
        "pl": "Analizuj przepływy z działalności operacyjnej, inwestycyjnej i finansowej"
    },
    "related_cash_flow_kpis": {
        "en": "Related Cash Flow KPIs",
        "pl": "Powiązane Wskaźniki Gotówkowe"
    },
    "no_cash_related_kpis": {
        "en": "No cash-related KPIs available from this analysis.",
        "pl": "Brak wskaźników gotówkowych dostępnych z tej analizy."
    },

    # Metric Labels (bilingual) - Balance Sheet
    "metric_bs_assets_total": {"en": "Total Assets", "pl": "Aktywa razem"},
    "metric_bs_fixed_assets": {"en": "Non-current Assets", "pl": "Aktywa trwałe"},
    "metric_bs_intangible_assets": {"en": "Intangible Assets", "pl": "Wartości niematerialne i prawne"},
    "metric_bs_ppe": {"en": "Property, Plant & Equipment", "pl": "Rzeczowe aktywa trwałe"},
    "metric_bs_ppe_land_buildings": {"en": "Fixed Assets in Use", "pl": "Środki trwałe"},
    "metric_bs_ppe_under_construction": {"en": "Assets under Construction", "pl": "Środki trwałe w budowie"},
    "metric_bs_lt_receivables": {"en": "Long-term Receivables", "pl": "Należności długoterminowe"},
    "metric_bs_lt_investments": {"en": "Long-term Investments", "pl": "Inwestycje długoterminowe"},
    "metric_bs_lt_prepayments": {"en": "Long-term Prepayments", "pl": "Długoterminowe rozliczenia międzyokresowe"},
    "metric_bs_current_assets": {"en": "Current Assets", "pl": "Aktywa obrotowe"},
    "metric_bs_inventory": {"en": "Inventories", "pl": "Zapasy"},
    "metric_bs_inventory_materials": {"en": "Materials", "pl": "Materiały"},
    "metric_bs_inventory_goods": {"en": "Goods for Resale", "pl": "Towary"},
    "metric_bs_inventory_advances": {"en": "Advances for Deliveries", "pl": "Zaliczki na dostawy"},
    "metric_bs_accounts_receivable": {"en": "Short-term Receivables", "pl": "Należności krótkoterminowe"},
    "metric_bs_receivables_related": {"en": "Receivables from Related Parties", "pl": "Należności od jednostek powiązanych"},
    "metric_bs_receivables_other_entities": {"en": "Receivables from Other Entities", "pl": "Należności od pozostałych jednostek"},
    "metric_bs_receivables_other": {"en": "Other Short-term Receivables", "pl": "Pozostałe należności krótkoterminowe"},
    "metric_bs_st_investments": {"en": "Short-term Investments", "pl": "Inwestycje krótkoterminowe"},
    "metric_bs_cash": {"en": "Cash and Cash Equivalents", "pl": "Środki pieniężne"},
    "metric_bs_st_prepayments": {"en": "Short-term Prepayments", "pl": "Krótkoterminowe rozliczenia międzyokresowe"},
    "metric_bs_called_up_capital": {"en": "Called Up Share Capital", "pl": "Należne wpłaty na kapitał"},
    "metric_bs_own_shares": {"en": "Own Shares", "pl": "Udziały (akcje) własne"},
    "metric_bs_liabilities_equity_total": {"en": "Total Liabilities & Equity", "pl": "Pasywa razem"},
    "metric_bs_equity": {"en": "Equity", "pl": "Kapitał własny"},
    "metric_bs_share_capital": {"en": "Share Capital", "pl": "Kapitał zakładowy"},
    "metric_bs_supplementary_capital": {"en": "Supplementary Capital", "pl": "Kapitał zapasowy"},
    "metric_bs_revaluation_reserve": {"en": "Revaluation Reserve", "pl": "Kapitał z aktualizacji wyceny"},
    "metric_bs_other_reserves": {"en": "Other Reserve Capital", "pl": "Pozostałe kapitały rezerwowe"},
    "metric_bs_retained_earnings": {"en": "Retained Earnings", "pl": "Zysk (strata) z lat ubiegłych"},
    "metric_bs_net_profit_loss": {"en": "Net Profit/Loss", "pl": "Zysk (strata) netto"},
    "metric_bs_profit_appropriations": {"en": "Appropriations from Net Profit", "pl": "Odpisy z zysku netto"},
    "metric_bs_liabilities_total": {"en": "Liabilities and Provisions", "pl": "Zobowiązania i rezerwy"},
    "metric_bs_provisions": {"en": "Provisions", "pl": "Rezerwy na zobowiązania"},
    "metric_bs_deferred_tax_provision": {"en": "Deferred Tax Provision", "pl": "Rezerwa z tyt. odroczonego podatku"},
    "metric_bs_pension_provisions": {"en": "Pension Provisions", "pl": "Rezerwa na świadczenia emerytalne"},
    "metric_bs_other_provisions": {"en": "Other Provisions", "pl": "Pozostałe rezerwy"},
    "metric_bs_lt_liabilities": {"en": "Long-term Liabilities", "pl": "Zobowiązania długoterminowe"},
    "metric_bs_lt_liabilities_related": {"en": "To Related Parties (LT)", "pl": "Wobec jednostek powiązanych (dług.)"},
    "metric_bs_lt_liabilities_other": {"en": "To Other Entities (LT)", "pl": "Wobec pozostałych jednostek (dług.)"},
    "metric_bs_current_liabilities": {"en": "Short-term Liabilities", "pl": "Zobowiązania krótkoterminowe"},
    "metric_bs_st_liabilities_related": {"en": "To Related Parties (ST)", "pl": "Wobec jednostek powiązanych (krótk.)"},
    "metric_bs_st_liabilities_associated": {"en": "To Associated Entities (ST)", "pl": "Wobec jednostek z zaangażowaniem"},
    "metric_bs_st_liabilities_other": {"en": "To Other Entities (ST)", "pl": "Wobec pozostałych jednostek (krótk.)"},
    "metric_bs_trade_payables": {"en": "Trade Payables", "pl": "Zobowiązania z tyt. dostaw i usług"},
    "metric_bs_tax_payables": {"en": "Tax Payables", "pl": "Zobowiązania z tyt. podatków"},
    "metric_bs_salaries_payable": {"en": "Salaries Payable", "pl": "Zobowiązania z tyt. wynagrodzeń"},
    "metric_bs_special_funds": {"en": "Special Funds", "pl": "Fundusze specjalne"},
    "metric_bs_accruals": {"en": "Accruals", "pl": "Rozliczenia międzyokresowe"},

    # Metric Labels (bilingual) - P&L
    "metric_pl_revenue": {"en": "Net Sales Revenue", "pl": "Przychody netto ze sprzedaży"},
    "metric_pl_export_revenue": {"en": "Export Revenue", "pl": "Przychody ze sprzedaży na eksport"},
    "metric_pl_revenue_products": {"en": "Revenue from Products", "pl": "Przychody ze sprzedaży produktów"},
    "metric_pl_revenue_goods": {"en": "Revenue from Goods", "pl": "Przychody ze sprzedaży towarów"},
    "metric_pl_cogs": {"en": "Cost of Sales", "pl": "Koszty sprzedanych produktów i towarów"},
    "metric_pl_export_costs": {"en": "Export Costs", "pl": "Koszty na eksport"},
    "metric_pl_cost_products": {"en": "Cost of Products Sold", "pl": "Koszt wytworzenia sprzedanych produktów"},
    "metric_pl_cost_goods": {"en": "Cost of Goods Sold", "pl": "Wartość sprzedanych towarów"},
    "metric_pl_gross_profit": {"en": "Gross Profit", "pl": "Zysk (strata) brutto ze sprzedaży"},
    "metric_pl_selling_expenses": {"en": "Selling Expenses", "pl": "Koszty sprzedaży"},
    "metric_pl_admin_expenses": {"en": "Administrative Expenses", "pl": "Koszty ogólnego zarządu"},
    "metric_pl_operating_profit_sales": {"en": "Operating Profit from Sales", "pl": "Zysk (strata) ze sprzedaży"},
    "metric_pl_other_operating_income": {"en": "Other Operating Income", "pl": "Pozostałe przychody operacyjne"},
    "metric_pl_gain_disposal_assets": {"en": "Gain on Disposal of Assets", "pl": "Zysk z rozchodu aktywów trwałych"},
    "metric_pl_other_op_income_other": {"en": "Other Operating Income - Other", "pl": "Inne przychody operacyjne"},
    "metric_pl_other_operating_expenses": {"en": "Other Operating Expenses", "pl": "Pozostałe koszty operacyjne"},
    "metric_pl_other_op_expenses_other": {"en": "Other Operating Expenses - Other", "pl": "Inne koszty operacyjne"},
    "metric_pl_ebit": {"en": "EBIT", "pl": "Zysk z działalności operacyjnej"},
    "metric_pl_financial_income": {"en": "Financial Income", "pl": "Przychody finansowe"},
    "metric_pl_dividend_income": {"en": "Dividend Income", "pl": "Dywidendy i udziały w zyskach"},
    "metric_pl_interest_income": {"en": "Interest Income", "pl": "Odsetki (przychody)"},
    "metric_pl_other_financial_income": {"en": "Other Financial Income", "pl": "Inne przychody finansowe"},
    "metric_pl_financial_expenses": {"en": "Financial Expenses", "pl": "Koszty finansowe"},
    "metric_pl_interest_expense": {"en": "Interest Expense", "pl": "Odsetki (koszty)"},
    "metric_pl_other_financial_expenses": {"en": "Other Financial Expenses", "pl": "Inne koszty finansowe"},
    "metric_pl_profit_before_tax": {"en": "Profit Before Tax", "pl": "Zysk (strata) brutto"},
    "metric_pl_income_tax": {"en": "Income Tax", "pl": "Podatek dochodowy"},
    "metric_pl_other_mandatory_reductions": {"en": "Other Mandatory Reductions", "pl": "Pozostałe obowiązkowe zmniejszenia zysku"},
    "metric_pl_net_profit": {"en": "Net Profit", "pl": "Zysk (strata) netto"},

    # Metric Labels (bilingual) - Cash Flow
    "metric_cf_operating": {"en": "Operating Cash Flow", "pl": "Przepływy z działalności operacyjnej"},
    "metric_cf_net_profit": {"en": "Net Profit (CF)", "pl": "Zysk (strata) netto"},
    "metric_cf_adjustments_total": {"en": "Total Adjustments", "pl": "Korekty razem"},
    "metric_cf_depreciation": {"en": "Depreciation & Amortization", "pl": "Amortyzacja"},
    "metric_cf_change_provisions": {"en": "Change in Provisions", "pl": "Zmiana stanu rezerw"},
    "metric_cf_change_inventory": {"en": "Change in Inventory", "pl": "Zmiana stanu zapasów"},
    "metric_cf_change_receivables": {"en": "Change in Receivables", "pl": "Zmiana stanu należności"},
    "metric_cf_change_payables": {"en": "Change in Payables", "pl": "Zmiana stanu zobowiązań"},
    "metric_cf_change_accruals": {"en": "Change in Accruals", "pl": "Zmiana stanu rozliczeń międzyokresowych"},
    "metric_cf_other_adjustments": {"en": "Other Adjustments", "pl": "Inne korekty"},
    "metric_cf_investing": {"en": "Investing Cash Flow", "pl": "Przepływy z działalności inwestycyjnej"},
    "metric_cf_investing_inflows": {"en": "Investing Inflows", "pl": "Wpływy z działalności inwestycyjnej"},
    "metric_cf_sale_fixed_assets": {"en": "Sale of Fixed Assets", "pl": "Zbycie aktywów trwałych"},
    "metric_cf_investing_outflows": {"en": "Investing Outflows", "pl": "Wydatki z działalności inwestycyjnej"},
    "metric_cf_capex": {"en": "Capital Expenditure", "pl": "Nabycie aktywów trwałych"},
    "metric_cf_financing": {"en": "Financing Cash Flow", "pl": "Przepływy z działalności finansowej"},
    "metric_cf_financing_inflows": {"en": "Financing Inflows", "pl": "Wpływy z działalności finansowej"},
    "metric_cf_loans_received": {"en": "Loans Received", "pl": "Kredyty i pożyczki"},
    "metric_cf_financing_outflows": {"en": "Financing Outflows", "pl": "Wydatki z działalności finansowej"},
    "metric_cf_dividends_paid": {"en": "Dividends Paid", "pl": "Dywidendy wypłacone"},
    "metric_cf_net_change": {"en": "Net Cash Flow", "pl": "Przepływy pieniężne netto razem"},
    "metric_cf_balance_change": {"en": "Balance Sheet Change in Cash", "pl": "Bilansowa zmiana stanu środków pieniężnych"},
    "metric_cf_opening_cash": {"en": "Opening Cash Balance", "pl": "Środki pieniężne na początek okresu"},
    "metric_cf_closing_cash": {"en": "Closing Cash Balance", "pl": "Środki pieniężne na koniec okresu"},

    # Section headers
    "section_assets": {"en": "Assets", "pl": "Aktywa"},
    "section_fixed_assets": {"en": "A. Non-current Assets", "pl": "A. Aktywa trwałe"},
    "section_current_assets": {"en": "B. Current Assets", "pl": "B. Aktywa obrotowe"},
    "section_equity": {"en": "A. Equity", "pl": "A. Kapitał własny"},
    "section_liabilities": {"en": "B. Liabilities and Provisions", "pl": "B. Zobowiązania i rezerwy"},
    "section_operating_activities": {"en": "A. Operating Activities", "pl": "A. Działalność operacyjna"},
    "section_investing_activities": {"en": "B. Investing Activities", "pl": "B. Działalność inwestycyjna"},
    "section_financing_activities": {"en": "C. Financing Activities", "pl": "C. Działalność finansowa"},

    # Key metrics headers
    "key_balance_sheet_data": {"en": "Key Balance Sheet Data", "pl": "Kluczowe Dane Bilansowe"},
    "key_pl_data": {"en": "Key P&L Data", "pl": "Kluczowe Dane RZiS"},
    "key_cash_flow_data": {"en": "Key Cash Flow Data", "pl": "Kluczowe Dane Przepływów Pieniężnych"},

    # Cash Flow page specific
    "cash_flow_title": {"en": "Cash Flow Statement", "pl": "Rachunek Przepływów Pieniężnych"},
    "cash_flow_subtitle": {"en": "Rachunek Przepływów Pieniężnych", "pl": "Rachunek Przepływów Pieniężnych"},
    "no_cash_flow_data": {"en": "No Cash Flow data available in this financial statement.",
                         "pl": "Brak danych przepływów pieniężnych w tym sprawozdaniu finansowym."},

    # Metric value column
    "metric": {"en": "Metric", "pl": "Metryka"},
    "value": {"en": "Value", "pl": "Wartość"},
    "label": {"en": "Label", "pl": "Etykieta"},
}


def t(key: str, lang: str = "EN") -> str:
    """
    Main translation function - get text by key in specified language.

    Args:
        key: Translation key from TRANSLATIONS dictionary
        lang: Language code ("EN" or "PL", case-insensitive)

    Returns:
        Translated text in specified language
        Falls back to EN if key not found in specified language
        Returns key itself if key doesn't exist at all

    Examples:
        >>> t("app_title", "EN")
        'CFO Copilot'
        >>> t("app_title", "PL")
        'CFO Copilot'
        >>> t("settings", "PL")
        'Ustawienia'
    """
    trans = TRANSLATIONS.get(key, {})
    # Normalize language code to lowercase for dictionary lookup
    lang_lower = lang.lower()
    # Fallback chain: requested lang -> en -> key itself
    return trans.get(lang_lower) or trans.get("en") or key


def tr(en: str, pl: str, lang: str) -> str:
    """
    Legacy translation function (backwards compatibility).

    Translate string based on selected language.

    Args:
        en: English text
        pl: Polish text
        lang: Language code ("EN" or "PL")

    Returns:
        Text in selected language
    """
    return en if lang == "EN" else pl
