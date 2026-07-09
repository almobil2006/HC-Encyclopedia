import typer

from hcenc.db.database import database
from hcenc.db.repository import repo
from hcenc.sage.sync import sync
from hcenc.sage.images import sync_images
from hcenc.sage.details import sync_details

app = typer.Typer(help="Synchronization")


@app.command()
def parse():

    database.initialize()

    total = sync.sync_all()

    typer.echo()

    typer.echo(f"Saved: {total}")

    typer.echo(f"Database: {repo.count_items()}")


@app.command()
def images():

    count = sync_images.sync()

    typer.echo(f"Downloaded: {count}")

@app.command()
def details():

    total = sync_details.sync()

    typer.echo(f"Downloaded: {total}")
