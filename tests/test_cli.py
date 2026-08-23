from click.testing import CliRunner
from ai_api_model_auditor.cli import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "recon" in result.output
    assert "audit" in result.output

def test_cli_recon_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["--dry-run", "recon", "--provider", "openai"])
    assert result.exit_code == 0
    assert "[DRY RUN] Would probe openai endpoint" in result.output

def test_cli_audit_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["--dry-run", "audit", "--provider", "anthropic", "--model", "claude-3"])
    assert result.exit_code == 0
    assert "[DRY RUN] Simulating audit probe" in result.output
    assert "Evidence saved to evidence/audit_anthropic_claude-3" in result.output
