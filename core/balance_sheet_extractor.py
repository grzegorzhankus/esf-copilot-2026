"""
Dynamic Balance Sheet Extractor for Polish e-Sprawozdania XML files.

This module extracts all balance sheet items (Aktywa/Pasywa) from XML
with their full hierarchical structure and both current/prior period values.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from xml.etree.ElementTree import Element


# Polish balance sheet labels (hierarchical)
BS_LABELS_PL = {
    # AKTYWA (Assets)
    "Aktywa": "AKTYWA",
    "Aktywa_A": "A. Aktywa trwałe",
    "Aktywa_A_I": "I. Wartości niematerialne i prawne",
    "Aktywa_A_I_1": "1. Koszty zakończonych prac rozwojowych",
    "Aktywa_A_I_2": "2. Wartość firmy",
    "Aktywa_A_I_3": "3. Inne wartości niematerialne i prawne",
    "Aktywa_A_I_4": "4. Zaliczki na wartości niematerialne i prawne",
    "Aktywa_A_II": "II. Rzeczowe aktywa trwałe",
    "Aktywa_A_II_1": "1. Środki trwałe",
    "Aktywa_A_II_1_A": "a) grunty",
    "Aktywa_A_II_1_B": "b) budynki, lokale i obiekty",
    "Aktywa_A_II_1_C": "c) urządzenia techniczne i maszyny",
    "Aktywa_A_II_1_D": "d) środki transportu",
    "Aktywa_A_II_1_E": "e) inne środki trwałe",
    "Aktywa_A_II_2": "2. Środki trwałe w budowie",
    "Aktywa_A_II_3": "3. Zaliczki na środki trwałe w budowie",
    "Aktywa_A_III": "III. Należności długoterminowe",
    "Aktywa_A_III_1": "1. Od jednostek powiązanych",
    "Aktywa_A_III_2": "2. Od pozostałych jednostek",
    "Aktywa_A_III_3": "3. Od pozostałych jednostek w których posiada zaangażowanie",
    "Aktywa_A_IV": "IV. Inwestycje długoterminowe",
    "Aktywa_A_IV_1": "1. Nieruchomości",
    "Aktywa_A_IV_2": "2. Wartości niematerialne i prawne",
    "Aktywa_A_IV_3": "3. Długoterminowe aktywa finansowe",
    "Aktywa_A_IV_4": "4. Inne inwestycje długoterminowe",
    "Aktywa_A_V": "V. Długoterminowe rozliczenia międzyokresowe",
    "Aktywa_A_V_1": "1. Aktywa z tytułu odroczonego podatku dochodowego",
    "Aktywa_A_V_2": "2. Inne rozliczenia międzyokresowe",
    "Aktywa_B": "B. Aktywa obrotowe",
    "Aktywa_B_I": "I. Zapasy",
    "Aktywa_B_I_1": "1. Materiały",
    "Aktywa_B_I_2": "2. Półprodukty i produkty w toku",
    "Aktywa_B_I_3": "3. Produkty gotowe",
    "Aktywa_B_I_4": "4. Towary",
    "Aktywa_B_I_5": "5. Zaliczki na dostawy i usługi",
    "Aktywa_B_II": "II. Należności krótkoterminowe",
    "Aktywa_B_II_1": "1. Od jednostek powiązanych",
    "Aktywa_B_II_2": "2. Od jednostek z zaangażowaniem",
    "Aktywa_B_II_3": "3. Od pozostałych jednostek",
    "Aktywa_B_II_3_A": "a) z tytułu dostaw i usług",
    "Aktywa_B_II_3_B": "b) z tytułu podatków, dotacji",
    "Aktywa_B_II_3_C": "c) inne",
    "Aktywa_B_II_3_D": "d) dochodzone na drodze sądowej",
    "Aktywa_B_III": "III. Inwestycje krótkoterminowe",
    "Aktywa_B_III_1": "1. Krótkoterminowe aktywa finansowe",
    "Aktywa_B_III_1_A": "a) w jednostkach powiązanych",
    "Aktywa_B_III_1_B": "b) w pozostałych jednostkach",
    "Aktywa_B_III_1_C": "c) środki pieniężne i inne aktywa pieniężne",
    "Aktywa_B_III_2": "2. Inne inwestycje krótkoterminowe",
    "Aktywa_B_IV": "IV. Krótkoterminowe rozliczenia międzyokresowe",
    "Aktywa_C": "C. Należne wpłaty na kapitał podstawowy",
    "Aktywa_D": "D. Udziały (akcje) własne",

    # PASYWA (Equity & Liabilities)
    "Pasywa": "PASYWA",
    "Pasywa_A": "A. Kapitał (fundusz) własny",
    "Pasywa_A_I": "I. Kapitał (fundusz) podstawowy",
    "Pasywa_A_II": "II. Kapitał (fundusz) zapasowy",
    "Pasywa_A_II_1": "1. Ze sprzedaży akcji powyżej wartości nominalnej",
    "Pasywa_A_III": "III. Kapitał (fundusz) z aktualizacji wyceny",
    "Pasywa_A_III_1": "1. Z tytułu aktualizacji wyceny",
    "Pasywa_A_IV": "IV. Pozostałe kapitały (fundusze) rezerwowe",
    "Pasywa_A_IV_1": "1. Tworzony zgodnie ze statutem",
    "Pasywa_A_IV_2": "2. Na udziały (akcje) własne",
    "Pasywa_A_V": "V. Zysk (strata) z lat ubiegłych",
    "Pasywa_A_VI": "VI. Zysk (strata) netto",
    "Pasywa_A_VII": "VII. Odpisy z zysku netto w ciągu roku obrotowego",
    "Pasywa_B": "B. Zobowiązania i rezerwy na zobowiązania",
    "Pasywa_B_I": "I. Rezerwy na zobowiązania",
    "Pasywa_B_I_1": "1. Rezerwa z tytułu odroczonego podatku dochodowego",
    "Pasywa_B_I_2": "2. Rezerwa na świadczenia emerytalne i podobne",
    "Pasywa_B_I_2_1": "a) długoterminowa",
    "Pasywa_B_I_2_2": "b) krótkoterminowa",
    "Pasywa_B_I_3": "3. Pozostałe rezerwy",
    "Pasywa_B_I_3_1": "a) długoterminowe",
    "Pasywa_B_I_3_2": "b) krótkoterminowe",
    "Pasywa_B_II": "II. Zobowiązania długoterminowe",
    "Pasywa_B_II_1": "1. Wobec jednostek powiązanych",
    "Pasywa_B_II_2": "2. Wobec jednostek z zaangażowaniem",
    "Pasywa_B_II_3": "3. Wobec pozostałych jednostek",
    "Pasywa_B_II_3_A": "a) kredyty i pożyczki",
    "Pasywa_B_II_3_B": "b) z tytułu emisji dłużnych papierów wartościowych",
    "Pasywa_B_II_3_C": "c) inne zobowiązania finansowe",
    "Pasywa_B_II_3_D": "d) zobowiązania wekslowe",
    "Pasywa_B_II_3_E": "e) inne",
    "Pasywa_B_III": "III. Zobowiązania krótkoterminowe",
    "Pasywa_B_III_1": "1. Wobec jednostek powiązanych",
    "Pasywa_B_III_2": "2. Wobec jednostek z zaangażowaniem",
    "Pasywa_B_III_3": "3. Wobec pozostałych jednostek",
    "Pasywa_B_III_3_A": "a) kredyty i pożyczki",
    "Pasywa_B_III_3_B": "b) z tytułu emisji dłużnych papierów wartościowych",
    "Pasywa_B_III_3_C": "c) inne zobowiązania finansowe",
    "Pasywa_B_III_3_D": "d) z tytułu dostaw i usług",
    "Pasywa_B_III_3_D_1": "- do 12 miesięcy",
    "Pasywa_B_III_3_D_2": "- powyżej 12 miesięcy",
    "Pasywa_B_III_3_E": "e) zaliczki otrzymane na dostawy i usługi",
    "Pasywa_B_III_3_F": "f) zobowiązania wekslowe",
    "Pasywa_B_III_3_G": "g) z tytułu podatków, ceł, ubezpieczeń społecznych",
    "Pasywa_B_III_3_H": "h) z tytułu wynagrodzeń",
    "Pasywa_B_III_3_I": "i) inne",
    "Pasywa_B_III_4": "4. Fundusze specjalne",
    "Pasywa_B_IV": "IV. Rozliczenia międzyokresowe",
    "Pasywa_B_IV_1": "1. Ujemna wartość firmy",
    "Pasywa_B_IV_2": "2. Inne rozliczenia międzyokresowe",
    "Pasywa_B_IV_2_1": "a) długoterminowe",
    "Pasywa_B_IV_2_2": "b) krótkoterminowe",
}

# English labels
BS_LABELS_EN = {
    # AKTYWA (Assets)
    "Aktywa": "ASSETS",
    "Aktywa_A": "A. Fixed assets",
    "Aktywa_A_I": "I. Intangible assets",
    "Aktywa_A_I_1": "1. R&D costs",
    "Aktywa_A_I_2": "2. Goodwill",
    "Aktywa_A_I_3": "3. Other intangible assets",
    "Aktywa_A_I_4": "4. Advances on intangible assets",
    "Aktywa_A_II": "II. Tangible fixed assets",
    "Aktywa_A_II_1": "1. Fixed assets",
    "Aktywa_A_II_1_A": "a) land",
    "Aktywa_A_II_1_B": "b) buildings and structures",
    "Aktywa_A_II_1_C": "c) plant and machinery",
    "Aktywa_A_II_1_D": "d) vehicles",
    "Aktywa_A_II_1_E": "e) other fixed assets",
    "Aktywa_A_II_2": "2. Fixed assets under construction",
    "Aktywa_A_II_3": "3. Advances for construction",
    "Aktywa_A_III": "III. Long-term receivables",
    "Aktywa_A_III_1": "1. From related parties",
    "Aktywa_A_III_2": "2. From other entities",
    "Aktywa_A_III_3": "3. From entities with investment",
    "Aktywa_A_IV": "IV. Long-term investments",
    "Aktywa_A_IV_1": "1. Real estate",
    "Aktywa_A_IV_2": "2. Intangible assets",
    "Aktywa_A_IV_3": "3. Long-term financial assets",
    "Aktywa_A_IV_4": "4. Other long-term investments",
    "Aktywa_A_V": "V. Long-term prepayments",
    "Aktywa_A_V_1": "1. Deferred tax assets",
    "Aktywa_A_V_2": "2. Other prepayments",
    "Aktywa_B": "B. Current assets",
    "Aktywa_B_I": "I. Inventories",
    "Aktywa_B_I_1": "1. Materials",
    "Aktywa_B_I_2": "2. Work in progress",
    "Aktywa_B_I_3": "3. Finished goods",
    "Aktywa_B_I_4": "4. Goods for resale",
    "Aktywa_B_I_5": "5. Advances for deliveries",
    "Aktywa_B_II": "II. Short-term receivables",
    "Aktywa_B_II_1": "1. From related parties",
    "Aktywa_B_II_2": "2. From entities with investment",
    "Aktywa_B_II_3": "3. From other entities",
    "Aktywa_B_II_3_A": "a) trade receivables",
    "Aktywa_B_II_3_B": "b) taxes, subsidies receivable",
    "Aktywa_B_II_3_C": "c) other",
    "Aktywa_B_II_3_D": "d) claimed at court",
    "Aktywa_B_III": "III. Short-term investments",
    "Aktywa_B_III_1": "1. Short-term financial assets",
    "Aktywa_B_III_1_A": "a) in related parties",
    "Aktywa_B_III_1_B": "b) in other entities",
    "Aktywa_B_III_1_C": "c) cash and cash equivalents",
    "Aktywa_B_III_2": "2. Other short-term investments",
    "Aktywa_B_IV": "IV. Short-term prepayments",
    "Aktywa_C": "C. Called up share capital not paid",
    "Aktywa_D": "D. Own shares",

    # PASYWA (Equity & Liabilities)
    "Pasywa": "EQUITY AND LIABILITIES",
    "Pasywa_A": "A. Equity",
    "Pasywa_A_I": "I. Share capital",
    "Pasywa_A_II": "II. Share premium",
    "Pasywa_A_II_1": "1. From share issue above nominal value",
    "Pasywa_A_III": "III. Revaluation reserve",
    "Pasywa_A_III_1": "1. From revaluation",
    "Pasywa_A_IV": "IV. Other reserves",
    "Pasywa_A_IV_1": "1. Created per statute",
    "Pasywa_A_IV_2": "2. For own shares",
    "Pasywa_A_V": "V. Retained earnings",
    "Pasywa_A_VI": "VI. Net profit (loss)",
    "Pasywa_A_VII": "VII. Write-offs during year",
    "Pasywa_B": "B. Liabilities and provisions",
    "Pasywa_B_I": "I. Provisions",
    "Pasywa_B_I_1": "1. Deferred tax provision",
    "Pasywa_B_I_2": "2. Pension and similar provisions",
    "Pasywa_B_I_2_1": "a) long-term",
    "Pasywa_B_I_2_2": "b) short-term",
    "Pasywa_B_I_3": "3. Other provisions",
    "Pasywa_B_I_3_1": "a) long-term",
    "Pasywa_B_I_3_2": "b) short-term",
    "Pasywa_B_II": "II. Long-term liabilities",
    "Pasywa_B_II_1": "1. To related parties",
    "Pasywa_B_II_2": "2. To entities with investment",
    "Pasywa_B_II_3": "3. To other entities",
    "Pasywa_B_II_3_A": "a) loans and borrowings",
    "Pasywa_B_II_3_B": "b) debt securities",
    "Pasywa_B_II_3_C": "c) other financial liabilities",
    "Pasywa_B_II_3_D": "d) bills of exchange",
    "Pasywa_B_II_3_E": "e) other",
    "Pasywa_B_III": "III. Short-term liabilities",
    "Pasywa_B_III_1": "1. To related parties",
    "Pasywa_B_III_2": "2. To entities with investment",
    "Pasywa_B_III_3": "3. To other entities",
    "Pasywa_B_III_3_A": "a) loans and borrowings",
    "Pasywa_B_III_3_B": "b) debt securities",
    "Pasywa_B_III_3_C": "c) other financial liabilities",
    "Pasywa_B_III_3_D": "d) trade payables",
    "Pasywa_B_III_3_D_1": "- up to 12 months",
    "Pasywa_B_III_3_D_2": "- over 12 months",
    "Pasywa_B_III_3_E": "e) advances received",
    "Pasywa_B_III_3_F": "f) bills of exchange",
    "Pasywa_B_III_3_G": "g) taxes and social security",
    "Pasywa_B_III_3_H": "h) wages payable",
    "Pasywa_B_III_3_I": "i) other",
    "Pasywa_B_III_4": "4. Special funds",
    "Pasywa_B_IV": "IV. Accruals",
    "Pasywa_B_IV_1": "1. Negative goodwill",
    "Pasywa_B_IV_2": "2. Other accruals",
    "Pasywa_B_IV_2_1": "a) long-term",
    "Pasywa_B_IV_2_2": "b) short-term",
}


@dataclass
class BalanceSheetItem:
    """Single balance sheet line item."""
    key: str  # e.g., "Aktywa_A_I_1"
    label_pl: str
    label_en: str
    level: int  # hierarchy level (0=total, 1=A/B, 2=I/II, 3=1/2, etc.)
    current: Optional[float]  # KwotaA
    prior: Optional[float]  # KwotaB

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _get_local_name(tag: str) -> str:
    """Strip namespace from element tag."""
    if "}" in tag:
        return tag.split("}")[1]
    return tag


def _extract_kwota(elem: Element, kwota_name: str) -> Optional[float]:
    """Extract KwotaA or KwotaB value from element."""
    for child in elem:
        local_name = _get_local_name(child.tag)
        if local_name == kwota_name and child.text:
            try:
                return float(child.text.strip())
            except (ValueError, AttributeError):
                return None
    return None


def _get_level(key: str) -> int:
    """Determine hierarchy level from key."""
    # Count underscores and segments to determine level
    parts = key.split("_")
    if len(parts) == 1:  # "Aktywa" or "Pasywa"
        return 0
    elif len(parts) == 2:  # "Aktywa_A"
        return 1
    elif len(parts) == 3:  # "Aktywa_A_I"
        return 2
    elif len(parts) == 4:  # "Aktywa_A_I_1"
        return 3
    elif len(parts) == 5:  # "Aktywa_A_I_1_A"
        return 4
    else:
        return 5


def _extract_balance_sheet_items(elem: Element, parent_key: str = "") -> List[BalanceSheetItem]:
    """Recursively extract balance sheet items from XML element."""
    items = []

    local_name = _get_local_name(elem.tag)

    # Check if this is a balance sheet item (Aktywa* or Pasywa*)
    is_bs_item = local_name.startswith("Aktywa") or local_name.startswith("Pasywa")

    if is_bs_item:
        current = _extract_kwota(elem, "KwotaA")
        prior = _extract_kwota(elem, "KwotaB")

        # Only add items that have values
        if current is not None or prior is not None:
            key = local_name
            label_pl = BS_LABELS_PL.get(key, key)
            label_en = BS_LABELS_EN.get(key, key)
            level = _get_level(key)

            items.append(BalanceSheetItem(
                key=key,
                label_pl=label_pl,
                label_en=label_en,
                level=level,
                current=current,
                prior=prior
            ))

    # Recurse into children
    for child in elem:
        items.extend(_extract_balance_sheet_items(child, local_name))

    return items


def extract_balance_sheet(root: Element) -> List[BalanceSheetItem]:
    """
    Extract complete balance sheet from XML root element.

    Args:
        root: XML root element

    Returns:
        List of BalanceSheetItem objects in hierarchical order
    """
    items = []

    # Find Bilans section
    for elem in root.iter():
        local_name = _get_local_name(elem.tag)
        if local_name == "Bilans":
            # Extract from Aktywa and Pasywa sections
            for child in elem:
                child_name = _get_local_name(child.tag)
                if child_name in ("Aktywa", "Pasywa"):
                    items.extend(_extract_balance_sheet_items(child))
            break

    return items


def balance_sheet_to_dict(items: List[BalanceSheetItem]) -> List[Dict[str, Any]]:
    """Convert balance sheet items to dictionary format for JSON serialization."""
    return [item.to_dict() for item in items]


def get_balance_sheet_summary(items: List[BalanceSheetItem]) -> Dict[str, Any]:
    """
    Extract key balance sheet summary values.

    Returns dict with:
        - total_assets, total_assets_prior
        - total_equity, total_equity_prior
        - total_liabilities, total_liabilities_prior
    """
    summary = {}

    for item in items:
        if item.key == "Aktywa":
            summary["total_assets"] = item.current
            summary["total_assets_prior"] = item.prior
        elif item.key == "Pasywa_A":
            summary["total_equity"] = item.current
            summary["total_equity_prior"] = item.prior
        elif item.key == "Pasywa_B":
            summary["total_liabilities"] = item.current
            summary["total_liabilities_prior"] = item.prior
        elif item.key == "Aktywa_A":
            summary["fixed_assets"] = item.current
            summary["fixed_assets_prior"] = item.prior
        elif item.key == "Aktywa_B":
            summary["current_assets"] = item.current
            summary["current_assets_prior"] = item.prior
        elif item.key == "Aktywa_B_III_1_C":
            summary["cash"] = item.current
            summary["cash_prior"] = item.prior
        elif item.key == "Pasywa_A_VI":
            summary["net_profit"] = item.current
            summary["net_profit_prior"] = item.prior

    return summary
