from aiornot.sync_client import Client
import click
from pathlib import Path
from pprint import pprint
import os
import json
from pathlib import Path
from pydantic import BaseModel
import sys


def load_api_key() -> str | None:
    token = os.getenv("AIORNOT_API_TOKEN")
    if token is not None:
        return token

    config_path = Path.home() / ".aiornot" / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("api_token")

    click.echo("No API token found.")
    click.echo(
        "Set `AIORNOT_API_TOKEN` environment variable or run `aiornot config`"
    )
    sys.exit(1)


def save_api_key(api_key: str) -> None:
    config_path = Path.home() / ".aiornot" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    do_save = True

    if config_path.exists():
        do_save = click.confirm("Overwrite existing API token?")
        if not do_save:
            click.echo("Not overwriting existing API token.")
            return
    if do_save:
        with open(config_path, "w") as f:
            json.dump({"api_token": api_key}, f)
            click.echo("API Key saved to ~/.aiornot/config.json")


def print_model_as_json(model: BaseModel) -> None:
    click.echo(model.model_dump_json(indent=4))


@click.group()
def cli():
    pass


@cli.group()
def token():
    pass


@cli.command()
@click.argument("source")
def image(source):
    client = Client(load_api_key())
    if source.startswith("http"):
        print_model_as_json(client.image_report_by_url(source))
    else:
        path = Path(source)
        if not path.exists():
            click.echo(f"File {source} does not exist.")
            sys.exit(1)
        print_model_as_json(client.image_report_by_file(path))


@cli.command()
@click.argument("source")
def audio(source):
    client = Client(api_key=load_api_key())
    if source.startswith("http"):
        print_model_as_json(client.audio_report_by_url(source))
    else:
        path = Path(source)
        if not path.exists():
            click.echo(f"File {source} does not exist.")
            sys.exit(1)
        print_model_as_json(client.audio_report_by_file(path))


@token.command()
def check():
    print_model_as_json(Client(api_key=load_api_key()).check_token())


@token.command()
def revoke():
    click.confirm("Are you sure you want to revoke your API token?", abort=True)
    pprint(Client(api_key=load_api_key()).revoke_token())


@token.command()
def refresh():
    client = Client()
    pprint(client.refresh_token())


@token.command()
def config():
    click.echo("Go to https://aiornot.com/dashboard/api to get an API key.")

    while True:
        api_key = click.prompt("API key")
        client = Client(api_key=api_key)
        if client.check_token():
            break
        else:
            click.echo("Invalid API key. Please try again.")

    save_api_key(api_key)


if __name__ == "__main__":
    cli()
