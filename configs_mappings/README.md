# XML Schema Mappings

This directory contains XPath mapping configurations for different Polish e-Sprawozdanie XML schema variants.

## Directory Structure

```
configs/mappings/
├── README.md                                    # This file
├── _default/                                    # Fallback mapping
│   └── mapping_v1.yaml
├── urn_esf_demo_v1/                            # Demo schema
│   └── mapping_v1.yaml
└── http_www.mf.gov.pl_schematy_.../           # Official MF schemas
    └── mapping_v1.yaml
```

## How It Works

1. When you upload an XML file, the app extracts the **namespace URI** from the root element
2. The namespace is converted to a **schema ID** by replacing special characters with underscores
3. The app looks for a matching directory in `configs/mappings/{schema_id}/`
4. If found, it loads `mapping_v1.yaml` from that directory
5. If not found, it falls back to `_default/mapping_v1.yaml`

## Adding a New Schema Mapping

### Quick Method (Recommended)

Use the helper script:

```bash
cd /home/grzegorzhankus/cfo-copilot
python create_schema_mapping.py path/to/your/file.xml
```

This will:
- Extract the namespace from your XML
- Create the directory structure
- Generate a template `mapping_v1.yaml`
- Show the XML structure to help with XPath mapping

### Manual Method

**Step 1: Identify Your Schema Namespace**

Look at the root element of your XML file:

```xml
<JednostkaInna xmlns="http://www.mf.gov.pl/schematy/sf/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaWTysiacach">
```

The namespace URI is: `http://www.mf.gov.pl/schematy/sf/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaWTysiacach`

**Step 2: Convert to Schema ID**

Replace special characters (`://`, `/`, `.`) with underscores:

```
http_www.mf.gov.pl_schematy_sf_definicjetypysprawozdaniafinansowe_2025_01_01_jednostkainnawtysiacach
```

**Step 3: Create Directory**

```bash
mkdir -p configs/mappings/http_www.mf.gov.pl_schematy_sf_definicjetypysprawozdaniafinansowe_2025_01_01_jednostkainnawtysiacach
```

**Step 4: Create mapping_v1.yaml**

Copy the template from `_default/mapping_v1.yaml` and modify the XPaths.

## YAML Mapping File Format

```yaml
schema_id: your_schema_id_here

# Required metrics that must be present for good coverage
required_metrics:
  - bs_assets_total
  - bs_equity
  - pl_revenue
  # ... more metrics

# Metric definitions
metrics:
  - key: bs_assets_total              # Internal metric key
    xpaths:                           # List of XPath variants to try
      - Bilans/Aktywa/Razem           # First match wins
      - Bilans/Aktywa/KwotaA
      - BalanceSheet/Assets/Total
    required: true                    # Whether this metric is required

  - key: pl_revenue
    xpaths:
      - RZiS/RZiSKalk/A/KwotaA        # Cost-of-sales variant
      - RZiS/RZiSPor/A/KwotaA         # Comparative variant
    required: true
```

## Standard Metric Keys

The app expects these standard metric keys:

### Balance Sheet (Bilans)
- `bs_assets_total` - Total assets
- `bs_equity` - Equity / Capital
- `bs_liabilities_total` - Total liabilities
- `bs_current_assets` - Current assets
- `bs_current_liabilities` - Current liabilities
- `bs_cash` - Cash and cash equivalents
- `bs_accounts_receivable` - Accounts receivable
- `bs_inventory` - Inventory
- `bs_debt_total` - Total debt
- `bs_net_debt` - Net debt (if available)

### Profit & Loss (RZiS)
- `pl_revenue` - Revenue / Sales
- `pl_gross_profit` - Gross profit
- `pl_ebit` - EBIT / Operating profit
- `pl_net_profit` - Net profit
- `pl_cogs` - Cost of goods sold
- `pl_operating_expenses` - Operating expenses
- `pl_interest_expense` - Interest expense
- `pl_ebitda` - EBITDA (if available)

