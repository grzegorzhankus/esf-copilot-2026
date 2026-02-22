"""Natural Language Query Engine for financial data.

This module provides a natural language interface for querying financial data,
converting user questions into structured queries and returning results.

Features:
- Text-to-SQL conversion using LLM
- Semantic search over financial analyses
- Query result formatting and explanation
- Support for Polish and English queries

Optimized for NVIDIA DGX Spark with NIM integration.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Import LLM client
from core.llm_advanced import AdvancedLLMClient, create_financial_analyst_prompt


@dataclass
class QueryResult:
    """Result of a natural language query."""
    query: str
    interpreted_query: str
    sql_equivalent: Optional[str]
    results: List[Dict[str, Any]]
    result_count: int
    explanation: str
    execution_time_ms: float
    language: str = "EN"


@dataclass
class FinancialDataStore:
    """In-memory store for financial analysis data."""
    analyses: List[Dict[str, Any]] = field(default_factory=list)
    _df: Optional[pd.DataFrame] = None

    def load_from_directory(self, directory: Path) -> int:
        """Load all analysis JSON files from a directory.

        Args:
            directory: Path to directory containing analysis JSON files.

        Returns:
            Number of files loaded.
        """
        directory = Path(directory)
        if not directory.exists():
            return 0

        loaded = 0
        for json_file in directory.glob("analysis_*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.analyses.append(data)
                    loaded += 1
            except Exception:
                continue

        self._build_dataframe()
        return loaded

    def add_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add a single analysis to the store.

        Args:
            analysis: Analysis data dictionary.
        """
        self.analyses.append(analysis)
        self._build_dataframe()

    def _build_dataframe(self) -> None:
        """Build pandas DataFrame from analyses for fast querying."""
        if not self.analyses:
            self._df = pd.DataFrame()
            return

        rows = []
        for analysis in self.analyses:
            row = {
                "filename": analysis.get("metadata", {}).get("filename", ""),
                "schema": analysis.get("metadata", {}).get("schema_id_slug", ""),
                "analyzed_at": analysis.get("metadata", {}).get("analyzed_at_utc", ""),
                "coverage": analysis.get("coverage", {}).get("percent", 0),
            }

            # Extract base metrics
            for metric in analysis.get("metrics_base", []):
                if metric.get("value") is not None:
                    row[metric["key"]] = metric["value"]

            # Extract KPIs
            for kpi in analysis.get("kpis", []):
                if kpi.get("value") is not None:
                    row[f"kpi_{kpi['key']}"] = kpi["value"]

            # Count red flags
            red_flags = analysis.get("red_flags", [])
            row["red_flag_count"] = len([f for f in red_flags if f.get("detected")])

            # Extract individual red flags
            for flag in red_flags:
                row[f"flag_{flag['key']}"] = flag.get("detected", False)

            rows.append(row)

        self._df = pd.DataFrame(rows)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Get the data as a pandas DataFrame."""
        if self._df is None:
            self._build_dataframe()
        return self._df

    def get_column_info(self) -> Dict[str, str]:
        """Get information about available columns.

        Returns:
            Dictionary mapping column names to their descriptions.
        """
        columns = {}
        if self._df is not None:
            for col in self._df.columns:
                if col.startswith("kpi_"):
                    columns[col] = f"KPI: {col.replace('kpi_', '').replace('_', ' ').title()}"
                elif col.startswith("flag_"):
                    columns[col] = f"Red Flag: {col.replace('flag_', '').replace('_', ' ').title()}"
                elif col in ["total_assets", "total_equity", "total_liabilities",
                             "current_assets", "current_liabilities", "net_income",
                             "revenue", "operating_profit", "cash"]:
                    columns[col] = f"Financial Metric: {col.replace('_', ' ').title()} (PLN)"
                else:
                    columns[col] = col.replace("_", " ").title()
        return columns


class NLQueryEngine:
    """Natural Language Query Engine for financial data.

    Uses LLM to interpret natural language queries and convert them
    to structured DataFrame operations.

    Example:
        >>> engine = NLQueryEngine()
        >>> engine.load_data(Path("outputs"))
        >>> result = engine.query("Show companies with ROE greater than 15%")
        >>> print(result.explanation)
    """

    def __init__(self, llm_client: Optional[AdvancedLLMClient] = None):
        """Initialize the query engine.

        Args:
            llm_client: Optional LLM client. If None, creates a new one.
        """
        self.llm_client = llm_client
        self.data_store = FinancialDataStore()
        self._query_cache: Dict[str, QueryResult] = {}

    def _get_llm_client(self) -> AdvancedLLMClient:
        """Get or create LLM client."""
        if self.llm_client is None:
            self.llm_client = AdvancedLLMClient()
        return self.llm_client

    def load_data(self, directory: Path) -> int:
        """Load financial data from directory.

        Args:
            directory: Path to directory with analysis files.

        Returns:
            Number of files loaded.
        """
        return self.data_store.load_from_directory(directory)

    def add_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add a single analysis to the query engine.

        Args:
            analysis: Analysis data dictionary.
        """
        self.data_store.add_analysis(analysis)

    def query(
        self,
        question: str,
        language: str = "EN",
        use_cache: bool = True
    ) -> QueryResult:
        """Execute a natural language query.

        Args:
            question: Natural language question.
            language: Language code ('EN' or 'PL').
            use_cache: Whether to use cached results.

        Returns:
            QueryResult with results and explanation.
        """
        import time
        start_time = time.time()

        # Check cache
        cache_key = f"{question.lower().strip()}_{language}"
        if use_cache and cache_key in self._query_cache:
            cached = self._query_cache[cache_key]
            return cached

        # Parse the query using LLM
        parsed = self._parse_query(question, language)

        # Execute the query
        results, sql_equiv = self._execute_query(parsed)

        # Generate explanation
        explanation = self._generate_explanation(question, results, language)

        elapsed_ms = (time.time() - start_time) * 1000

        result = QueryResult(
            query=question,
            interpreted_query=parsed.get("interpretation", question),
            sql_equivalent=sql_equiv,
            results=results,
            result_count=len(results),
            explanation=explanation,
            execution_time_ms=elapsed_ms,
            language=language
        )

        # Cache result
        self._query_cache[cache_key] = result

        return result

    def _parse_query(self, question: str, language: str) -> Dict[str, Any]:
        """Parse natural language query using LLM.

        Args:
            question: Natural language question.
            language: Language code.

        Returns:
            Parsed query structure.
        """
        df = self.data_store.dataframe
        if df.empty:
            return {"error": "No data loaded", "interpretation": question}

        # Get available columns
        columns = list(df.columns)
        column_info = self.data_store.get_column_info()

        # Build prompt for LLM
        system_prompt = self._build_parser_prompt(columns, column_info, language)

        try:
            client = self._get_llm_client()
            response = client.generate(
                prompt=question,
                system_prompt=system_prompt,
                temperature=0.1
            )

            # Parse LLM response
            return self._parse_llm_response(response)

        except Exception as e:
            # Fallback to rule-based parsing
            return self._rule_based_parse(question, language)

    def _build_parser_prompt(
        self,
        columns: List[str],
        column_info: Dict[str, str],
        language: str
    ) -> str:
        """Build system prompt for query parsing."""
        columns_desc = "\n".join([f"- {col}: {column_info.get(col, col)}" for col in columns[:30]])

        if language == "PL":
            return f"""Jesteś ekspertem od analizy danych finansowych. Twoim zadaniem jest przekształcenie pytania użytkownika w strukturę zapytania.

Dostępne kolumny danych:
{columns_desc}

Odpowiedz w formacie JSON:
{{
    "interpretation": "krótkie wyjaśnienie co użytkownik chce",
    "filter_column": "nazwa kolumny do filtrowania (lub null)",
    "filter_operator": "operator: >, <, >=, <=, ==, != (lub null)",
    "filter_value": "wartość do porównania (lub null)",
    "sort_column": "kolumna do sortowania (lub null)",
    "sort_ascending": true/false,
    "limit": liczba wyników (lub null dla wszystkich),
    "select_columns": ["lista", "kolumn", "do", "wyświetlenia"] lub null dla wszystkich,
    "aggregation": "sum/mean/count/min/max" lub null
}}

Odpowiedz TYLKO JSON, bez dodatkowego tekstu."""
        else:
            return f"""You are a financial data analysis expert. Your task is to convert the user's question into a query structure.

Available data columns:
{columns_desc}

Respond in JSON format:
{{
    "interpretation": "brief explanation of what the user wants",
    "filter_column": "column name to filter (or null)",
    "filter_operator": "operator: >, <, >=, <=, ==, != (or null)",
    "filter_value": "value to compare (or null)",
    "sort_column": "column to sort by (or null)",
    "sort_ascending": true/false,
    "limit": number of results (or null for all),
    "select_columns": ["list", "of", "columns", "to", "show"] or null for all,
    "aggregation": "sum/mean/count/min/max" or null
}}

Respond with ONLY JSON, no additional text."""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract query structure."""
        # Try to extract JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Try to parse entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        return {"interpretation": response, "error": "Could not parse LLM response"}

    def _rule_based_parse(self, question: str, language: str) -> Dict[str, Any]:
        """Fallback rule-based query parsing."""
        question_lower = question.lower()
        result = {"interpretation": question}

        # Common patterns
        patterns = {
            # ROE patterns
            r"roe\s*(>|większ[ey]|greater|above)\s*(\d+)": ("kpi_roe", ">"),
            r"roe\s*(<|mniejsz[ey]|less|below)\s*(\d+)": ("kpi_roe", "<"),
            # ROA patterns
            r"roa\s*(>|większ[ey]|greater|above)\s*(\d+)": ("kpi_roa", ">"),
            r"roa\s*(<|mniejsz[ey]|less|below)\s*(\d+)": ("kpi_roa", "<"),
            # Red flags
            r"(red flag|czerwon|warning|ostrzeżen)": ("red_flag_count", ">"),
            # Assets
            r"(assets|aktyw)\s*(>|większ|greater)\s*(\d+)": ("total_assets", ">"),
            # Current ratio
            r"(current ratio|płynność)\s*(>|większ|greater)\s*(\d+\.?\d*)": ("kpi_current_ratio", ">"),
        }

        for pattern, (column, operator) in patterns.items():
            match = re.search(pattern, question_lower)
            if match:
                groups = match.groups()
                value = float(groups[-1]) if groups[-1].replace(".", "").isdigit() else 0
                result["filter_column"] = column
                result["filter_operator"] = operator
                result["filter_value"] = value
                break

        # Check for sorting keywords
        if "najwyżs" in question_lower or "highest" in question_lower or "top" in question_lower:
            result["sort_ascending"] = False
        elif "najniżs" in question_lower or "lowest" in question_lower or "bottom" in question_lower:
            result["sort_ascending"] = True

        # Check for limit
        limit_match = re.search(r'(top|pierwsze|first)\s*(\d+)', question_lower)
        if limit_match:
            result["limit"] = int(limit_match.group(2))

        return result

    def _execute_query(
        self,
        parsed: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Execute parsed query on DataFrame.

        Args:
            parsed: Parsed query structure.

        Returns:
            Tuple of (results list, SQL equivalent string).
        """
        df = self.data_store.dataframe.copy()

        if df.empty:
            return [], None

        sql_parts = ["SELECT"]

        # Select columns
        select_cols = parsed.get("select_columns")
        if select_cols:
            df = df[[c for c in select_cols if c in df.columns]]
            sql_parts.append(", ".join(select_cols))
        else:
            sql_parts.append("*")

        sql_parts.append("FROM financial_data")

        # Apply filter
        filter_col = parsed.get("filter_column")
        filter_op = parsed.get("filter_operator")
        filter_val = parsed.get("filter_value")

        if filter_col and filter_op and filter_val is not None:
            if filter_col in df.columns:
                try:
                    if filter_op == ">":
                        df = df[df[filter_col] > filter_val]
                    elif filter_op == "<":
                        df = df[df[filter_col] < filter_val]
                    elif filter_op == ">=":
                        df = df[df[filter_col] >= filter_val]
                    elif filter_op == "<=":
                        df = df[df[filter_col] <= filter_val]
                    elif filter_op == "==":
                        df = df[df[filter_col] == filter_val]
                    elif filter_op == "!=":
                        df = df[df[filter_col] != filter_val]

                    sql_parts.append(f"WHERE {filter_col} {filter_op} {filter_val}")
                except Exception:
                    pass

        # Apply sorting
        sort_col = parsed.get("sort_column")
        sort_asc = parsed.get("sort_ascending", True)

        if sort_col and sort_col in df.columns:
            df = df.sort_values(sort_col, ascending=sort_asc)
            order = "ASC" if sort_asc else "DESC"
            sql_parts.append(f"ORDER BY {sort_col} {order}")
        elif filter_col and filter_col in df.columns:
            # Sort by filter column if no explicit sort
            df = df.sort_values(filter_col, ascending=sort_asc if sort_asc is not None else False)

        # Apply limit
        limit = parsed.get("limit")
        if limit:
            df = df.head(limit)
            sql_parts.append(f"LIMIT {limit}")

        # Apply aggregation
        agg = parsed.get("aggregation")
        if agg and filter_col:
            if agg == "sum":
                result = df[filter_col].sum()
            elif agg == "mean":
                result = df[filter_col].mean()
            elif agg == "count":
                result = len(df)
            elif agg == "min":
                result = df[filter_col].min()
            elif agg == "max":
                result = df[filter_col].max()
            else:
                result = None

            if result is not None:
                return [{"aggregation": agg, "column": filter_col, "value": result}], " ".join(sql_parts)

        # Convert to list of dicts
        results = df.to_dict("records")

        return results, " ".join(sql_parts)

    def _generate_explanation(
        self,
        question: str,
        results: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate natural language explanation of results.

        Args:
            question: Original question.
            results: Query results.
            language: Language code.

        Returns:
            Human-readable explanation.
        """
        count = len(results)

        if language == "PL":
            if count == 0:
                return "Nie znaleziono wyników spełniających kryteria zapytania."
            elif count == 1:
                return f"Znaleziono 1 wynik spełniający kryteria."
            else:
                return f"Znaleziono {count} wyników spełniających kryteria zapytania."
        else:
            if count == 0:
                return "No results found matching the query criteria."
            elif count == 1:
                return f"Found 1 result matching the criteria."
            else:
                return f"Found {count} results matching the query criteria."

    def get_sample_queries(self, language: str = "EN") -> List[str]:
        """Get sample queries for user guidance.

        Args:
            language: Language code.

        Returns:
            List of sample queries.
        """
        if language == "PL":
            return [
                "Pokaż firmy z ROE większym niż 15%",
                "Które firmy mają red flagi?",
                "Top 5 firm według aktywów",
                "Średnia rentowność wszystkich firm",
                "Firmy z ujemnym wynikiem netto",
                "Pokaż firmy z płynnością bieżącą poniżej 1",
            ]
        else:
            return [
                "Show companies with ROE greater than 15%",
                "Which companies have red flags?",
                "Top 5 companies by total assets",
                "Average profitability of all companies",
                "Companies with negative net income",
                "Show companies with current ratio below 1",
            ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded data.

        Returns:
            Dictionary with data statistics.
        """
        df = self.data_store.dataframe

        if df.empty:
            return {"loaded": False, "count": 0}

        stats = {
            "loaded": True,
            "count": len(df),
            "columns": list(df.columns),
            "numeric_columns": list(df.select_dtypes(include=["float64", "int64"]).columns),
        }

        # Add summary statistics for key metrics
        key_metrics = ["kpi_roe", "kpi_roa", "kpi_current_ratio", "total_assets", "red_flag_count"]
        for metric in key_metrics:
            if metric in df.columns:
                stats[f"{metric}_mean"] = df[metric].mean()
                stats[f"{metric}_min"] = df[metric].min()
                stats[f"{metric}_max"] = df[metric].max()

        return stats


def create_query_engine(data_directory: Optional[Path] = None) -> NLQueryEngine:
    """Factory function to create configured query engine.

    Args:
        data_directory: Optional directory to load data from.

    Returns:
        Configured NLQueryEngine instance.
    """
    engine = NLQueryEngine()

    if data_directory:
        engine.load_data(data_directory)

    return engine
