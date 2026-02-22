"""Anomaly Detection for Financial Statements using Autoencoders.

This module provides GPU-accelerated anomaly detection for financial data using:
- Autoencoder neural networks (PyTorch)
- Isolation Forest (sklearn/cuML)
- Statistical methods (Z-score, IQR)

Optimized for NVIDIA DGX Spark with Grace Blackwell architecture.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Check for GPU acceleration
GPU_AVAILABLE = False
try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
    DEVICE = torch.device("cuda" if GPU_AVAILABLE else "cpu")
except ImportError:
    torch = None
    DEVICE = None

# Try to import cuML for GPU-accelerated Isolation Forest
CUML_AVAILABLE = False
try:
    from cuml.ensemble import RandomForestClassifier as cuRF
    from cuml.cluster import DBSCAN as cuDBSCAN
    CUML_AVAILABLE = True
except ImportError:
    pass


@dataclass
class AnomalyResult:
    """Result of anomaly detection for a single company."""
    filename: str
    anomaly_score: float
    is_anomaly: bool
    anomaly_type: str
    contributing_factors: List[str]
    reconstruction_error: Optional[float] = None
    z_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class AnomalyReport:
    """Complete anomaly detection report."""
    total_companies: int
    anomalies_detected: int
    anomaly_rate: float
    method_used: str
    gpu_accelerated: bool
    execution_time_ms: float
    results: List[AnomalyResult] = field(default_factory=list)
    feature_importance: Dict[str, float] = field(default_factory=dict)


class SimpleAutoencoder(torch.nn.Module if torch else object):
    """Simple autoencoder for financial anomaly detection.

    Architecture:
    - Encoder: input -> 32 -> 16 -> 8 (latent)
    - Decoder: 8 -> 16 -> 32 -> output

    Lower reconstruction error = normal
    Higher reconstruction error = potential anomaly
    """

    def __init__(self, input_dim: int, latent_dim: int = 8):
        """Initialize autoencoder.

        Args:
            input_dim: Number of input features.
            latent_dim: Size of latent representation.
        """
        if torch is None:
            raise ImportError("PyTorch not installed")

        super().__init__()

        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 32),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(32, 16),
            torch.nn.ReLU(),
            torch.nn.Linear(16, latent_dim)
        )

        self.decoder = torch.nn.Sequential(
            torch.nn.Linear(latent_dim, 16),
            torch.nn.ReLU(),
            torch.nn.Linear(16, 32),
            torch.nn.ReLU(),
            torch.nn.Linear(32, input_dim)
        )

    def forward(self, x):
        """Forward pass through autoencoder."""
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def encode(self, x):
        """Get latent representation."""
        return self.encoder(x)


class AnomalyDetector:
    """Multi-method anomaly detector for financial data.

    Supports three detection methods:
    1. Autoencoder (neural network) - best for complex patterns
    2. Isolation Forest - best for traditional outlier detection
    3. Statistical (Z-score/IQR) - best for simple thresholding

    Example:
        >>> detector = AnomalyDetector(method="autoencoder")
        >>> detector.fit(training_data)
        >>> report = detector.detect(new_data)
        >>> print(f"Found {report.anomalies_detected} anomalies")
    """

    # Key financial metrics for anomaly detection
    DEFAULT_FEATURES = [
        "kpi_roe", "kpi_roa", "kpi_debt_ratio", "kpi_equity_ratio",
        "kpi_debt_to_equity", "kpi_net_profit_margin", "kpi_ebit_margin",
        "kpi_asset_turnover", "kpi_ocf_to_revenue", "kpi_quality_of_earnings"
    ]

    def __init__(
        self,
        method: str = "ensemble",
        threshold: float = 0.95,
        features: Optional[List[str]] = None,
        use_gpu: bool = True
    ):
        """Initialize anomaly detector.

        Args:
            method: Detection method - "autoencoder", "isolation_forest",
                    "statistical", or "ensemble" (combines all).
            threshold: Anomaly threshold (percentile for scores).
            features: List of feature columns to use.
            use_gpu: Whether to use GPU acceleration if available.
        """
        self.method = method
        self.threshold = threshold
        self.features = features or self.DEFAULT_FEATURES
        self.use_gpu = use_gpu and GPU_AVAILABLE

        # Models
        self._autoencoder: Optional[SimpleAutoencoder] = None
        self._scaler_mean: Optional[np.ndarray] = None
        self._scaler_std: Optional[np.ndarray] = None
        self._isolation_forest = None
        self._threshold_value: Optional[float] = None

        # Training stats
        self._is_fitted = False
        self._feature_stats: Dict[str, Dict[str, float]] = {}

    def fit(
        self,
        data: pd.DataFrame,
        epochs: int = 100,
        batch_size: int = 32,
        learning_rate: float = 0.001
    ) -> "AnomalyDetector":
        """Fit the anomaly detector on training data.

        Args:
            data: Training DataFrame with financial metrics.
            epochs: Number of training epochs (for autoencoder).
            batch_size: Batch size for training.
            learning_rate: Learning rate for autoencoder.

        Returns:
            Self for method chaining.
        """
        # Extract and preprocess features
        X = self._prepare_features(data)

        if X.shape[0] < 5:
            raise ValueError("Need at least 5 samples for training")

        # Fit scaler
        self._scaler_mean = np.nanmean(X, axis=0)
        self._scaler_std = np.nanstd(X, axis=0)
        self._scaler_std[self._scaler_std == 0] = 1  # Avoid division by zero

        # Scale data
        X_scaled = (X - self._scaler_mean) / self._scaler_std

        # Replace NaN with 0 after scaling
        X_scaled = np.nan_to_num(X_scaled, nan=0.0)

        # Calculate feature statistics for later analysis
        self._calculate_feature_stats(data)

        # Fit models based on method
        if self.method in ["autoencoder", "ensemble"]:
            self._fit_autoencoder(X_scaled, epochs, batch_size, learning_rate)

        if self.method in ["isolation_forest", "ensemble"]:
            self._fit_isolation_forest(X_scaled)

        # Calculate threshold from training data
        if self.method == "autoencoder":
            scores = self._score_autoencoder(X_scaled)
        elif self.method == "isolation_forest":
            scores = self._score_isolation_forest(X_scaled)
        elif self.method == "statistical":
            scores = self._score_statistical(X_scaled)
        else:  # ensemble
            scores = self._score_ensemble(X_scaled)

        self._threshold_value = np.percentile(scores, self.threshold * 100)

        self._is_fitted = True
        return self

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extract and prepare feature matrix from DataFrame."""
        available_features = [f for f in self.features if f in data.columns]

        if not available_features:
            raise ValueError(f"No features found. Available: {data.columns.tolist()}")

        self.features = available_features
        return data[available_features].values.astype(np.float32)

    def _calculate_feature_stats(self, data: pd.DataFrame) -> None:
        """Calculate statistics for each feature."""
        for feature in self.features:
            if feature in data.columns:
                values = data[feature].dropna()
                self._feature_stats[feature] = {
                    "mean": float(values.mean()),
                    "std": float(values.std()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "q25": float(values.quantile(0.25)),
                    "q75": float(values.quantile(0.75))
                }

    def _fit_autoencoder(
        self,
        X: np.ndarray,
        epochs: int,
        batch_size: int,
        learning_rate: float
    ) -> None:
        """Train autoencoder model."""
        if torch is None:
            return

        input_dim = X.shape[1]
        self._autoencoder = SimpleAutoencoder(input_dim)

        if self.use_gpu:
            self._autoencoder = self._autoencoder.to(DEVICE)

        optimizer = torch.optim.Adam(
            self._autoencoder.parameters(),
            lr=learning_rate
        )
        criterion = torch.nn.MSELoss()

        # Convert to tensor
        X_tensor = torch.FloatTensor(X)
        if self.use_gpu:
            X_tensor = X_tensor.to(DEVICE)

        # Training loop
        self._autoencoder.train()
        for epoch in range(epochs):
            # Shuffle data
            indices = torch.randperm(X_tensor.size(0))
            X_shuffled = X_tensor[indices]

            total_loss = 0.0
            num_batches = 0

            for i in range(0, X_shuffled.size(0), batch_size):
                batch = X_shuffled[i:i+batch_size]

                optimizer.zero_grad()
                reconstructed = self._autoencoder(batch)
                loss = criterion(reconstructed, batch)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                num_batches += 1

        self._autoencoder.eval()

    def _fit_isolation_forest(self, X: np.ndarray) -> None:
        """Train Isolation Forest model."""
        from sklearn.ensemble import IsolationForest

        self._isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self._isolation_forest.fit(X)

    def _score_autoencoder(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores from autoencoder (reconstruction error)."""
        if self._autoencoder is None or torch is None:
            return np.zeros(X.shape[0])

        X_tensor = torch.FloatTensor(X)
        if self.use_gpu:
            X_tensor = X_tensor.to(DEVICE)

        with torch.no_grad():
            reconstructed = self._autoencoder(X_tensor)
            errors = torch.mean((X_tensor - reconstructed) ** 2, dim=1)

        return errors.cpu().numpy()

    def _score_isolation_forest(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores from Isolation Forest."""
        if self._isolation_forest is None:
            return np.zeros(X.shape[0])

        # Isolation Forest returns negative scores (lower = more anomalous)
        # We negate to get positive scores where higher = more anomalous
        return -self._isolation_forest.score_samples(X)

    def _score_statistical(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores using statistical methods (max Z-score)."""
        # Z-scores are already computed since data is scaled
        z_scores = np.abs(X)
        return np.max(z_scores, axis=1)  # Max Z-score across features

    def _score_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble anomaly scores (weighted average)."""
        scores = []
        weights = []

        # Autoencoder scores
        ae_scores = self._score_autoencoder(X)
        if np.any(ae_scores):
            scores.append(self._normalize_scores(ae_scores))
            weights.append(0.4)

        # Isolation Forest scores
        if_scores = self._score_isolation_forest(X)
        if np.any(if_scores):
            scores.append(self._normalize_scores(if_scores))
            weights.append(0.4)

        # Statistical scores
        stat_scores = self._score_statistical(X)
        scores.append(self._normalize_scores(stat_scores))
        weights.append(0.2)

        # Weighted average
        total_weight = sum(weights)
        ensemble_scores = np.zeros(X.shape[0])
        for score, weight in zip(scores, weights):
            ensemble_scores += score * (weight / total_weight)

        return ensemble_scores

    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to 0-1 range."""
        min_val = np.min(scores)
        max_val = np.max(scores)
        if max_val - min_val == 0:
            return np.zeros_like(scores)
        return (scores - min_val) / (max_val - min_val)

    def detect(
        self,
        data: pd.DataFrame,
        include_scores: bool = True
    ) -> AnomalyReport:
        """Detect anomalies in new data.

        Args:
            data: DataFrame with financial metrics.
            include_scores: Whether to include detailed scores.

        Returns:
            AnomalyReport with detection results.
        """
        import time
        start_time = time.time()

        if not self._is_fitted:
            # Auto-fit on provided data
            self.fit(data)

        # Prepare features
        X = self._prepare_features(data)
        X_scaled = (X - self._scaler_mean) / self._scaler_std
        X_scaled = np.nan_to_num(X_scaled, nan=0.0)

        # Get scores based on method
        if self.method == "autoencoder":
            scores = self._score_autoencoder(X_scaled)
        elif self.method == "isolation_forest":
            scores = self._score_isolation_forest(X_scaled)
        elif self.method == "statistical":
            scores = self._score_statistical(X_scaled)
        else:  # ensemble
            scores = self._score_ensemble(X_scaled)

        # Determine anomalies
        is_anomaly = scores > self._threshold_value

        # Build results
        results = []
        filenames = data.get("filename", pd.Series(range(len(data)))).tolist()

        for i, (filename, score, anomaly) in enumerate(zip(filenames, scores, is_anomaly)):
            # Calculate Z-scores for this sample
            z_scores = {}
            contributing_factors = []

            for j, feature in enumerate(self.features):
                z = abs(X_scaled[i, j])
                z_scores[feature] = float(z)
                if z > 2.0:  # More than 2 std deviations
                    contributing_factors.append(f"{feature} (z={z:.2f})")

            # Determine anomaly type
            if anomaly:
                if len(contributing_factors) > 3:
                    anomaly_type = "Multiple metric deviations"
                elif contributing_factors:
                    anomaly_type = f"Deviation in: {contributing_factors[0].split(' ')[0]}"
                else:
                    anomaly_type = "Pattern-based anomaly"
            else:
                anomaly_type = "Normal"

            result = AnomalyResult(
                filename=str(filename),
                anomaly_score=float(score),
                is_anomaly=bool(anomaly),
                anomaly_type=anomaly_type,
                contributing_factors=contributing_factors[:5],  # Top 5
                reconstruction_error=float(scores[i]) if self.method == "autoencoder" else None,
                z_scores=z_scores if include_scores else {}
            )
            results.append(result)

        # Calculate feature importance based on variance contribution
        feature_importance = {}
        for j, feature in enumerate(self.features):
            # Higher variance in anomalies vs normal = more important
            anomaly_vals = X_scaled[is_anomaly, j] if np.any(is_anomaly) else np.array([])
            normal_vals = X_scaled[~is_anomaly, j] if np.any(~is_anomaly) else np.array([])

            if len(anomaly_vals) > 0 and len(normal_vals) > 0:
                importance = abs(np.mean(anomaly_vals) - np.mean(normal_vals))
            else:
                importance = np.std(X_scaled[:, j])

            feature_importance[feature] = float(importance)

        elapsed_ms = (time.time() - start_time) * 1000

        return AnomalyReport(
            total_companies=len(data),
            anomalies_detected=int(np.sum(is_anomaly)),
            anomaly_rate=float(np.mean(is_anomaly)),
            method_used=self.method,
            gpu_accelerated=self.use_gpu and torch is not None,
            execution_time_ms=elapsed_ms,
            results=results,
            feature_importance=feature_importance
        )


def create_anomaly_detector(
    method: str = "ensemble",
    use_gpu: bool = True
) -> AnomalyDetector:
    """Factory function to create configured anomaly detector.

    Args:
        method: Detection method ("autoencoder", "isolation_forest",
                "statistical", "ensemble").
        use_gpu: Whether to use GPU acceleration.

    Returns:
        Configured AnomalyDetector instance.
    """
    return AnomalyDetector(method=method, use_gpu=use_gpu)


def load_data_for_detection(directory: Path) -> pd.DataFrame:
    """Load analysis data from directory for anomaly detection.

    Args:
        directory: Directory containing analysis JSON files.

    Returns:
        DataFrame with financial metrics.
    """
    directory = Path(directory)
    rows = []

    for json_file in directory.glob("analysis_*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            row = {"filename": data.get("metadata", {}).get("filename", json_file.name)}

            # Extract KPIs
            for kpi in data.get("kpis", []):
                if kpi.get("value") is not None:
                    row[f"kpi_{kpi['key']}"] = kpi["value"]

            # Extract base metrics
            for metric in data.get("metrics_base", []):
                if metric.get("value") is not None:
                    row[metric["key"]] = metric["value"]

            rows.append(row)
        except Exception:
            continue

    return pd.DataFrame(rows)


def get_gpu_status() -> Dict[str, Any]:
    """Get GPU status for anomaly detection.

    Returns:
        Dictionary with GPU availability information.
    """
    status = {
        "pytorch_installed": torch is not None,
        "cuda_available": GPU_AVAILABLE,
        "cuml_available": CUML_AVAILABLE
    }

    if torch is not None and GPU_AVAILABLE:
        status["device_name"] = torch.cuda.get_device_name(0)
        status["device_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)

    return status
