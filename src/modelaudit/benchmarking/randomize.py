"""
Randomization models and logic for benchmark tests.
"""

import random
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TestCategory(str, Enum):
    """
    Categories for test cases to support leakage controls.
    """

    PUBLIC = "public"
    PRIVATE = "private"
    GENERATED = "generated"


class BenchmarkTest(BaseModel):
    """
    Represents a single test case within a benchmark.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="A unique identifier for the test case.")
    category: TestCategory = Field(
        ..., description="The visibility/leakage category of the test."
    )
    prompt: str = Field(..., description="The prompt to send to the model.")
    expected_output: Optional[str] = Field(
        None, description="The expected output or criteria for success."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context or metadata for the test."
    )


class RandomizedGenerator:
    """
    Generates equivalent randomized tests from a deterministic seed
    to prevent trivial special-casing by models.
    """

    def __init__(self, seed: int):
        self._seed = seed
        self._rng = random.Random(self._seed)

    def generate(self, base_test: BenchmarkTest) -> BenchmarkTest:
        """
        Generates a randomized but equivalent version of the provided base test.
        """
        # A simple randomized variation by appending a random, non-functional token
        # or instruction to avoid trivial exact string matching by models.
        random_suffix = f" (Variant ID: {self._rng.randint(1000, 9999)})"

        randomized_prompt = f"{base_test.prompt}{random_suffix}"

        return BenchmarkTest(
            id=f"{base_test.id}-rand",
            category=base_test.category,
            prompt=randomized_prompt,
            expected_output=base_test.expected_output,
            metadata={**base_test.metadata, "randomized": True, "seed": self._seed},
        )

    def shuffle_options(self, options: List[str]) -> List[str]:
        """
        Deterministically shuffles a list of options based on the seed.
        """
        options_copy = list(options)
        self._rng.shuffle(options_copy)
        return options_copy
