from modelaudit.benchmarking.randomize import (
    BenchmarkTest,
    RandomizedGenerator,
    TestCategory,
)


def test_test_category_enum():
    """Test the TestCategory Enum."""
    assert TestCategory.PUBLIC.value == "public"
    assert TestCategory.PRIVATE.value == "private"
    assert TestCategory.GENERATED.value == "generated"


def test_benchmark_test_model():
    """Test the BenchmarkTest Pydantic model initialization."""
    test_case = BenchmarkTest(
        id="test-1",
        category=TestCategory.PUBLIC,
        prompt="What is 2+2?",
        expected_output="4",
    )
    assert test_case.id == "test-1"
    assert test_case.category == TestCategory.PUBLIC
    assert test_case.prompt == "What is 2+2?"
    assert test_case.expected_output == "4"
    assert test_case.metadata == {}


def test_randomized_generator_deterministic():
    """Test that RandomizedGenerator produces identical output for identical seeds."""
    base_test = BenchmarkTest(
        id="test-1",
        category=TestCategory.PRIVATE,
        prompt="Write a poem about AI.",
        metadata={"source": "user"},
    )

    seed = 42
    gen1 = RandomizedGenerator(seed)
    gen2 = RandomizedGenerator(seed)

    rand_test1 = gen1.generate(base_test)
    rand_test2 = gen2.generate(base_test)

    assert rand_test1.id == "test-1-rand"
    assert rand_test1.category == TestCategory.PRIVATE
    assert rand_test1.prompt == rand_test2.prompt
    assert rand_test1.prompt != base_test.prompt  # Should be different from base
    assert rand_test1.metadata["randomized"] is True
    assert rand_test1.metadata["seed"] == seed
    assert rand_test1.metadata["source"] == "user"


def test_randomized_generator_shuffle():
    """Test deterministic shuffling of options."""
    options = ["A", "B", "C", "D"]
    seed = 123

    gen1 = RandomizedGenerator(seed)
    gen2 = RandomizedGenerator(seed)

    shuffled1 = gen1.shuffle_options(options)
    shuffled2 = gen2.shuffle_options(options)

    assert shuffled1 == shuffled2
    assert sorted(shuffled1) == sorted(options)
