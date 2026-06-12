import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Settings:
    """Application configuration and evaluation thresholds."""
    APP_NAME: str = "FeedPulse AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # API Keys (Optional - runs in high-fidelity deterministic mode if omitted)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    # Retrieval Tuning
    DEFAULT_HYBRID_ALPHA: float = 0.55  # Weight of dense vs sparse (0 = 100% BM25, 1 = 100% Dense)
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RERANK_TOP_K: int = 15

    # Evaluation Quality Gates (Enterpret Rigor)
    MIN_FAITHFULNESS: float = 0.85
    MIN_CONTEXT_RECALL: float = 0.80
    MIN_CONTEXT_PRECISION: float = 0.75
    MAX_HALLUCINATION_RATE: float = 0.10

settings = Settings()
