"""P&L (Profit & Loss) Extractor for Polish e-Sprawozdanie XML.

Extracts Income Statement (RZiS - Rachunek Zysków i Strat) data from XML
with hierarchical structure and both current and prior period values.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from xml.etree.ElementTree import Element


@dataclass
class PLItem:
    """A single P&L line item."""
    key: str
    label_pl: str
    label_en: str
    level: int
    current: Optional[float]
    prior: Optional[float]


# P&L item labels for RZiS Kalkulacyjny format
# Keys follow pattern: parent_child (e.g., A_A_I means A/A_I in XML path)
PL_LABELS = {
    # Level 0 - Total results
    "RZiS": ("RACHUNEK ZYSKÓW I STRAT", "PROFIT & LOSS STATEMENT"),
    "RZiSKalk": ("RACHUNEK ZYSKÓW I STRAT (Kalkulacyjny)", "PROFIT & LOSS (Cost method)"),

    # A - Revenue section
    "A": ("A. Przychody netto ze sprzedaży", "A. Net sales revenue"),
    "A_I": ("I. Przychody netto ze sprzedaży produktów", "I. Revenue from products"),
    "A_II": ("II. Zmiana stanu produktów", "II. Change in products"),
    "A_III": ("III. Koszt wytworzenia na własne potrzeby", "III. Production for own use"),
    "A_IV": ("IV. Przychody netto ze sprzedaży towarów", "IV. Revenue from goods"),
    "A_J": ("w tym od jednostek powiązanych", "of which from related parties"),
    # Nested keys (path A/A_I becomes key A_A_I)
    "A_A_I": ("I. Przychody netto ze sprzedaży produktów", "I. Revenue from products"),
    "A_A_II": ("II. Zmiana stanu produktów", "II. Change in products"),
    "A_A_III": ("III. Koszt wytworzenia na własne potrzeby", "III. Production for own use"),
    "A_A_IV": ("IV. Przychody netto ze sprzedaży towarów", "IV. Revenue from goods"),
    "A_A_J": ("w tym od jednostek powiązanych", "of which from related parties"),

    # B - Operating costs section
    "B": ("B. Koszty działalności operacyjnej", "B. Operating costs"),
    "B_I": ("I. Koszt wytworzenia sprzedanych produktów", "I. Cost of products sold"),
    "B_II": ("II. Wartość sprzedanych towarów i materiałów", "II. Cost of goods sold"),
    "B_J": ("w tym od jednostek powiązanych", "of which from related parties"),
    # Nested keys
    "B_B_I": ("I. Koszt wytworzenia sprzedanych produktów", "I. Cost of products sold"),
    "B_B_II": ("II. Wartość sprzedanych towarów i materiałów", "II. Cost of goods sold"),
    "B_B_J": ("w tym od jednostek powiązanych", "of which from related parties"),

    # C - Gross profit
    "C": ("C. Zysk (strata) brutto ze sprzedaży", "C. Gross profit (loss) from sales"),

    # D - Selling costs
    "D": ("D. Koszty sprzedaży", "D. Selling costs"),

    # E - Other operating income
    "E": ("E. Pozostałe przychody operacyjne", "E. Other operating income"),
    "E_I": ("I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych", "I. Gain from disposal of fixed assets"),
    "E_II": ("II. Dotacje", "II. Subsidies"),
    "E_III": ("III. Aktualizacja wartości aktywów niefinansowych", "III. Revaluation of assets"),
    "E_IV": ("IV. Inne przychody operacyjne", "IV. Other operating income"),
    "E_E_I": ("I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych", "I. Gain from disposal of fixed assets"),
    "E_E_II": ("II. Dotacje", "II. Subsidies"),
    "E_E_III": ("III. Aktualizacja wartości aktywów niefinansowych", "III. Revaluation of assets"),
    "E_E_IV": ("IV. Inne przychody operacyjne", "IV. Other operating income"),

    # F - Other operating costs
    "F": ("F. Pozostałe koszty operacyjne", "F. Other operating costs"),
    "F_I": ("I. Strata z tytułu rozchodu niefinansowych aktywów trwałych", "I. Loss from disposal of fixed assets"),
    "F_II": ("II. Aktualizacja wartości aktywów niefinansowych", "II. Revaluation of assets"),
    "F_III": ("III. Inne koszty operacyjne", "III. Other operating costs"),
    "F_F_I": ("I. Strata z tytułu rozchodu niefinansowych aktywów trwałych", "I. Loss from disposal of fixed assets"),
    "F_F_II": ("II. Aktualizacja wartości aktywów niefinansowych", "II. Revaluation of assets"),
    "F_F_III": ("III. Inne koszty operacyjne", "III. Other operating costs"),

    # G - Operating result (variant)
    "G": ("G. Zysk (strata) z działalności operacyjnej", "G. Operating profit (loss)"),
    "G_I": ("I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych", "I. Gain from disposal of fixed assets"),
    "G_II": ("II. Dotacje", "II. Subsidies"),
    "G_III": ("III. Aktualizacja wartości aktywów niefinansowych", "III. Revaluation of assets"),
    "G_IV": ("IV. Inne przychody operacyjne", "IV. Other operating income"),
    "G_G_I": ("I. Zysk z tytułu rozchodu niefinansowych aktywów trwałych", "I. Gain from disposal of fixed assets"),
    "G_G_II": ("II. Dotacje", "II. Subsidies"),
    "G_G_III": ("III. Aktualizacja wartości aktywów niefinansowych", "III. Revaluation of assets"),
    "G_G_IV": ("IV. Inne przychody operacyjne", "IV. Other operating income"),

    # H - Administrative costs
    "H": ("H. Koszty ogólnego zarządu", "H. Administrative costs"),
    "H_I": ("I. Strata z tytułu rozchodu niefinansowych aktywów trwałych", "I. Loss from disposal of fixed assets"),
    "H_II": ("II. Aktualizacja wartości aktywów niefinansowych", "II. Revaluation of assets"),
    "H_III": ("III. Inne koszty operacyjne", "III. Other operating costs"),
    "H_H_I": ("I. Strata z tytułu rozchodu niefinansowych aktywów trwałych", "I. Loss from disposal of fixed assets"),
    "H_H_II": ("II. Aktualizacja wartości aktywów niefinansowych", "II. Revaluation of assets"),
    "H_H_III": ("III. Inne koszty operacyjne", "III. Other operating costs"),

    # I - Operating profit (EBIT)
    "I": ("I. Zysk (strata) z działalności operacyjnej", "I. Operating profit (loss) / EBIT"),

    # J - Financial income
    "J": ("J. Przychody finansowe", "J. Financial income"),
    "J_I": ("I. Dywidendy i udziały w zyskach", "I. Dividends and profit shares"),
    "J_II": ("II. Odsetki", "II. Interest received"),
    "J_III": ("III. Zysk z tytułu rozchodu aktywów finansowych", "III. Gain from financial assets"),
    "J_IV": ("IV. Aktualizacja wartości aktywów finansowych", "IV. Revaluation of financial assets"),
    "J_V": ("V. Inne", "V. Other"),
    "J_J_I": ("I. Dywidendy i udziały w zyskach", "I. Dividends and profit shares"),
    "J_J_II": ("II. Odsetki", "II. Interest received"),
    "J_J_III": ("III. Zysk z tytułu rozchodu aktywów finansowych", "III. Gain from financial assets"),
    "J_J_IV": ("IV. Aktualizacja wartości aktywów finansowych", "IV. Revaluation of financial assets"),
    "J_J_V": ("V. Inne", "V. Other"),

    # K - Financial costs
    "K": ("K. Koszty finansowe", "K. Financial costs"),
    "K_I": ("I. Odsetki", "I. Interest expense"),
    "K_II": ("II. Strata z tytułu rozchodu aktywów finansowych", "II. Loss from financial assets"),
    "K_III": ("III. Aktualizacja wartości aktywów finansowych", "III. Revaluation of financial assets"),
    "K_IV": ("IV. Inne", "IV. Other"),
    "K_K_I": ("I. Odsetki", "I. Interest expense"),
    "K_K_II": ("II. Strata z tytułu rozchodu aktywów finansowych", "II. Loss from financial assets"),
    "K_K_III": ("III. Aktualizacja wartości aktywów finansowych", "III. Revaluation of financial assets"),
    "K_K_IV": ("IV. Inne", "IV. Other"),

    # L - Profit before tax
    "L": ("L. Zysk (strata) brutto", "L. Profit (loss) before tax"),

    # M - Income tax
    "M": ("M. Podatek dochodowy", "M. Income tax"),

    # N - Other mandatory reductions
    "N": ("N. Pozostałe obowiązkowe zmniejszenia zysku", "N. Other mandatory profit reductions"),

    # O - Net profit
    "O": ("O. Zysk (strata) netto", "O. Net profit (loss)"),
}


def _get_label(key: str) -> tuple:
    """Get Polish and English labels for a P&L item key."""
    # Remove RZiSKalk prefix if present
    clean_key = key.replace("RZiSKalk_", "").replace("RZiS_", "")

    # Try exact match first
    if clean_key in PL_LABELS:
        return PL_LABELS[clean_key]

    # Try simplified key: A_A_I -> A_I (remove repeated parent prefix)
    parts = clean_key.split("_")
    if len(parts) >= 3 and parts[0] == parts[1]:
        # Key like A_A_I -> try A_I
        simplified = "_".join([parts[0]] + parts[2:])
        if simplified in PL_LABELS:
            return PL_LABELS[simplified]

    # Try just the last part: A_A_I -> I
    if len(parts) >= 2:
        last_part = parts[-1]
        for prefix in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]:
            test_key = f"{prefix}_{last_part}"
            if test_key in PL_LABELS:
                return PL_LABELS[test_key]

    # Default label from key (format nicely)
    display_key = clean_key.replace("_", " ")
    return (display_key, display_key)


def _get_level(key: str) -> int:
    """Determine hierarchy level from key structure."""
    # Remove prefixes
    clean = key.replace("RZiSKalk_", "").replace("RZiS_", "")

    # Count underscores to determine level
    parts = clean.split("_")

    if clean == "RZiS":
        return 0
    elif len(parts) == 1 and parts[0].isalpha():
        # Single letter (A, B, C, etc.)
        return 1
    elif len(parts) == 2 and parts[1].startswith(("I", "V", "X")):
        # Roman numeral (A_I, A_II, etc.)
        return 2
    elif len(parts) >= 3:
        return 3
    else:
        return 2


def _localname(tag: str) -> str:
    """Strip namespace from tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _extract_amounts(node: Element) -> tuple:
    """Extract KwotaA (current) and KwotaB (prior) values from node."""
    current = None
    prior = None

    for child in node:
        local = _localname(child.tag)
        if local == "KwotaA" and child.text:
            try:
                current = float(child.text.strip().replace(" ", "").replace(",", "."))
            except ValueError:
                pass
        elif local == "KwotaB" and child.text:
            try:
                prior = float(child.text.strip().replace(" ", "").replace(",", "."))
            except ValueError:
                pass

    return current, prior


