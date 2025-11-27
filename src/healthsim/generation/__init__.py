"""Data generation framework.

This module provides base classes and utilities for generating
synthetic data with reproducibility support.
"""

from healthsim.generation.base import BaseGenerator, PersonGenerator
from healthsim.generation.distributions import (
    NormalDistribution,
    UniformDistribution,
    WeightedChoice,
)
from healthsim.generation.reproducibility import SeedManager

__all__ = [
    # Generators
    "BaseGenerator",
    "PersonGenerator",
    # Distributions
    "WeightedChoice",
    "NormalDistribution",
    "UniformDistribution",
    # Reproducibility
    "SeedManager",
]
