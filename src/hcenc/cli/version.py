from rich import print

from hcenc import __version__


def version():
    """
    Show application version.
    """

    print(f"[bold green]HC Encyclopedia[/bold green] {__version__}")