def _extract_pl_recursive(node: Element, parent_key: str = "", items: List[PLItem] = None) -> List[PLItem]:
    """Recursively extract P&L items from XML structure."""
    if items is None:
        items = []

    local = _localname(node.tag)

    # Skip non-relevant nodes
    if local in ("KwotaA", "KwotaB"):
        return items

    # Build key
    if parent_key:
        key = f"{parent_key}_{local}"
    else:
        key = local

    # Check if this node has amounts
    current, prior = _extract_amounts(node)

    # Only add if it's a P&L item (has amounts or is a known category)
    if current is not None or prior is not None or local in PL_LABELS:
        label_pl, label_en = _get_label(key)
        level = _get_level(key)

        items.append(PLItem(
            key=key,
            label_pl=label_pl,
            label_en=label_en,
            level=level,
            current=current,
            prior=prior,
        ))

    # Recurse into children
    for child in node:
        _extract_pl_recursive(child, key, items)

    return items


def extract_pl_statement(root: Element) -> List[PLItem]:
    """Extract all P&L items from XML root.

    Args:
        root: XML ElementTree root element.

    Returns:
        List of PLItem objects representing the income statement structure.
    """
    items = []

    # Find RZiS (Rachunek Zysków i Strat) section
    for elem in root.iter():
        local = _localname(elem.tag)
        if local in ("RZiS", "RZiSKalk", "RZiSPor"):
            # Found P&L section, extract items
            _extract_pl_recursive(elem, "", items)
            break

    return items


