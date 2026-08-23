import click
import os
from .config import AppConfig, set_config
from .safety import redactor

@click.group()
@click.option("--dry-run", is_flag=True, help="Run without making real API calls.")
@click.option("--base-url", type=str, help="Custom base URL for compatible endpoints.")
@click.pass_context
def cli(ctx, dry_run, base_url):
    """AI API Model Auditor CLI"""
    ctx.ensure_object(dict)
    ctx.obj["DRY_RUN"] = dry_run

    # Initialize configuration
    config_kwargs = {}
    if base_url:
        config_kwargs["base_url"] = base_url

    config = AppConfig(**config_kwargs)
    set_config(config)

    # Register secrets to redactor
    if config.openai_api_key:
        redactor.add_secret(config.openai_api_key)
    if config.anthropic_api_key:
        redactor.add_secret(config.anthropic_api_key)
    if config.gemini_api_key:
        redactor.add_secret(config.gemini_api_key)

@cli.command()
@click.option("--provider", required=True, type=click.Choice(["openai", "anthropic", "gemini"]), help="The provider to recon.")
@click.pass_context
def recon(ctx, provider):
    """Enumerate models for a given provider."""
    dry_run = ctx.obj["DRY_RUN"]

    from .adapters import get_adapter
    from .config import get_config
    from .probes.recon import probe_endpoint

    config = get_config()

    click.echo(f"Starting recon for {provider}...")
    if dry_run:
        click.echo(f"[DRY RUN] Would probe {provider} endpoint.")
        return

    try:
        adapter = get_adapter(provider, config)
        findings = probe_endpoint(adapter)

        if findings["status"] == "success":
            click.echo(f"Found {len(findings['models_discovered'])} models:")
            for m in findings['models_discovered']:
                click.echo(f" - {m}")
        else:
            click.echo(f"Recon failed: {findings.get('error')}", err=True)

    except Exception as e:
        click.echo(f"Error initializing adapter: {e}", err=True)

@cli.command()
@click.option("--provider", required=True, type=click.Choice(["openai", "anthropic", "gemini"]), help="The provider to audit.")
@click.option("--model", required=True, help="The model ID to target.")
@click.option("--prompt", default="Hello, are you functional?", help="The test prompt to send.")
@click.pass_context
def audit(ctx, provider, model, prompt):
    """Run a minimal end-to-end audit path on a specific model."""
    dry_run = ctx.obj["DRY_RUN"]

    from .adapters import get_adapter
    from .config import get_config
    from .storage.evidence import EvidenceStore
    from .safety import redact_string

    config = get_config()
    store = EvidenceStore()

    click.echo(f"Starting audit on {provider}/{model}...")

    messages = [{"role": "user", "content": prompt}]
    evidence_data = {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "mode": "dry-run" if dry_run else "live"
    }

    if dry_run:
        click.echo("[DRY RUN] Simulating audit probe.")
        evidence_data["response"] = "simulated response"
        path = store.save_evidence(f"audit_{provider}_{model}", evidence_data)
        click.echo(f"Evidence saved to {path}")
        return

    try:
        adapter = get_adapter(provider, config)
        response_data = adapter.chat(model, messages, max_tokens=100)

        evidence_data["response_data"] = response_data
        path = store.save_evidence(f"audit_{provider}_{model}", evidence_data)

        # Output safely
        safe_response = redact_string(response_data.get("content", ""))
        click.echo(f"Received response: {safe_response}")
        click.echo(f"Evidence saved to {path}")

    except Exception as e:
        click.echo(f"Audit failed: {e}", err=True)
        evidence_data["error"] = str(e)
        store.save_evidence(f"audit_error_{provider}_{model}", evidence_data)

if __name__ == "__main__":
    cli()
