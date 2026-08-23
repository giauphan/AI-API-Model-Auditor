import pytest
from pydantic import ValidationError

from src.modelaudit.baselines.registry import ModelBaseline, Registry


def test_registry_registration():
    registry = Registry()
    baseline = ModelBaseline(
        model_name="test-model",
        provider="openai",
        date="2026-08-21",
        test_pack_version="1.0.0",
        features={"system_prompt": True},
    )

    registry.register(baseline)

    retrieved = registry.get("test-model")
    assert retrieved is not None
    assert retrieved.model_name == "test-model"
    assert retrieved.provider == "openai"
    assert retrieved.date == "2026-08-21"
    assert retrieved.features["system_prompt"] is True


def test_registry_not_found():
    registry = Registry()
    assert registry.get("non-existent") is None


def test_registry_list():
    registry = Registry()
    baseline1 = ModelBaseline(
        model_name="model1",
        provider="openai",
        date="2026-08-21",
        test_pack_version="1.0",
    )
    baseline2 = ModelBaseline(
        model_name="model2",
        provider="anthropic",
        date="2026-08-21",
        test_pack_version="1.0",
    )

    registry.register(baseline1)
    registry.register(baseline2)

    models = registry.list_models()
    assert "model1" in models
    assert "model2" in models
    assert len(models) == 2


def test_baseline_validation_error_on_missing_fields():
    with pytest.raises(ValidationError):
        ModelBaseline(
            provider="openai",
            date="2026-08-21",
            test_pack_version="1.0",
            # Missing model_name
        )


def test_baseline_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        ModelBaseline(
            model_name="model",
            provider="openai",
            date="2026-08-21",
            test_pack_version="1.0",
            credentials="my-secret-key",  # Extra fields are forbidden by config
        )
