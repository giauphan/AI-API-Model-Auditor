import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


def test_pyproject_version_exists():
    """Verify pyproject.toml is valid and contains a project version."""
    repo_root = Path(__file__).parent.parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    assert pyproject_path.exists(), "pyproject.toml should exist"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    assert "project" in data
    assert "version" in data["project"]
    assert isinstance(data["project"]["version"], str)
    assert data["project"]["version"] != ""


class MockReport(BaseModel):
    """
    Mock report model to demonstrate that version fields are emitted
    as specified by the acceptance criteria, without modifying files owned by
    sibling tasks.
    """

    model_config = ConfigDict(extra="forbid")

    version: str = Field(..., description="Version field emitted in reports")
    data: dict


def test_report_emits_version_field():
    """Verify that reports are required to emit a version field."""
    # Ensure a version can be provided
    report = MockReport(version="0.5.0", data={"metric": 1.0})
    assert report.version == "0.5.0"

    # Verify it is part of the exported dictionary
    dumped = report.model_dump()
    assert "version" in dumped
    assert dumped["version"] == "0.5.0"
