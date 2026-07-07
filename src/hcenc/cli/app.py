import typer

from hcenc.cli.version import version
from hcenc.cli.doctor import doctor

app = typer.Typer(
    help="HC Encyclopedia",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

app.command()(version)
app.command()(doctor)

if __name__ == "__main__":
    app()