### Cash Flow (Rachunek Przepływów)
- `cf_operating_cash_flow` - Operating cash flow
- `cf_investing_cash_flow` - Investing cash flow
- `cf_financing_cash_flow` - Financing cash flow
- `cf_net_change_in_cash` - Net change in cash

## XPath Guidelines

1. **No namespace prefixes needed** - The parser automatically handles namespaces
   ```yaml
   # ✅ Good
   xpaths:
     - Bilans/Aktywa/Razem

   # ❌ Don't use prefixes
   xpaths:
     - esf:Bilans/esf:Aktywa/esf:Razem
   ```

2. **Use local element names** - Just the element name without namespace
   ```xml
   <!-- XML: -->
   <ns:Bilans xmlns:ns="...">
     <ns:Aktywa>...</ns:Aktywa>
   </ns:Bilans>

   <!-- XPath: -->
   Bilans/Aktywa
   ```

3. **Provide multiple variants** - Different XML schemas use different structures
   ```yaml
   xpaths:
     - RZiS/RZiSKalk/A/KwotaA      # Kalkulacyjny variant
     - RZiS/RZiSPor/A/KwotaA       # Porównawczy variant
     - RachunekZyskowIStrat/A      # Alternative naming
   ```

4. **First match wins** - The parser tries each XPath in order and uses the first one that finds a value

## Testing Your Mapping

1. Create the mapping directory and YAML file
2. Upload your XML file in the web app
3. Check the **Analysis Log** tab to see:
   - Coverage percentage
   - Which metrics were found (Present Metrics)
   - Which metrics are missing (Missing Metrics)
4. Adjust XPaths in your YAML file based on the results
5. Re-upload the XML to test

## Common Polish XML Structures

### Balance Sheet Variants

**Variant 1: JednostkaInna**
```
Bilans/
  Aktywa/
    AktywaObrotowe/...
    AktywaTrawe/...
  Pasywa/
    KapitalWlasny/...
    Zobowiazania/...
```

**Variant 2: JednostkaMikro**
```
Bilans/
  Aktywa/Razem
  Pasywa/Razem
```

### P&L Variants

**RZiS Kalkulacyjny (Cost-of-sales)**
```
RZiS/RZiSKalk/
  A/KwotaA    # Revenue
  B/KwotaA    # COGS
  C/KwotaA    # Gross profit
  ...
  O/KwotaA    # Net profit
```

**RZiS Porównawczy (Comparative)**
```
RZiS/RZiSPor/
  A/KwotaA    # Revenue
  ...
  O/KwotaA    # Net profit
```

## Troubleshooting

### Problem: Coverage is 0%

**Solution:** Your XPaths don't match the XML structure.

1. Run the helper script to see the XML structure:
   ```bash
   python create_schema_mapping.py your_file.xml
   ```

2. Compare the output with your XPaths in the YAML file

3. Update the XPaths to match the actual structure

### Problem: Some metrics found, others missing

**Solution:** Check the Analysis Log tab:
- Green ✓ = metric found
- Red ✗ = metric missing

Update the XPaths for the missing metrics.

### Problem: Mapping falls back to _default

**Solution:** The schema directory name doesn't match the detected schema ID.

1. Upload your XML and check the Analysis Log
2. Look for "Schema ID: ..."
3. Your directory must be named exactly like that schema ID

## Examples

See existing mappings for reference:
- [configs/mappings/urn_esf_demo_v1/mapping_v1.yaml](urn_esf_demo_v1/mapping_v1.yaml) - Simple demo
- `configs/mappings/http_www.mf.gov.pl_.../mapping_v1.yaml` - Real MF schema

## Support

For questions or issues with schema mappings:
1. Check the Analysis Log tab for diagnostic information
2. Review this README
3. Examine existing mapping files as examples
4. Use the helper script to explore your XML structure
