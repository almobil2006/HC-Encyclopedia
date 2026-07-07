import typer

from hcenc.sage.client import sage

app = typer.Typer()


@app.command("download")
def download(page: int = 1):

    file = sage.fetch_page(page)

    typer.echo(f"Saved: {file}")
