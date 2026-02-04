# config/timeouts.py
"""Configuration des timeouts et délais."""

from dataclasses import dataclass

@dataclass
class TimeoutConfig:
    """Configuration des timeouts pour les tests OpenBravo."""
    
    # Délais d'attente (secondes)
    VERY_SHORT_WAIT: float = 0.2
    SHORT_WAIT: float = 0.5
    MEDIUM_WAIT: float = 2.0
    LONG_WAIT: float = 5.0
    ELEMENT_VISIBLE: float = 15.0
    
    # Tentatives de retry
    MAX_ALERT_ATTEMPTS: int = 30
    ALERT_CHECK_INTERVAL: float = 0.1
    
    # Délais de fermeture
    ESC_KEY_DELAY: float = 0.1
    ESC_KEY_REPEATS: int = 6

    DEFAULT_WAIT: int = 1

# Singleton
DEFAULT_TIMEOUTS = TimeoutConfig()