"""
RINGTRACE AI - Phase 7: Graph Neural Network (GNN) Engine.
Advanced relational fraud detection across Bank A, Bank B, Bank C, and Bank D.
"""

__all__ = [
    "GNNFeatureEngineer",
    "GNNDatasetBuilder",
    "EdgeAwareGNN",
    "GATv2Net",
    "GNNTrainer",
    "GNNInferenceService",
    "GNNSubGraphExplainer",
]


def __getattr__(name: str):
    """Lazy module attribute loading to prevent eager PyTorch memory allocation at startup."""
    if name == "GNNFeatureEngineer":
        from src.gnn.features import GNNFeatureEngineer
        return GNNFeatureEngineer
    if name == "GNNDatasetBuilder":
        from src.gnn.dataset import GNNDatasetBuilder
        return GNNDatasetBuilder
    if name in ("EdgeAwareGNN", "GATv2Net"):
        from src.gnn.models import EdgeAwareGNN, GATv2Net
        return EdgeAwareGNN if name == "EdgeAwareGNN" else GATv2Net
    if name == "GNNTrainer":
        from src.gnn.trainer import GNNTrainer
        return GNNTrainer
    if name == "GNNInferenceService":
        from src.gnn.inference import GNNInferenceService
        return GNNInferenceService
    if name == "GNNSubGraphExplainer":
        from src.gnn.explainer import GNNSubGraphExplainer
        return GNNSubGraphExplainer
    raise AttributeError(f"module 'src.gnn' has no attribute '{name}'")
