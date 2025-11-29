# healthsim-core

**Shared foundation library for the HealthSim synthetic healthcare data platform.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](CHANGELOG.md)

---

## Overview

healthsim-core provides **domain-agnostic infrastructure** for synthetic healthcare data generation. It serves as the foundation for:

- **[PatientSim](https://github.com/mark64oswald/PatientSim)** — Clinical/EMR synthetic data
- **[MemberSim](https://github.com/mark64oswald/MemberSim)** — Payer/claims synthetic data

This library contains **no clinical or payer-specific concepts** — only generic patterns that both products extend.

## What's Included

| Module | Description |
|--------|-------------|
| `healthsim.person` | Person demographics, identifiers, relationships |
| `healthsim.temporal` | Timeline management, periods, date utilities |
| `healthsim.generation` | Base generator, distributions, reproducibility |
| `healthsim.validation` | Validation framework, results, base validators |
| `healthsim.formats` | Base transformer, JSON/CSV utilities |
| `healthsim.skills` | Skill schema, loader, composer |
| `healthsim.config` | Settings management, logging |

## Installation

```bash
pip install healthsim-core
```

For development:

```bash
git clone https://github.com/mark64oswald/healthsim-core.git
cd healthsim-core
pip install -e ".[dev]"
```

## Modules

### `healthsim.person`

Core person demographics model.

```python
from datetime import date
from healthsim.person import Person, PersonName, Address, Gender, ContactInfo

person = Person(
    id="person-001",
    name=PersonName(given_name="Jane", family_name="Smith"),
    birth_date=date(1985, 6, 15),
    gender=Gender.FEMALE,
    address=Address(
        street="123 Main St",
        city="Boston",
        state="MA",
        zip_code="02101"
    ),
    contact=ContactInfo(
        phone="617-555-1234",
        email="jane.smith@example.com"
    )
)

print(f"{person.name.full_name}, Age {person.age}")
```

### `healthsim.temporal`

Timeline and date management.

```python
from datetime import date
from healthsim.temporal import (
    Timeline, Period, PeriodCollection,
    EventStatus, EventDelay,
    calculate_age, relative_date, business_days_between
)

# Create a timeline with events
timeline = Timeline(name="Treatment Plan", start_date=date(2024, 1, 1))
timeline.create_event("intake", name="Initial Intake")
timeline.create_event(
    "assessment",
    name="Assessment",
    delay=EventDelay(min_days=7, max_days=14)
)
timeline.schedule_events()

# Get pending events
pending = timeline.get_pending_events()

# Period management
coverage = Period(start_date=date(2024, 1, 1), end_date=date(2024, 12, 31))
print(f"Coverage duration: {coverage.duration_days} days")

# Date utilities
age = calculate_age(date(1985, 6, 15))
next_week = relative_date(date.today(), days=7)
workdays = business_days_between(date(2024, 1, 1), date(2024, 1, 31))
```

### `healthsim.generation`

Reproducible data generation with distributions and cohorts.

```python
from healthsim.generation import (
    SeedManager, WeightedChoice,
    CohortGenerator, CohortConstraints, CohortProgress,
    AgeDistribution, NormalDistribution, UniformDistribution
)

# Reproducible random with SeedManager
seed_manager = SeedManager(seed=42)
child_seed = seed_manager.get_child_seed()
random_val = seed_manager.get_random_int(1, 100)

# Weighted selection
gender = WeightedChoice(options=[("M", 0.48), ("F", 0.52)])
selected = gender.select(rng=seed_manager.rng)

# Age distribution with presets
ages = AgeDistribution.adult()  # 18-65 distribution
sampled_age = ages.sample(rng=seed_manager.rng)

# Normal and uniform distributions
height = NormalDistribution(mean=170, std_dev=10)
weight = UniformDistribution(min_value=60, max_value=100)
```

### `healthsim.validation`

Validation framework for generated data.

```python
from healthsim.validation import (
    BaseValidator, ValidationResult, ValidationSeverity,
    CompositeValidator, StructuralValidator
)

# Create a custom validator
class MyValidator(BaseValidator):
    def validate(self, data) -> ValidationResult:
        result = ValidationResult()
        if not data.get("required_field"):
            result.add_issue(
                code="MISSING_001",
                message="Required field is missing",
                severity=ValidationSeverity.ERROR,
                field_path="required_field"
            )
        return result

# Combine validators
validator = CompositeValidator()
validator.add(MyValidator())
validator.add(StructuralValidator(required_fields=["id", "name"]))

result = validator.validate(entity)
if not result.valid:
    for error in result.errors:
        print(f"[{error.code}] {error.message}")
```

### `healthsim.formats`

Base transformer classes for output formats.

```python
from healthsim.formats import (
    Transformer, JsonTransformer, CsvTransformer,
    format_date, format_datetime, safe_str, truncate
)

class MyJsonTransformer(JsonTransformer):
    def transform(self, entity):
        return {
            "id": entity.id,
            "name": safe_str(entity.name),
            "created": format_date(entity.created_at),
            "description": truncate(entity.description, max_length=100)
        }

# Use the transformer
transformer = MyJsonTransformer()
json_output = transformer.transform(my_entity)
```

### `healthsim.skills`

Skill file loading for Claude integration.

```python
from healthsim.skills import SkillLoader, SkillComposer

# Load skills from directory
loader = SkillLoader("./skills")
skills = loader.load_all()

# Load single skill
skill = loader.load_file("skills/my-skill.md")
print(f"Skill: {skill.name}")
print(f"Parameters: {[p.name for p in skill.parameters]}")

# Compose for Claude
composer = SkillComposer(skills)
context = composer.compose_with_headers()
```

## Building Products on HealthSim Core

When building a new product using this library:

### 1. Extend Person for your entity model

```python
from healthsim.person import Person
from pydantic import Field

class Patient(Person):
    """Clinical patient model."""
    mrn: str = Field(..., description="Medical Record Number")
    diagnoses: list[str] = Field(default_factory=list)

class Member(Person):
    """Health plan member model."""
    member_id: str = Field(..., description="Member ID")
    plan_code: str = Field(..., description="Plan identifier")
```

### 2. Extend CohortGenerator for batch generation

```python
from healthsim.generation import CohortGenerator, CohortConstraints

class MemberCohortGenerator(CohortGenerator["Member"]):
    def generate_one(self, index: int, constraints: CohortConstraints) -> Member:
        # Use self.seed_manager for reproducibility
        member_seed = self.seed_manager.get_child_seed()
        # Generate member...
        return member
```

### 3. Extend BaseValidator for domain validation

```python
from healthsim.validation import BaseValidator, ValidationResult

class MemberValidator(BaseValidator):
    def validate(self, member) -> ValidationResult:
        result = ValidationResult()
        # Add validation logic...
        return result
```

### 4. Use Timeline for event sequencing

```python
from healthsim.temporal import Timeline, EventDelay

timeline = Timeline(name="Enrollment", start_date=start_date)
timeline.create_event("enroll", name="New Enrollment")
timeline.create_event(
    "id_card",
    name="ID Card Mailed",
    delay=EventDelay(min_days=3, max_days=5)
)
timeline.schedule_events()
```

## API Reference

### healthsim.person

- `Gender` — Enum (MALE, FEMALE, OTHER, UNKNOWN)
- `PersonName` — Name components with `full_name` property
- `Address` — Physical address
- `ContactInfo` — Phone, email
- `Identifier` — Generic identifier with type
- `Person` — Base person model with demographics

### healthsim.temporal

- `TimePeriod` — Start/end datetime with duration
- `Period` — Date range with gap/overlap detection
- `PeriodCollection` — Collection of periods with consolidation
- `TimelineEvent` — Event with status, delay, and dependencies
- `Timeline` — Ordered sequence of events with scheduling
- `EventStatus` — PENDING, EXECUTED, SKIPPED, FAILED
- `EventDelay` — Configurable delay between events
- `calculate_age()` — Age from birth date
- `relative_date()` — Calculate date offsets
- `business_days_between()` — Count business days
- `next_business_day()` — Find next Mon-Fri
- `is_future_date()` — Check if date is in future

### healthsim.generation

- `SeedManager` — Seed management with child seeds and RNG
- `BaseGenerator` — Abstract base with seed management
- `PersonGenerator` — Generate Person instances
- `CohortGenerator` — Generate groups of entities (generic)
- `CohortConstraints` — Configure cohort generation
- `CohortProgress` — Track generation progress
- `AgeDistribution` — Weighted age band sampling with presets
- `WeightedChoice` — Select from weighted options
- `NormalDistribution` — Normal distribution sampling
- `UniformDistribution` — Uniform distribution sampling

### healthsim.validation

- `ValidationSeverity` — ERROR, WARNING, INFO
- `ValidationIssue` — Single validation issue
- `ValidationResult` — Collection of issues with `valid` property
- `BaseValidator` — Abstract validator base class
- `CompositeValidator` — Combine multiple validators
- `StructuralValidator` — Required field validation
- `TemporalValidator` — Date/time validation

### healthsim.formats

- `Transformer` — Generic abstract transformer
- `JsonTransformer` — JSON output base class
- `CsvTransformer` — CSV output base class
- `BaseTransformer` — Legacy transformer base
- `JSONExporter` — Export to JSON
- `CSVExporter` — Export to CSV
- `format_date()` — Format date to string
- `format_datetime()` — Format datetime to string
- `safe_str()` — Safe string conversion
- `truncate()` — Truncate text with suffix

### healthsim.skills

- `Skill` — Complete skill definition
- `SkillType` — Type enumeration
- `SkillParameter` — Configurable parameter
- `SkillLoader` — Load from markdown files
- `SkillComposer` — Compose multiple skills

### healthsim.config

- `HealthSimSettings` — Base settings class
- `setup_logging()` — Configure logging

## Development

```bash
# Clone the repository
git clone https://github.com/mark64oswald/healthsim-core.git
cd healthsim-core

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Code quality
black src/ tests/
ruff check src/ tests/ --fix
mypy src/
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Related Projects

- **[PatientSim](https://github.com/mark64oswald/PatientSim)** — Clinical/EMR synthetic data generation
- **[MemberSim](https://github.com/mark64oswald/MemberSim)** — Payer/claims synthetic data generation
