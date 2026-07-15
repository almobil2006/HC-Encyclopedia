import typer

from hcenc.sage.sync_items import sync_items
from hcenc.sage.sync_runes import sync_runes
from hcenc.sage.sync_sets import sync_sets
from hcenc.sage.sync_set_details import sync_set_details
from hcenc.sage.sync_set_images import sync_set_images
from hcenc.sage.sync_recommended_item_images import (
    sync_recommended_item_images,
)

app = typer.Typer()


@app.command("items")
def items():

    total = sync_items.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("runes")
def runes():

    total = sync_runes.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("sets")
def sets():

    total = sync_sets.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("set-details")
def set_details():

    total = sync_set_details.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("set-images")
def set_images():

    total = sync_set_images.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("recommended-item-images")
def recommended_item_images():

    total = sync_recommended_item_images.sync()

    print()

    print(f"Downloaded: {total}")