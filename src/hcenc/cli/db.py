import typer

from hcenc.db.database import database

app = typer.Typer()


@app.command("init")
def init_database():

    database.initialize()

    typer.echo("Database initialized.")
