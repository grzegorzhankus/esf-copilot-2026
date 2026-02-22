# e-SF Copilot - Polish Financial Statement Analyzer

AI-powered financial analysis tool for Polish e-Sprawozdania (electronic financial statements) with full bilingual support (English/Polish).

## 🌟 Features

### 🌐 Bilingual Interface (NEW!)
- Full English/Polish language support across all pages
- Language switcher in sidebar for instant switching
- Bilingual AI chat responses (Ollama LLM responds in selected language)
- All menus, buttons, notifications, and error messages translated
- Session-based language persistence

### 1. 📄 XML Analysis
- Upload and parse Polish e-Sprawozdania XML files
- Automatic schema detection and validation
- Extract base financial metrics from balance sheet, P&L, and cash flow statements
- Calculate 10 financial KPIs across 4 categories
- Detect 9 financial red flags with severity levels
- Interactive visualizations and charts
- Export to Excel, PDF, and JSON formats

### 2. 💬 CFO Chat (LLM-Powered)
- Interactive chat with AI financial advisor
- Context-aware analysis based on uploaded financial data
- Get expert insights on profitability, liquidity, and solvency
- Ask questions in natural language
- Powered by Ollama LLM (offline, privacy-first)

### 3. 📦 Batch Processing
- Analyze multiple XML files simultaneously
- Generate summary reports across all files
- Compare financial health across entities
- Batch export (ZIP) with all reports
- Progress tracking and error handling

### 4. 📈 Financial Forecasting
- Project future financial performance (1-3 years)
- Scenario analysis (best case, base case, worst case)
- Linear growth models with confidence levels
- Interactive forecast visualizations
- Export forecasts to CSV

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app/app.py
```

The application will open in your browser at `http://localhost:8501`

### Setting Up LLM (for CFO Chat)

**Option 1: NVIDIA NIM (Recommended for DGX Spark)**

1. Get API key from [NVIDIA Build Platform](https://build.nvidia.com/)
2. Create `.env` file:
   ```bash
   cp .env.example .env
   nano .env  # Add NVIDIA_API_KEY
   ```
3. Supported models:
   - Llama 4 Maverick (405B)
   - DeepSeek V3 (685B)
   - Mistral Large 3 (123B)
   - Qwen3 (72B)

**Option 2: Ollama (Local Fallback)**

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3.1:8b
   ```
3. Ensure Ollama is running on `http://localhost:11434`

**Verify Setup:**
```bash
python test_llm_setup.py
```

See [docs/LLM_SETUP.md](docs/LLM_SETUP.md) for detailed configuration.

## 📊 Capabilities

### Base Metrics Extraction
- Total Assets, Equity, Total Liabilities
- Revenue, EBIT, Net Income
- Operating Cash Flow, Net Change in Cash

### KPI Calculations (10 KPIs)

**Profitability** (4 KPIs): ROA, ROE, Net Profit Margin, EBIT Margin
**Leverage** (3 KPIs): Debt-to-Equity, Equity Ratio, Debt Ratio
**Efficiency** (1 KPI): Asset Turnover
**Cash Flow** (2 KPIs): OCF to Revenue, Quality of Earnings

### Red Flag Detection (9 Rules)

**High Severity** (5 flags): Negative Net Income, Negative Equity, Negative OCF, Excessive Leverage, Negative Profit Margin
**Medium Severity** (3 flags): High Debt-to-Equity, Low Equity Ratio, Poor Earnings Quality
**Low Severity** (1 flag): Low ROE

### Visualizations
- Financial Health Score Gauge
- Base Metrics Bar Chart
- Balance Sheet Structure Pie Chart
- KPI Gauge Charts
- Red Flags Summary Chart
- Forecast Line Charts
- Scenario Comparison Charts

## 📁 Project Structure

```
esf-copilot-2026/
├── app/
│   ├── app.py                          # Main landing page (bilingual)
│   └── pages/
│       ├── 1_📄_XML_Analysis.py       # XML upload and analysis (bilingual)
│       ├── 2_💬_CFO_Chat.py           # AI-powered chat interface (bilingual)
│       ├── 3_📦_Batch_Processing.py   # Multi-file processing (bilingual)
│       ├── 4_📈_Forecasting.py        # Financial forecasting (bilingual)
│       ├── 5_📊_Overview.py           # KPIs and red flags dashboard
│       ├── 6_📈_P&L.py                # Profit & Loss statement
│       ├── 7_📙_Balance_Sheet.py      # Assets and liabilities
│       ├── 8_📋_Analysis_Log.py       # Raw data and parsing details
│       └── 9_🧾_Board_Memo.py         # Executive summary generator
├── core/                              # Core analysis modules
│   ├── i18n.py                        # Translation dictionary (489+ keys)
│   ├── language_selector.py          # Language switcher component
│   ├── llm_integration.py            # Ollama integration with bilingual prompts
│   ├── analysis_pipeline.py          # XML analysis engine
│   ├── kpi_calculator.py             # Financial KPI calculations
│   ├── red_flags.py                  # Red flag detection
│   ├── forecasting.py                # Financial forecasting models
│   └── ... (other modules)
├── configs/mappings/                  # Schema-specific XPath mappings
├── data/demo_xml/                     # Sample XML files
├── outputs/                           # Generated analysis files
└── requirements.txt                   # Python dependencies
```

## 🔧 Configuration

### Language Settings

The application automatically detects and persists language preference using Streamlit session state. Users can switch between English (EN) and Polish (PL) using the sidebar dropdown on any page.

To add new translations:
1. Edit `core/i18n.py`
2. Add new keys to the `TRANSLATIONS` dictionary with EN/PL values
3. Use `t("key_name", lang)` in your code to access translations

### Adding New Schema Mappings

Create `configs/mappings/<schema_slug>/mapping_v1.yaml`:

```yaml
version: v1
schema_id: http://www.mf.gov.pl/schematy/...
unit: PLN
metrics:
  bs_total_assets:
    xpaths:
      - Bilans/Aktywa/SumaAktywow
    transform: first
    sign_rule: none
```

## 📚 Dependencies

- streamlit (>=1.32.0), defusedxml (>=0.7.1), PyYAML (>=6.0.1)
- openpyxl (>=3.1.0), pandas (>=2.0.0), reportlab (>=4.0.0)
- plotly (>=5.14.0), requests (>=2.31.0)

## 🎯 Use Cases

- Financial Due Diligence
- Compliance Monitoring
- Portfolio Management
- Financial Planning
- Audit Preparation

## 🔒 Security & Privacy

- All processing done locally
- No external data transmission (except optional Ollama)
- Privacy-first AI with local LLM
- Secure XML parsing with defusedxml

---

**Built with Streamlit and AI**
