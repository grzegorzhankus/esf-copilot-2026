"""Cash Flow Extractor for Polish e-Sprawozdanie XML.

Extracts Cash Flow Statement (Rachunek Przepływów Pieniężnych) data from XML
with hierarchical structure and both current and prior period values.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from xml.etree.ElementTree import Element


@dataclass
class CFItem:
    """A single Cash Flow line item."""
    key: str
    label_pl: str
    label_en: str
    level: int
    current: Optional[float]
    prior: Optional[float]


# Cash Flow item labels for Rachunek Przepływów Pieniężnych (Pośredni format)
CF_LABELS = {
    # Level 0 - Total
    "RachPrzeplywow": ("RACHUNEK PRZEPŁYWÓW PIENIĘŻNYCH", "CASH FLOW STATEMENT"),
    "PrzeplywyPosr": ("Metoda pośrednia", "Indirect method"),
    "PrzeplywyBezposr": ("Metoda bezpośrednia", "Direct method"),

    # A - Operating Activities
    "A": ("A. Przepływy środków pieniężnych z działalności operacyjnej", "A. Cash flows from operating activities"),
    "A_I": ("I. Zysk (strata) netto", "I. Net profit (loss)"),
    "A_II": ("II. Korekty razem", "II. Total adjustments"),
    "A_II_1": ("1. Amortyzacja", "1. Depreciation and amortization"),
    "A_II_2": ("2. Zyski (straty) z tytułu różnic kursowych", "2. Foreign exchange gains (losses)"),
    "A_II_3": ("3. Odsetki i udziały w zyskach (dywidendy)", "3. Interest and dividends"),
    "A_II_4": ("4. Zysk (strata) z działalności inwestycyjnej", "4. Profit (loss) from investing activities"),
    "A_II_5": ("5. Zmiana stanu rezerw", "5. Change in provisions"),
    "A_II_6": ("6. Zmiana stanu zapasów", "6. Change in inventories"),
    "A_II_7": ("7. Zmiana stanu należności", "7. Change in receivables"),
    "A_II_8": ("8. Zmiana stanu zobowiązań krótkoterminowych", "8. Change in short-term liabilities"),
    "A_II_9": ("9. Zmiana stanu rozliczeń międzyokresowych", "9. Change in prepayments and accruals"),
    "A_II_10": ("10. Inne korekty", "10. Other adjustments"),
    "A_III": ("III. Przepływy pieniężne netto z działalności operacyjnej", "III. Net cash from operating activities"),

    # B - Investing Activities
    "B": ("B. Przepływy środków pieniężnych z działalności inwestycyjnej", "B. Cash flows from investing activities"),
    "B_I": ("I. Wpływy", "I. Inflows"),
    "B_I_1": ("1. Zbycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych", "1. Disposal of intangible and tangible assets"),
    "B_I_2": ("2. Zbycie inwestycji w nieruchomości oraz wartości niematerialne i prawne", "2. Disposal of investment property"),
    "B_I_3": ("3. Z aktywów finansowych", "3. From financial assets"),
    "B_I_3_A": ("a) w jednostkach powiązanych", "a) in related parties"),
    "B_I_3_B": ("b) w pozostałych jednostkach", "b) in other entities"),
    "B_I_3_B_1": ("- zbycie aktywów finansowych", "- disposal of financial assets"),
    "B_I_3_B_2": ("- dywidendy i udziały w zyskach", "- dividends and profit shares"),
    "B_I_3_B_3": ("- spłata udzielonych pożyczek długoterminowych", "- repayment of long-term loans"),
    "B_I_3_B_4": ("- odsetki", "- interest"),
    "B_I_3_B_5": ("- inne wpływy z aktywów finansowych", "- other inflows from financial assets"),
    "B_I_4": ("4. Inne wpływy inwestycyjne", "4. Other investing inflows"),
    "B_II": ("II. Wydatki", "II. Outflows"),
    "B_II_1": ("1. Nabycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych", "1. Acquisition of intangible and tangible assets"),
    "B_II_2": ("2. Inwestycje w nieruchomości oraz wartości niematerialne i prawne", "2. Investment in property"),
    "B_II_3": ("3. Na aktywa finansowe", "3. For financial assets"),
    "B_II_3_A": ("a) w jednostkach powiązanych", "a) in related parties"),
    "B_II_3_B": ("b) w pozostałych jednostkach", "b) in other entities"),
    "B_II_4": ("4. Inne wydatki inwestycyjne", "4. Other investing outflows"),
    "B_III": ("III. Przepływy pieniężne netto z działalności inwestycyjnej", "III. Net cash from investing activities"),

    # C - Financing Activities
    "C": ("C. Przepływy środków pieniężnych z działalności finansowej", "C. Cash flows from financing activities"),
    "C_I": ("I. Wpływy", "I. Inflows"),
    "C_I_1": ("1. Wpływy netto z wydania udziałów (emisji akcji) i innych instrumentów kapitałowych", "1. Net proceeds from share issuance"),
    "C_I_2": ("2. Kredyty i pożyczki", "2. Loans and borrowings"),
    "C_I_3": ("3. Emisja dłużnych papierów wartościowych", "3. Debt securities issued"),
    "C_I_4": ("4. Inne wpływy finansowe", "4. Other financing inflows"),
    "C_II": ("II. Wydatki", "II. Outflows"),
    "C_II_1": ("1. Nabycie udziałów (akcji) własnych", "1. Acquisition of treasury shares"),
    "C_II_2": ("2. Dywidendy i inne wypłaty na rzecz właścicieli", "2. Dividends and other payments to owners"),
    "C_II_3": ("3. Inne, niż wypłaty na rzecz właścicieli, wydatki z tytułu podziału zysku", "3. Other profit distribution"),
    "C_II_4": ("4. Spłaty kredytów i pożyczek", "4. Repayment of loans"),
    "C_II_5": ("5. Wykup dłużnych papierów wartościowych", "5. Redemption of debt securities"),
    "C_II_6": ("6. Z tytułu innych zobowiązań finansowych", "6. Other financial liabilities"),
    "C_II_7": ("7. Płatności zobowiązań z tytułu umów leasingu finansowego", "7. Finance lease payments"),
    "C_II_8": ("8. Odsetki", "8. Interest paid"),
    "C_II_9": ("9. Inne wydatki finansowe", "9. Other financing outflows"),
    "C_III": ("III. Przepływy pieniężne netto z działalności finansowej", "III. Net cash from financing activities"),

    # D, E, F - Summary
    "D": ("D. Przepływy pieniężne netto razem", "D. Total net cash flows"),
    "E": ("E. Bilansowa zmiana stanu środków pieniężnych", "E. Balance sheet change in cash"),
    "F": ("F. Środki pieniężne na początek okresu", "F. Cash at beginning of period"),
    "G": ("G. Środki pieniężne na koniec okresu", "G. Cash at end of period"),
}

# Additional nested keys that may appear with doubled prefixes
# e.g., A_A_II -> should map to A_II labels
for parent in ["A", "B", "C"]:
    for sub in ["I", "II", "III"]:
        # Handle A_A_II format
        doubled_key = f"{parent}_{parent}_{sub}"
        simple_key = f"{parent}_{sub}"
        if simple_key in CF_LABELS:
            CF_LABELS[doubled_key] = CF_LABELS[simple_key]

        # Handle deeper nesting: A_A_II_1, A_A_II_A_II_1, etc.
        for num in range(1, 15):
            # A_A_II_1 -> A_II_1
            doubled_num_key = f"{parent}_{parent}_{sub}_{num}"
            simple_num_key = f"{parent}_{sub}_{num}"
            if simple_num_key in CF_LABELS:
                CF_LABELS[doubled_num_key] = CF_LABELS[simple_num_key]

            # A_A_II_A_II_1 -> A_II_1 (extremely nested)
            extra_nested_key = f"{parent}_{parent}_{sub}_{parent}_{sub}_{num}"
            if simple_num_key in CF_LABELS:
                CF_LABELS[extra_nested_key] = CF_LABELS[simple_num_key]

# Handle sub-items with letters (e.g., B_I_3_A, B_I_3_B, C_II_7, etc.)
for parent in ["A", "B", "C"]:
    for sub in ["I", "II", "III"]:
        for num in range(1, 15):
            # Handle A, B suffixes
            for letter in ["A", "B"]:
                simple_key = f"{parent}_{sub}_{num}_{letter}"
                doubled_key = f"{parent}_{parent}_{sub}_{num}_{letter}"
                extra_nested = f"{parent}_{parent}_{sub}_{parent}_{sub}_{num}_{letter}"
                if simple_key in CF_LABELS:
                    CF_LABELS[doubled_key] = CF_LABELS[simple_key]
                    CF_LABELS[extra_nested] = CF_LABELS[simple_key]

                # Handle deeper: B_I_3_B_1, etc.
                for subnum in range(1, 10):
                    deep_simple = f"{parent}_{sub}_{num}_{letter}_{subnum}"
                    deep_doubled = f"{parent}_{parent}_{sub}_{num}_{letter}_{subnum}"
                    deep_extra = f"{parent}_{parent}_{sub}_{parent}_{sub}_{num}_{letter}_{subnum}"
                    if deep_simple in CF_LABELS:
                        CF_LABELS[deep_doubled] = CF_LABELS[deep_simple]
                        CF_LABELS[deep_extra] = CF_LABELS[deep_simple]


def _get_label(key: str) -> tuple:
    """Get Polish and English labels for a Cash Flow item key."""
    # Remove prefixes
    clean_key = key.replace("RachPrzeplywow_", "").replace("PrzeplywyPosr_", "").replace("PrzeplywyBezposr_", "")

    # Try exact match first
    if clean_key in CF_LABELS:
        return CF_LABELS[clean_key]

    # Handle complex nested patterns like A_A_II_A_II_1
    parts = clean_key.split("_")

    # Pattern: A_A_II_A_II_1 -> A_II_1
    # Check if we have repeating section pattern
    if len(parts) >= 5:
        # Try A_A_II_A_II_1 -> A_II_1
        if parts[0] == parts[1] == parts[3] and parts[2] == parts[4]:
            simplified = "_".join([parts[0], parts[2]] + parts[5:])
            if simplified in CF_LABELS:
                return CF_LABELS[simplified]

    # Pattern: A_A_II_1 -> A_II_1 (doubled prefix with suffix)
    if len(parts) >= 4 and parts[0] == parts[1]:
        simplified = "_".join([parts[0]] + parts[2:])
        if simplified in CF_LABELS:
            return CF_LABELS[simplified]

    # Pattern: A_A_II -> A_II (simple doubled prefix)
    if len(parts) >= 3 and parts[0] == parts[1]:
        simplified = "_".join([parts[0]] + parts[2:])
        if simplified in CF_LABELS:
            return CF_LABELS[simplified]

    # Try just removing the first duplicate: A_A_II -> A_II
    if len(parts) >= 2 and parts[0] == parts[1]:
        simplified = "_".join(parts[1:])
        if simplified in CF_LABELS:
            return CF_LABELS[simplified]

    # Default label from key - display in dotted format
    display_key = clean_key.replace("_", ".")
    return (display_key, display_key)


def _get_level(key: str) -> int:
    """Determine hierarchy level from key structure."""
    clean = key.replace("RachPrzeplywow_", "").replace("PrzeplywyPosr_", "").replace("PrzeplywyBezposr_", "")

    # Remove doubled prefix if present (A_A_II -> A_II)
    parts = clean.split("_")
    if len(parts) >= 2 and parts[0] == parts[1]:
        parts = parts[1:]
        clean = "_".join(parts)

    # Determine level
    if clean in ("RachPrzeplywow", "PrzeplywyPosr", "PrzeplywyBezposr"):
        return 0
    elif clean in ("A", "B", "C", "D", "E", "F", "G"):
        return 1
    elif len(parts) == 2 and parts[1] in ("I", "II", "III"):
        return 2
    elif len(parts) == 3:
        return 3
    elif len(parts) >= 4:
        return 4
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


def _extract_cf_recursive(node: Element, parent_key: str = "", items: List[CFItem] = None) -> List[CFItem]:
    """Recursively extract Cash Flow items from XML structure."""
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

    # Only add if it's a CF item (has amounts or is a known category)
    clean_key = key.replace("RachPrzeplywow_", "").replace("PrzeplywyPosr_", "").replace("PrzeplywyBezposr_", "")
    if current is not None or prior is not None or clean_key in CF_LABELS or local in CF_LABELS:
        label_pl, label_en = _get_label(key)
        level = _get_level(key)

        items.append(CFItem(
            key=key,
            label_pl=label_pl,
            label_en=label_en,
            level=level,
            current=current,
            prior=prior,
        ))

    # Recurse into children
    for child in node:
        _extract_cf_recursive(child, key, items)

    return items


def extract_cash_flow(root: Element) -> List[CFItem]:
    """Extract all Cash Flow items from XML root.

    Args:
        root: XML ElementTree root element.

    Returns:
        List of CFItem objects representing the cash flow structure.
    """
    items = []

    # Find RachPrzeplywow (Cash Flow Statement) section
    for elem in root.iter():
        local = _localname(elem.tag)
        if local == "RachPrzeplywow":
            # Found Cash Flow section, extract items
            _extract_cf_recursive(elem, "", items)
            break

    return items


def cf_to_dict(items: List[CFItem]) -> List[Dict[str, Any]]:
    """Convert CFItem list to list of dictionaries.

    Args:
        items: List of CFItem objects.

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


def get_cf_summary(items: List[CFItem]) -> Dict[str, Optional[float]]:
    """Extract key Cash Flow summary values.

    Args:
        items: List of CFItem objects.

    Returns:
        Dictionary with key CF metrics.
    """
    summary = {}

    for item in items:
        clean = item.key.replace("RachPrzeplywow_", "").replace("PrzeplywyPosr_", "").replace("PrzeplywyBezposr_", "")
        # Remove doubled prefix
        parts = clean.split("_")
        if len(parts) >= 2 and parts[0] == parts[1]:
            clean = "_".join(parts[1:])

        if clean == "A_III" or clean == "A_A_III":
            summary["operating_total"] = item.current
            summary["operating_total_prior"] = item.prior
        elif clean == "B_III" or clean == "B_B_III":
            summary["investing_total"] = item.current
            summary["investing_total_prior"] = item.prior
        elif clean == "C_III" or clean == "C_C_III":
            summary["financing_total"] = item.current
            summary["financing_total_prior"] = item.prior
        elif clean == "D":
            summary["net_change"] = item.current
            summary["net_change_prior"] = item.prior
        elif clean == "F":
            summary["opening_balance"] = item.current
        elif clean == "G":
            summary["closing_balance"] = item.current

    return summary
