from click.testing import CliRunner
from ai_api_model_auditor.cli import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "scan" in result.output
    assert "quick" in result.output
    assert "audit" in result.output

def test_cli_doctor_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--provider", "openai"])
    assert result.exit_code == 0
    assert "[DRY RUN]" in result.output

def test_cli_quick_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["quick", "--provider", "openai", "--model", "dummy"])
    assert result.exit_code == 0
    assert "Evidence saved" in result.output

def test_cli_scan_models_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "models", "--provider", "openai"])
    assert result.exit_code == 0
    assert "[DRY RUN] Would probe openai endpoint" in result.output

def test_cli_scan_probe_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "probe", "--provider", "openai", "--model", "dummy"])
    assert result.exit_code == 0
    assert "[DRY RUN] Simulating audit probe" in result.output

def test_cli_audit_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["audit", "--provider", "anthropic", "--model", "claude-3"])
    assert result.exit_code == 0
    assert "[DRY RUN] Simulating audit probe" in result.output
    assert "Evidence saved to evidence/audit_anthropic_claude-3" in result.output
