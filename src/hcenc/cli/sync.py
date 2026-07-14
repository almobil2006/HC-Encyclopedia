import typer

from hcenc.db.database import database
from hcenc.db.repository import repo

from hcenc.sage.sync import sync
from hcenc.sage.images import sync_images
from hcenc.sage.details import sync_details

from hcenc.sage.sync_sets import sync_sets
from hcenc.sage.sync_set_details import sync_set_details
from hcenc.sage.sync_set_images import sync_set_images

app = typer.Typer(help="Synchronization")

@app.command()
def parse():

    database.initialize()

    total = sync.sync_all()

    typer.echo()
    typer.echo(f"Saved: {total}")
    typer.echo(f"Database: {repo.count_items()}")

@app.command(name="set-images")
def set_images():

    total = sync_set_images.sync()

    print(f"Downloaded: {total}")

@app.command()
def details():

    database.initialize()

    total = sync_details.sync()

    typer.echo()
    typer.echo(f"Downloaded: {total}")


@app.command()
def images():

    database.initialize()

    total = sync_images.sync()

    typer.echo()
    typer.echo(f"Downloaded: {total}")


@app.command()
def sets():

    database.initialize()

    total = sync_sets.sync()

    typer.echo()
    typer.echo(f"Saved sets: {total}")


@app.command(name="set-details")
def set_details():

    database.initialize()

    total = sync_set_details.sync()

    typer.echo()
    typer.echo(f"Downloaded: {total}")