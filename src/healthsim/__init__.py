"""HealthSim Core - Shared foundation for HealthSim product family.

This library provides generic infrastructure for building simulation
and synthetic data generation products.

Modules:
    person: Person demographics, identifiers, relationships
    temporal: Timeline management, periods, date utilities
    generation: Base generator, distributions, reproducibility
    validation: Validation framework, results, base validators
    formats: Base transformer, JSON/CSV utilities
    skills: Skill schema, loader, composer
    config: Settings management, logging
"""

__version__ = "0.1.0"

__all__ = [
    "__version__",
]
