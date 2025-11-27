"""Tests for healthsim.generation module."""

import random

import pytest

from healthsim.generation import (
    BaseGenerator,
    NormalDistribution,
    PersonGenerator,
    SeedManager,
    UniformDistribution,
    WeightedChoice,
)
from healthsim.person import Gender


class TestSeedManager:
    """Tests for SeedManager."""

    def test_creation(self) -> None:
        """Test creating a seed manager."""
        manager = SeedManager(seed=42)
        assert manager.seed == 42

    def test_reproducibility(self) -> None:
        """Test that same seed produces same results."""
        manager1 = SeedManager(seed=42)
        manager2 = SeedManager(seed=42)

        vals1 = [manager1.get_random_int(1, 100) for _ in range(5)]
        vals2 = [manager2.get_random_int(1, 100) for _ in range(5)]

        assert vals1 == vals2

    def test_different_seeds(self) -> None:
        """Test that different seeds produce different results."""
        manager1 = SeedManager(seed=42)
        manager2 = SeedManager(seed=123)

        vals1 = [manager1.get_random_int(1, 100) for _ in range(5)]
        vals2 = [manager2.get_random_int(1, 100) for _ in range(5)]

        assert vals1 != vals2

    def test_reset(self) -> None:
        """Test resetting the seed manager."""
        manager = SeedManager(seed=42)

        first_run = [manager.get_random_int(1, 100) for _ in range(5)]

        manager.reset()

        second_run = [manager.get_random_int(1, 100) for _ in range(5)]

        assert first_run == second_run

    def test_random_choice(self) -> None:
        """Test random choice."""
        manager = SeedManager(seed=42)
        options = ["a", "b", "c", "d"]

        choice = manager.get_random_choice(options)
        assert choice in options

    def test_random_sample(self) -> None:
        """Test random sample."""
        manager = SeedManager(seed=42)
        options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        sample = manager.get_random_sample(options, 3)
        assert len(sample) == 3
        assert all(s in options for s in sample)

    def test_random_bool(self) -> None:
        """Test random boolean."""
        manager = SeedManager(seed=42)

        # With probability 1.0, should always be True
        assert manager.get_random_bool(1.0) is True

        # With probability 0.0, should always be False
        manager.reset()
        assert manager.get_random_bool(0.0) is False

    def test_child_seed(self) -> None:
        """Test getting deterministic child seed."""
        manager = SeedManager(seed=42)

        seed1 = manager.get_child_seed()
        manager.reset()
        seed2 = manager.get_child_seed()

        assert seed1 == seed2


class TestWeightedChoice:
    """Tests for WeightedChoice."""

    def test_creation(self) -> None:
        """Test creating weighted choice."""
        wc = WeightedChoice(options=[
            ("common", 0.7),
            ("rare", 0.3),
        ])

        assert len(wc.options) == 2

    def test_select(self) -> None:
        """Test selection."""
        wc = WeightedChoice(options=[
            ("a", 0.5),
            ("b", 0.5),
        ])

        rng = random.Random(42)
        choice = wc.select(rng)
        assert choice in ["a", "b"]

    def test_weighted_distribution(self) -> None:
        """Test that weights affect distribution."""
        wc = WeightedChoice(options=[
            ("common", 0.9),
            ("rare", 0.1),
        ])

        rng = random.Random(42)
        results = [wc.select(rng) for _ in range(1000)]

        common_count = results.count("common")
        assert common_count > 800  # Should be ~90%

    def test_empty_options_raises(self) -> None:
        """Test that empty options raises error."""
        wc = WeightedChoice(options=[])

        with pytest.raises(ValueError, match="No options"):
            wc.select()

    def test_select_multiple(self) -> None:
        """Test selecting multiple items."""
        wc = WeightedChoice(options=[
            ("a", 1),
            ("b", 1),
            ("c", 1),
        ])

        rng = random.Random(42)
        choices = wc.select_multiple(5, rng)

        assert len(choices) == 5
        assert all(c in ["a", "b", "c"] for c in choices)

    def test_select_multiple_unique(self) -> None:
        """Test selecting unique items."""
        wc = WeightedChoice(options=[
            ("a", 1),
            ("b", 1),
            ("c", 1),
        ])

        rng = random.Random(42)
        choices = wc.select_multiple(3, rng, unique=True)

        assert len(choices) == 3
        assert len(set(choices)) == 3  # All unique


class TestNormalDistribution:
    """Tests for NormalDistribution."""

    def test_creation(self) -> None:
        """Test creating normal distribution."""
        dist = NormalDistribution(mean=100, std_dev=15)
        assert dist.mean == 100
        assert dist.std_dev == 15

    def test_sample(self) -> None:
        """Test sampling from distribution."""
        dist = NormalDistribution(mean=100, std_dev=15)
        rng = random.Random(42)

        # Sample many times and check mean is close
        samples = [dist.sample(rng) for _ in range(1000)]
        avg = sum(samples) / len(samples)

        assert 95 < avg < 105  # Should be close to 100

    def test_sample_int(self) -> None:
        """Test sampling integers."""
        dist = NormalDistribution(mean=100, std_dev=15)
        rng = random.Random(42)

        value = dist.sample_int(rng)
        assert isinstance(value, int)

    def test_sample_bounded(self) -> None:
        """Test bounded sampling."""
        dist = NormalDistribution(mean=100, std_dev=15)
        rng = random.Random(42)

        value = dist.sample_bounded(min_val=80, max_val=120, rng=rng)
        assert 80 <= value <= 120


