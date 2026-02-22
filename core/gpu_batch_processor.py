"""GPU-accelerated batch processing for financial statement analysis.

This module provides high-performance batch processing of XML files using:
- RAPIDS cuDF for GPU-accelerated DataFrames (if available)
- Concurrent processing with ThreadPoolExecutor (CPU fallback)
- Parallel KPI calculations
- Real-time progress tracking

Optimized for NVIDIA DGX Spark with Grace Blackwell architecture.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Try to import RAPIDS for GPU acceleration
GPU_AVAILABLE = False
try:
    import cudf
    import cupy as cp
    GPU_AVAILABLE = True
    print("✓ RAPIDS GPU acceleration available")
except ImportError:
    import pandas as pd
    print("⚠ RAPIDS not installed - using CPU (pandas)")

# Import core analysis modules
from core.xml_loader import parse_xml_bytes, XmlParseError
from core.schema_detector import detect_schema_id, schema_id_to_slug
from core.mapping_engine import load_mapping, compute_metrics
from core.kpi_calculator import calculate_kpis
from core.red_flags import detect_red_flags
from core.contracts import (
    AnalysisResult, Metadata, MetricValue, Coverage, KPI, RedFlag
)


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_files: int
    successful: int
    failed: int
    processing_time_seconds: float
    files_per_second: float
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    gpu_accelerated: bool = False


@dataclass
class ProcessingStats:
    """Real-time processing statistics."""
    processed: int = 0
    successful: int = 0
    failed: int = 0
    current_file: str = ""
    elapsed_seconds: float = 0.0
    estimated_remaining_seconds: float = 0.0
    files_per_second: float = 0.0


class GPUBatchProcessor:
    """High-performance batch processor for financial statements.

    Uses GPU acceleration when RAPIDS is available, falls back to
    multi-threaded CPU processing otherwise.

    Example:
        >>> processor = GPUBatchProcessor(max_workers=8)
        >>> results = processor.process_directory("data/xml_files/")
        >>> print(f"Processed {results.successful} files at {results.files_per_second:.1f} files/sec")
    """

    def __init__(
        self,
        max_workers: int = 8,
        use_gpu: bool = True,
        progress_callback: Optional[Callable[[ProcessingStats], None]] = None
    ):
        """Initialize batch processor.

        Args:
            max_workers: Number of parallel workers for CPU processing.
            use_gpu: Whether to use GPU acceleration if available.
            progress_callback: Optional callback for progress updates.
        """
        self.max_workers = max_workers
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.progress_callback = progress_callback
        self._stats = ProcessingStats()

    def process_files(
        self,
        file_paths: List[Path],
        output_dir: Optional[Path] = None
    ) -> BatchResult:
        """Process multiple XML files in batch.

        Args:
            file_paths: List of XML file paths to process.
            output_dir: Optional directory to save results.

        Returns:
            BatchResult with processing statistics and results.
        """
        start_time = time.time()
        results = []
        errors = []

        total_files = len(file_paths)
        self._stats = ProcessingStats()

        if self.use_gpu:
            # GPU-accelerated processing
            results, errors = self._process_gpu(file_paths)
        else:
            # CPU multi-threaded processing
            results, errors = self._process_cpu(file_paths)

        elapsed = time.time() - start_time
        successful = len(results)
        failed = len(errors)

        # Save results if output directory specified
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save batch summary
            summary_path = output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_files": total_files,
                    "successful": successful,
                    "failed": failed,
                    "processing_time_seconds": elapsed,
                    "files_per_second": successful / elapsed if elapsed > 0 else 0,
                    "gpu_accelerated": self.use_gpu,
                    "errors": errors
                }, f, indent=2)

        return BatchResult(
            total_files=total_files,
            successful=successful,
            failed=failed,
            processing_time_seconds=elapsed,
            files_per_second=successful / elapsed if elapsed > 0 else 0,
            results=results,
            errors=errors,
            gpu_accelerated=self.use_gpu
        )

    def process_directory(
        self,
        directory: Path,
        pattern: str = "*.xml",
        output_dir: Optional[Path] = None
    ) -> BatchResult:
        """Process all XML files in a directory.

        Args:
            directory: Directory containing XML files.
            pattern: Glob pattern for file matching.
            output_dir: Optional directory to save results.

        Returns:
            BatchResult with processing statistics and results.
        """
        directory = Path(directory)
        file_paths = list(directory.glob(pattern))
        return self.process_files(file_paths, output_dir)

    def _process_gpu(
        self,
        file_paths: List[Path]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Process files using GPU acceleration.

        Uses RAPIDS cuDF for GPU-accelerated DataFrame operations.
        """
        results = []
        errors = []

        # First, parse all files and extract metrics (CPU-bound, parallelized)
        raw_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._analyze_single_file, fp): fp
                for fp in file_paths
            }

            for future in as_completed(futures):
                fp = futures[future]
                self._stats.processed += 1
                self._stats.current_file = fp.name

                try:
                    result = future.result()
                    if result:
                        raw_results.append(result)
                        self._stats.successful += 1
                    else:
                        errors.append({"file": str(fp), "error": "Analysis returned None"})
                        self._stats.failed += 1
                except Exception as e:
                    errors.append({"file": str(fp), "error": str(e)})
                    self._stats.failed += 1

                self._update_progress()

        # Convert to GPU DataFrame for fast aggregation
        if raw_results and GPU_AVAILABLE:
            try:
                # Extract metrics for GPU processing
                metrics_data = []
                for r in raw_results:
                    row = {"filename": r["metadata"]["filename"]}
                    for m in r.get("metrics_base", []):
                        if m["value"] is not None:
                            row[m["key"]] = m["value"]
                    for k in r.get("kpis", []):
                        if k["value"] is not None:
                            row[f"kpi_{k['key']}"] = k["value"]
                    metrics_data.append(row)

                # Create GPU DataFrame
                gdf = cudf.DataFrame(metrics_data)

                # GPU-accelerated statistics calculation
                summary_stats = {}
                numeric_cols = gdf.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns
                for col in numeric_cols:
                    summary_stats[col] = {
                        "mean": float(gdf[col].mean()),
                        "std": float(gdf[col].std()),
                        "min": float(gdf[col].min()),
                        "max": float(gdf[col].max()),
                        "median": float(gdf[col].median())
                    }

                # Add summary stats to results
                for r in raw_results:
                    r["batch_statistics"] = summary_stats
                    results.append(r)

            except Exception as e:
                print(f"GPU aggregation failed, using CPU: {e}")
                results = raw_results
        else:
            results = raw_results

        return results, errors

    def _process_cpu(
        self,
        file_paths: List[Path]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Process files using CPU multi-threading."""
        results = []
        errors = []

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._analyze_single_file, fp): fp
                for fp in file_paths
            }

            for future in as_completed(futures):
                fp = futures[future]
                self._stats.processed += 1
                self._stats.current_file = fp.name
                self._stats.elapsed_seconds = time.time() - start_time

                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        self._stats.successful += 1
                    else:
                        errors.append({"file": str(fp), "error": "Analysis returned None"})
                        self._stats.failed += 1
                except Exception as e:
                    errors.append({"file": str(fp), "error": str(e)})
                    self._stats.failed += 1

                self._update_progress()

        return results, errors

    def _analyze_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single XML file.

        Args:
            file_path: Path to XML file.

        Returns:
            Analysis result as dictionary, or None if failed.
        """
        try:
            # Read file
            xml_bytes = file_path.read_bytes()
            file_size = len(xml_bytes)

            # Parse XML
            root = parse_xml_bytes(xml_bytes)

            # Detect schema
            schema_id = detect_schema_id(root)
            schema_slug = schema_id_to_slug(schema_id)

            # Load mapping
            mapping = load_mapping(schema_slug)
            if not mapping:
                # Try default mapping
                mapping = load_mapping("mf_2025_jednostka_inna")

            if not mapping:
                return None

            # Extract metrics
            metrics, coverage = compute_metrics(root, mapping)

            # Calculate KPIs
            metrics_dict = {m.key: m.value for m in metrics if m.value is not None}
            kpis = calculate_kpis(metrics_dict)
            kpis_dict = {k.key: k.value for k in kpis if k.value is not None}

            # Detect red flags
            red_flags = detect_red_flags(metrics_dict, kpis_dict)

            # Build result
            metadata = Metadata(
                schema_id=schema_id,
                schema_id_slug=schema_slug,
                filename=file_path.name,
                file_size_bytes=file_size,
                analyzed_at_utc=datetime.now(timezone.utc).isoformat()
            )

            result = AnalysisResult(
                metadata=metadata,
                metrics_base=list(metrics),
                coverage=coverage,
                kpis=list(kpis),
                red_flags=list(red_flags)
            )

            return result.to_dict()

        except Exception as e:
            return None

    def _update_progress(self):
        """Update and report progress."""
        if self._stats.processed > 0 and self._stats.elapsed_seconds > 0:
            self._stats.files_per_second = self._stats.processed / self._stats.elapsed_seconds

            remaining = len(self._stats.current_file) - self._stats.processed
            if self._stats.files_per_second > 0:
                self._stats.estimated_remaining_seconds = remaining / self._stats.files_per_second

        if self.progress_callback:
            self.progress_callback(self._stats)


def aggregate_batch_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate results from batch processing.

    Args:
        results: List of analysis results.

    Returns:
        Aggregated statistics and summaries.
    """
    if not results:
        return {}

    # Use GPU if available for aggregation
    if GPU_AVAILABLE:
        return _aggregate_gpu(results)
    else:
        return _aggregate_cpu(results)


def _aggregate_gpu(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """GPU-accelerated aggregation using cuDF."""
    # Extract metrics into rows
    rows = []
    for r in results:
        row = {"filename": r["metadata"]["filename"]}
        for m in r.get("metrics_base", []):
            if m["value"] is not None:
                row[m["key"]] = m["value"]
        for k in r.get("kpis", []):
            if k["value"] is not None:
                row[f"kpi_{k['key']}"] = k["value"]
        rows.append(row)

    # Create GPU DataFrame
    gdf = cudf.DataFrame(rows)

    # Calculate statistics on GPU
    stats = {}
    numeric_cols = gdf.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns

    for col in numeric_cols:
        stats[col] = {
            "count": int(gdf[col].count()),
            "mean": float(gdf[col].mean()),
            "std": float(gdf[col].std()),
            "min": float(gdf[col].min()),
            "max": float(gdf[col].max()),
            "median": float(gdf[col].median()),
            "q25": float(gdf[col].quantile(0.25)),
            "q75": float(gdf[col].quantile(0.75))
        }

    # Count red flags
    red_flag_counts = {}
    for r in results:
        for rf in r.get("red_flags", []):
            if rf.get("detected"):
                key = rf["key"]
                red_flag_counts[key] = red_flag_counts.get(key, 0) + 1

    return {
        "total_companies": len(results),
        "metric_statistics": stats,
        "red_flag_summary": red_flag_counts,
        "gpu_accelerated": True
    }


def _aggregate_cpu(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """CPU-based aggregation using pandas."""
    import pandas as pd

    # Extract metrics into rows
    rows = []
    for r in results:
        row = {"filename": r["metadata"]["filename"]}
        for m in r.get("metrics_base", []):
            if m["value"] is not None:
                row[m["key"]] = m["value"]
        for k in r.get("kpis", []):
            if k["value"] is not None:
                row[f"kpi_{k['key']}"] = k["value"]
        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Calculate statistics
    stats = {}
    numeric_cols = df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns

    for col in numeric_cols:
        stats[col] = {
            "count": int(df[col].count()),
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "median": float(df[col].median()),
            "q25": float(df[col].quantile(0.25)),
            "q75": float(df[col].quantile(0.75))
        }

    # Count red flags
    red_flag_counts = {}
    for r in results:
        for rf in r.get("red_flags", []):
            if rf.get("detected"):
                key = rf["key"]
                red_flag_counts[key] = red_flag_counts.get(key, 0) + 1

    return {
        "total_companies": len(results),
        "metric_statistics": stats,
        "red_flag_summary": red_flag_counts,
        "gpu_accelerated": False
    }


def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information and availability status.

    Returns:
        Dictionary with GPU information.
    """
    info = {
        "gpu_available": GPU_AVAILABLE,
        "rapids_installed": GPU_AVAILABLE
    }

    if GPU_AVAILABLE:
        try:
            import cupy as cp
            device = cp.cuda.Device()
            info["device_name"] = device.name
            info["compute_capability"] = device.compute_capability

            mem_info = device.mem_info
            info["memory_total_gb"] = mem_info[1] / (1024**3)
            info["memory_free_gb"] = mem_info[0] / (1024**3)
            info["memory_used_gb"] = (mem_info[1] - mem_info[0]) / (1024**3)
        except Exception as e:
            info["error"] = str(e)

    return info
