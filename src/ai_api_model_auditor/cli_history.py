import json

import click

from .storage.history import HistoryManager
from .storage.replay import Replayer


@click.group(name="history")
def history_cmd():
    """Commands for managing and analyzing historical audit runs."""
    pass


@history_cmd.command(name="list")
@click.option("--provider", required=True, help="The API provider (e.g., openai).")
@click.option("--model", required=True, help="The model identifier.")
@click.option("--db-path", default="history.db", help="Path to the SQLite database.")
def list_history(provider, model, db_path):
    """List historical audit runs for a specific provider and model."""
    manager = HistoryManager(db_path=db_path)
    runs = manager.get_history(provider=provider, model=model)
    click.echo(f"Found {len(runs)} run(s) for {provider}/{model}.")
    for idx, run in enumerate(runs, 1):
        click.echo(f"{idx}. Date: {run.get('run_date')}")


@history_cmd.command(name="compare")
@click.option("--provider", required=True, help="The API provider.")
@click.option("--model", required=True, help="The model identifier.")
@click.option(
    "--date1", required=True, help="Date of the first run to compare (YYYY-MM-DD)."
)
@click.option(
    "--date2", required=True, help="Date of the second run to compare (YYYY-MM-DD)."
)
@click.option("--db-path", default="history.db", help="Path to the SQLite database.")
def compare_history(provider, model, date1, date2, db_path):
    """Compare two historical runs to detect drift."""
    manager = HistoryManager(db_path=db_path)
    runs1 = manager.get_history(provider=provider, model=model, date=date1)
    runs2 = manager.get_history(provider=provider, model=model, date=date2)

    if not runs1:
        click.echo(f"No run found for {provider}/{model} on {date1}.")
        return
    if not runs2:
        click.echo(f"No run found for {provider}/{model} on {date2}.")
        return

    drifts = manager.detect_drift(runs1[0], runs2[0])
    if drifts:
        click.echo("Drift detected:")
        for drift in drifts:
            click.echo(f"- {drift}")
    else:
        click.echo("No drift detected between the two runs.")


@history_cmd.command(name="replay")
@click.option("--provider", required=True, help="The API provider.")
@click.option("--model", required=True, help="The model identifier.")
@click.option("--date", required=True, help="Date of the run to replay.")
@click.option("--db-path", default="history.db", help="Path to the SQLite database.")
def replay_run(provider, model, date, db_path):
    """Replay a sanitized historical audit run."""
    manager = HistoryManager(db_path=db_path)
    runs = manager.get_history(provider=provider, model=model, date=date)

    if not runs:
        click.echo(f"No run found for {provider}/{model} on {date}.")
        return

    replayer = Replayer(history_manager=manager)
    replayed_data = replayer.replay_run(runs[0])
    click.echo(json.dumps(replayed_data, indent=2))
