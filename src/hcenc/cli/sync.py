import typer

from hcenc.sage.client import sage

app = typer.Typer()


@app.command("download")
def download(page: int = 1):

    file = sage.fetch_page(page)

    typer.echo(f"Saved: {file}")

@app.command("parse")
def parse(page: int = 1):

    items = sage.load_page(page)

    typer.echo(f"Items: {len(items)}")

    for item in items[:5]:
        typer.echo(item)