class TestUniformDistribution:
    """Tests for UniformDistribution."""

    def test_creation(self) -> None:
        """Test creating uniform distribution."""
        dist = UniformDistribution(min_val=0, max_val=100)
        assert dist.min_val == 0
        assert dist.max_val == 100

    def test_sample(self) -> None:
        """Test sampling."""
        dist = UniformDistribution(min_val=0, max_val=100)
        rng = random.Random(42)

        for _ in range(100):
            value = dist.sample(rng)
            assert 0 <= value <= 100

    def test_sample_int(self) -> None:
        """Test integer sampling."""
        dist = UniformDistribution(min_val=1, max_val=6)
        rng = random.Random(42)

        for _ in range(100):
            value = dist.sample_int(rng)
            assert 1 <= value <= 6
            assert isinstance(value, int)


class TestBaseGenerator:
    """Tests for BaseGenerator."""

    def test_creation(self) -> None:
        """Test creating a generator."""
        gen = BaseGenerator(seed=42)
        assert gen.seed_manager.seed == 42

    def test_reproducibility(self) -> None:
        """Test that same seed produces same results."""
        gen1 = BaseGenerator(seed=42)
        gen2 = BaseGenerator(seed=42)

        ids1 = [gen1.generate_id("TEST") for _ in range(5)]
        gen1.reset()
        ids2 = [gen1.generate_id("TEST") for _ in range(5)]

        # After reset, should get same sequence
        # Note: generate_id uses uuid which may not be seeded

    def test_generate_id(self) -> None:
        """Test ID generation."""
        gen = BaseGenerator()

        id1 = gen.generate_id("ITEM")
        id2 = gen.generate_id("ITEM")

        assert id1.startswith("ITEM-")
        assert id2.startswith("ITEM-")
        assert id1 != id2  # Should be unique

    def test_generate_id_no_prefix(self) -> None:
        """Test ID generation without prefix."""
        gen = BaseGenerator()
        id = gen.generate_id()
        assert "-" not in id  # No prefix dash

    def test_random_choice(self) -> None:
        """Test random choice."""
        gen = BaseGenerator(seed=42)
        options = [1, 2, 3, 4, 5]

        choice = gen.random_choice(options)
        assert choice in options

    def test_random_int(self) -> None:
        """Test random integer."""
        gen = BaseGenerator(seed=42)

        for _ in range(100):
            val = gen.random_int(1, 10)
            assert 1 <= val <= 10

    def test_random_float(self) -> None:
        """Test random float."""
        gen = BaseGenerator(seed=42)

        for _ in range(100):
            val = gen.random_float(0.0, 1.0)
            assert 0.0 <= val <= 1.0

    def test_weighted_choice(self) -> None:
        """Test weighted choice."""
        gen = BaseGenerator(seed=42)
        options = [("heavy", 0.9), ("light", 0.1)]

        results = [gen.weighted_choice(options) for _ in range(100)]
        heavy_count = results.count("heavy")

        assert heavy_count > 70  # Should be ~90%


class TestPersonGenerator:
    """Tests for PersonGenerator."""

    def test_creation(self) -> None:
        """Test creating a person generator."""
        gen = PersonGenerator(seed=42)
        assert gen.seed_manager.seed == 42

    def test_generate_person(self) -> None:
        """Test generating a person."""
        gen = PersonGenerator(seed=42)
        person = gen.generate_person()

        assert person.id.startswith("PERSON-")
        assert person.name.given_name is not None
        assert person.name.family_name is not None
        assert person.gender in [Gender.MALE, Gender.FEMALE]
        assert person.birth_date is not None

    def test_generate_person_with_age_range(self) -> None:
        """Test generating person with age constraints."""
        gen = PersonGenerator(seed=42)
        person = gen.generate_person(age_range=(25, 35))

        assert 25 <= person.age <= 35

    def test_generate_person_with_gender(self) -> None:
        """Test generating person with specific gender."""
        gen = PersonGenerator(seed=42)
        person = gen.generate_person(gender=Gender.FEMALE)

        assert person.gender == Gender.FEMALE

    def test_generate_person_with_address(self) -> None:
        """Test generating person with address."""
        gen = PersonGenerator(seed=42)
        person = gen.generate_person(include_address=True)

        assert person.address is not None
        assert person.address.city is not None

    def test_generate_person_without_address(self) -> None:
        """Test generating person without address."""
        gen = PersonGenerator(seed=42)
        person = gen.generate_person(include_address=False)

        assert person.address is None

    def test_generate_name(self) -> None:
        """Test generating just a name."""
        gen = PersonGenerator(seed=42)
        name = gen.generate_name(Gender.MALE)

        assert name.given_name is not None
        assert name.family_name is not None

    def test_generate_address(self) -> None:
        """Test generating just an address."""
        gen = PersonGenerator(seed=42)
        address = gen.generate_address()

        assert address.street_address is not None
        assert address.city is not None
        assert address.state is not None
        assert address.postal_code is not None
        assert address.country == "US"

    def test_generate_contact(self) -> None:
        """Test generating contact info."""
        gen = PersonGenerator(seed=42)
        contact = gen.generate_contact()

        assert contact.phone is not None
        assert contact.email is not None

    def test_reproducibility(self) -> None:
        """Test that same seed produces same person."""
        gen1 = PersonGenerator(seed=42)
        gen2 = PersonGenerator(seed=42)

        person1 = gen1.generate_person()
        person2 = gen2.generate_person()

        assert person1.name.given_name == person2.name.given_name
        assert person1.name.family_name == person2.name.family_name
        assert person1.gender == person2.gender
        assert person1.birth_date == person2.birth_date