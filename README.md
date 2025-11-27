# HealthSim Core

Shared foundation library for the HealthSim product family. This library provides generic infrastructure for building simulation and synthetic data generation products.

> **Note**: This is an infrastructure library. For end-user products, see:
> - [PatientSim](https://github.com/mark64oswald/PatientSim) — Healthcare patient simulation
> - MemberSim (coming soon) — Health plan member simulation
> - RxMemberSim (coming soon) — Pharmacy member simulation

## What's Included

HealthSim Core provides domain-agnostic building blocks:

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
pip install healthsim-core[dev]
```

## Quick Start

### Generate a Person

```python
from healthsim.generation import PersonGenerator

generator = PersonGenerator(seed=42)
person = generator.generate_person(age_range=(25, 65))

print(f"{person.name.full_name}, Age {person.age}")
# Output: John Smith, Age 42
```

### Validate Data

```python
from healthsim.validation import ValidationResult, ValidationSeverity

result = ValidationResult()
if some_date > today:
    result.add_issue(
        code="DATE_001",
        message="Date cannot be in the future",
        severity=ValidationSeverity.ERROR,
        field_path="birth_date"
    )

if result.valid:
    print("Data is valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
```

### Load Skills

```python
from healthsim.skills import SkillLoader

loader = SkillLoader()
skill = loader.load_file("skills/my-skill.md")

print(f"Skill: {skill.name}")
print(f"Parameters: {[p.name for p in skill.parameters]}")
```

## Building Products on HealthSim Core

To build a new product using this library:

1. **Install as dependency**:
   ```toml
   # pyproject.toml
   dependencies = ["healthsim-core>=0.1.0"]
   ```

2. **Extend the Person model**:
   ```python
   from healthsim.person import Person

   class Patient(Person):
       """Patient extends Person with healthcare-specific fields."""
       mrn: str  # Medical Record Number
       # ... clinical fields
   ```

3. **Extend the Generator**:
   ```python
   from healthsim.generation import BaseGenerator

   class PatientGenerator(BaseGenerator):
       """Generate patients with clinical data."""

       def generate_patient(self, **kwargs) -> Patient:
           # Use base generator utilities
           person = self._generate_person(**kwargs)
           mrn = self._generate_identifier("MRN")
           return Patient(**person.model_dump(), mrn=mrn)
   ```

4. **Use the validation framework**:
   ```python
   from healthsim.validation import BaseValidator, ValidationResult

   class ClinicalValidator(BaseValidator):
       """Domain-specific validation rules."""

       def validate(self, data) -> ValidationResult:
           result = ValidationResult()
           # Add domain-specific checks
           return result
   ```

## API Reference

### healthsim.person

- `Gender` — Enum (MALE, FEMALE, OTHER, UNKNOWN)
- `PersonName` — Name components with `full_name` property
- `Address` — Physical address
- `ContactInfo` — Phone, email
- `Person` — Base person model with demographics

### healthsim.temporal

- `TimePeriod` — Start/end datetime with duration
- `TimelineEvent` — Single event with timestamp
- `Timeline` — Ordered sequence of events
- `calculate_age()` — Age from birth date
- `format_datetime_iso()` — ISO 8601 formatting

### healthsim.generation

- `BaseGenerator` — Abstract base with seed management
- `PersonGenerator` — Generate Person instances
- `weighted_choice()` — Select from weighted options
- `random_date_in_range()` — Random date generation

### healthsim.validation

- `ValidationSeverity` — ERROR, WARNING, INFO
- `ValidationIssue` — Single validation issue
- `ValidationResult` — Collection of issues
- `BaseValidator` — Abstract validator base class
- `TemporalValidator` — Date/time validation

### healthsim.formats

- `BaseTransformer` — Abstract format transformer
- `JSONExporter` — Export to JSON
- `CSVExporter` — Export to CSV

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

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

## License

MIT License — see [LICENSE](LICENSE) for details.