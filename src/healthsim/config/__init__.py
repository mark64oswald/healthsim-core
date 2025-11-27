"""Configuration and logging utilities.

This module provides settings management and logging configuration
for HealthSim applications.
"""

from healthsim.config.logging import setup_logging
from healthsim.config.settings import HealthSimSettings

__all__ = [
    "HealthSimSettings",
    "setup_logging",
]
