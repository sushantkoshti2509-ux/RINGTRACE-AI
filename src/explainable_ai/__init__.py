"""
Explainable AI (XAI) package for Feature 2 of RINGTRACE AI.
Provides lazy-loaded exports to prevent heavy SHAP and Matplotlib memory overhead at startup.
"""

def __getattr__(name: str):
    if name == "ModelSHAPExplainer":
        from src.explainable_ai.shap_explainer import ModelSHAPExplainer
        return ModelSHAPExplainer
    elif name == "HumanExplanationGenerator":
        from src.explainable_ai.reason_generator import HumanExplanationGenerator
        return HumanExplanationGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["ModelSHAPExplainer", "HumanExplanationGenerator"]

