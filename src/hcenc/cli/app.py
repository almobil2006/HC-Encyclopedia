import typer

from hcenc.cli.version import version
from hcenc.cli.doctor import doctor
from hcenc.cli.db import app as db_app
from hcenc.cli.sync import app as sync_app

app = typer.Typer(
    help="HC Encyclopedia",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

app.command()(version)
app.command()(doctor)

app.add_typer(
    db_app,
    name="db",
)
app.add_typer(
    sync_app,
    name="sync",
)

if __name__ == "__main__":
    app()
