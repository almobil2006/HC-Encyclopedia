import typer

from hcenc.sage.sync_items import sync_items
from hcenc.sage.sync_item_details import sync_item_details
from hcenc.sage.sync_runes import sync_runes
from hcenc.sage.sync_sets import sync_sets
from hcenc.sage.sync_set_details import sync_set_details
from hcenc.sage.sync_set_images import sync_set_images
from hcenc.sage.sync_recommended_item_images import (
    sync_recommended_item_images,
)
from hcenc.sage.sync_rune_details import sync_rune_details
from hcenc.sage.sync_rune_images import sync_rune_images

app = typer.Typer()


@app.command("all")
def sync_all_commands():

    steps = (
        ("items", sync_items),
        ("item-details", sync_item_details),
        ("sets", sync_sets),
        ("set-details", sync_set_details),
        ("set-images", sync_set_images),
        ("runes", sync_runes),
        ("rune-details", sync_rune_details),
        ("rune-images", sync_rune_images),
    )

    total = 0

    for name, step in steps:

        print()
        print(f"=== {name} ===")

        total += step.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("items")
def items():

    total = sync_items.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("item-details")
def item_details():

    total = sync_item_details.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("runes")
def runes():

    total = sync_runes.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("rune-details")
def rune_details():

    total = sync_rune_details.sync()

    print()

    print(f"Downloaded: {total}")


@app.command("rune-images")
def rune_images():

    total = sync_rune_images.sync()

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