def pl_to_dict(items: List[PLItem]) -> List[Dict[str, Any]]:
    """Convert PLItem list to list of dictionaries.

    Args:
        items: List of PLItem objects.

    Returns:
        List of dictionaries suitable for JSON serialization.
    """
    return [
        {
            "key": item.key,
            "label_pl": item.label_pl,
            "label_en": item.label_en,
            "level": item.level,
            "current": item.current,
            "prior": item.prior,
        }
        for item in items
    ]


def get_pl_summary(items: List[PLItem]) -> Dict[str, Optional[float]]:
    """Extract key P&L summary values.

    Args:
        items: List of PLItem objects.

    Returns:
        Dictionary with key P&L metrics.
    """
    summary = {}

    for item in items:
        key = item.key.replace("RZiSKalk_", "").replace("RZiS_", "")

        if key == "A":
            summary["revenue_current"] = item.current
            summary["revenue_prior"] = item.prior
        elif key == "C":
            summary["gross_profit_current"] = item.current
            summary["gross_profit_prior"] = item.prior
        elif key in ("I", "G"):  # EBIT can be under I or G depending on format
            if "ebit_current" not in summary:
                summary["ebit_current"] = item.current
                summary["ebit_prior"] = item.prior
        elif key == "L":
            summary["profit_before_tax_current"] = item.current
            summary["profit_before_tax_prior"] = item.prior
        elif key == "O":
            summary["net_profit_current"] = item.current
            summary["net_profit_prior"] = item.prior

    return summary
