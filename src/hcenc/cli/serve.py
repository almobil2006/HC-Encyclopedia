import typer
import uvicorn


def serve(
    host: str = typer.Option(
        "127.0.0.1",
        help="Адрес сервера",
    ),
    port: int = typer.Option(
        8000,
        help="Порт сервера",
    ),
):

    typer.echo(
        f"HC Encyclopedia: http://{host}:{port}"
    )

    uvicorn.run(
        "hcenc.api.app:app",
        host=host,
        port=port,
    )
