import click

from ai_api_model_auditor.cli_history import history_cmd

from .config import AppConfig, set_config
from .safety import redactor


@click.group()
@click.option(
    "--live", is_flag=True, help="Run with real API calls. Default is dry-run."
)
@click.option("--base-url", type=str, help="Custom base URL for compatible endpoints.")
@click.pass_context
def cli(ctx, live, base_url):
    """AI API Model Auditor CLI"""
    ctx.ensure_object(dict)
    ctx.obj["DRY_RUN"] = not live

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
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["openai", "anthropic", "gemini"]),
    help="The provider to recon.",
)
@click.pass_context
def recon(ctx, provider):
    """Enumerate models for a given provider."""
    dry_run = ctx.obj["DRY_RUN"]

    from .adapters import get_adapter
    from .config import get_config
    from .core.recon import probe_endpoint

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
            for m in findings["models_discovered"]:
                click.echo(f" - {m}")
        else:
            click.echo(f"Recon failed: {findings.get('error')}", err=True)

    except Exception as e:
        click.echo(f"Error initializing adapter: {e}", err=True)


@cli.command()
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["openai", "anthropic", "gemini"]),
    help="The provider to audit.",
)
@click.option("--model", required=True, help="The model ID to target.")
@click.option(
    "--prompt", default="Hello, are you functional?", help="The test prompt to send."
)
@click.option("--yes", is_flag=True, help="Bypass cost guard warnings automatically.")
@click.pass_context
def audit(ctx, provider, model, prompt, yes):
    """Run a minimal end-to-end audit path on a specific model."""
    dry_run = ctx.obj["DRY_RUN"]

    from .adapters import get_adapter
    from .config import get_config
    from .limits import estimate_cost
    from .safety import redact_string
    from .storage.evidence import EvidenceStore

    config = get_config()
    store = EvidenceStore()

    # Save the config as evidence
    store.save_config(config.model_dump())

    click.echo(f"Starting audit on {provider}/{model}...")

    messages = [{"role": "user", "content": prompt}]
    evidence_data = {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "mode": "dry-run" if dry_run else "live",
    }

    if dry_run:
        click.echo("[DRY RUN] Simulating audit probe.")
        evidence_data["response"] = "simulated response"
        path = store.save_evidence(
            f"audit_{provider}_{model}", evidence_data, metadata={"type": "audit"}
        )
        click.echo(f"Evidence saved to {path}")
        return

    # Extremely rough token count estimation (1 word ~= 1.3 tokens)
    input_tokens = len(prompt.split()) * 1.3
    max_output_tokens = 100

    est_cost = estimate_cost(provider, model, input_tokens, max_output_tokens)
    click.echo(f"Estimated maximum cost for this audit: ${est_cost:.6f}")

    if est_cost > 0.005 and not yes:
        click.confirm(
            f"Estimated cost is ${est_cost:.6f}, which exceeds threshold. Proceed?",
            abort=True,
        )
    elif not yes:
        click.confirm(
            f"Do you want to proceed with this cost (${est_cost:.6f})?", abort=True
        )

    try:
        adapter = get_adapter(provider, config)
        # Returns dict with raw_request, raw_response, timings
        response_data = adapter.chat(model, messages, max_tokens=max_output_tokens)

        evidence_data["response_data"] = response_data
        path = store.save_evidence(
            f"audit_{provider}_{model}",
            evidence_data,
            metadata={"type": "aud", "model": model},
        )

        # Output safely
        safe_response = redact_string(response_data.get("content", ""))
        # Only print the safely redacted content in verbose output
        click.echo(f"Received response: {safe_response}")
        click.echo(f"Evidence saved to {path}")

    except Exception as e:
        click.echo(f"Audit failed: {e}", err=True)
        evidence_data["error"] = str(e)
        store.save_evidence(
            f"audit_error_{provider}_{model}",
            evidence_data,
            metadata={"type": "err", "model": model},
        )


if __name__ == "__main__":
    cli()

cli.add_command(history_cmd)
