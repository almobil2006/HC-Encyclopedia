import math
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from hcenc.config import config
from hcenc.db.database import database
from hcenc.db.item_repository import item_repo
from hcenc.db.recommended_item_repository import recommended_item_repo
from hcenc.db.rune_repository import rune_repo
from hcenc.db.set_repository import set_repo
from hcenc.db.unit_repository import SLOTS, unit_repo


@asynccontextmanager
async def lifespan(app: FastAPI):

    database.initialize()

    yield


app = FastAPI(
    title="HC Encyclopedia",
    lifespan=lifespan,
)

templates = Jinja2Templates(
    directory=str(
        Path(__file__).parent / "templates"
    ),
)

app.mount(
    "/assets",
    StaticFiles(directory=str(config.assets)),
    name="assets",
)


def image_url(
    image_local: str = "",
    source_url: str = "",
) -> str:

    if image_local:

        local = config.root / image_local

        if local.exists():
            return "/" + image_local.replace("\\", "/")

    url = source_url or image_local or ""

    if url.startswith("/"):
        return "https://www.sagehc.eu" + url

    return url


def page_link(
    request: Request,
    target: int,
) -> str:

    params = dict(request.query_params)

    params["page"] = str(target)

    return (
        request.url.path
        + "?"
        + urlencode(params)
    )


templates.env.globals["image_url"] = image_url
templates.env.globals["page_link"] = page_link


#
# Перевод игровых терминов. SageHC отдаёт данные
# только на английском, поэтому классы, слоты и типы
# переводим словарём, остальное показываем как есть.
#

RU = {
    "Tank": "Танк",
    "Mage": "Маг",
    "Archer": "Лучник",
    "Artifact": "Артефакт",
    "Amulet": "Амулет",
    "Armor": "Броня",
    "Ring": "Кольцо",
    "Weapon": "Оружие",
    "Soul": "Душа",
    "Totem": "Тотем",
    "Armor Soul": "Душа брони",
    "Weapon Soul": "Душа оружия",
    "confrontation": "Противостояние",
    "massacre": "Резня",
    "fun": "Веселье",
    "Engraving": "Гравировка",
}

RU_CLASS = {
    "Tank": "танка",
    "Mage": "мага",
    "Archer": "лучника",
}


def ru(value: str) -> str:

    if not value:
        return ""

    if value in RU:
        return RU[value]

    parts = value.split(" ", 1)

    if len(parts) == 2 and parts[0] in RU_CLASS:
        return (
            RU.get(parts[1], parts[1])
            + " "
            + RU_CLASS[parts[0]]
        )

    return value


templates.env.filters["ru"] = ru


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    stats = {
        "items": item_repo.count(),
        "sets": set_repo.count_sets(),
        "runes": rune_repo.count(),
        "owned": item_repo.count_owned(),
        "units": len(unit_repo.all()),
    }

    return templates.TemplateResponse(
        request,
        "home.html",
        {"stats": stats},
    )


@app.get("/items", response_class=HTMLResponse)
def items_page(
    request: Request,
    q: str = "",
    fighter_type: str = "",
    slot: str = "",
    rarity: str = "",
    owned: str = "",
    page: int = Query(1, ge=1),
):

    size = 50

    only_owned = owned == "1"

    rows, total = item_repo.page(
        q=q,
        fighter_type=fighter_type,
        slot=slot,
        rarity=rarity,
        owned=only_owned,
        page=page,
        size=size,
    )

    return templates.TemplateResponse(
        request,
        "items.html",
        {
            "rows": rows,
            "total": total,
            "page": page,
            "pages": max(1, math.ceil(total / size)),
            "q": q,
            "fighter_type": fighter_type,
            "slot": slot,
            "rarity": rarity,
            "only_owned": only_owned,
            "facets": item_repo.facets(),
        },
    )


@app.post("/items/{code}/own")
def item_toggle_owned(
    request: Request,
    code: str,
):

    item = item_repo.get(code)

    if item is None:
        raise HTTPException(status_code=404)

    item_repo.set_owned(
        code,
        not item.owned,
    )

    return RedirectResponse(
        request.headers.get("referer") or "/items",
        status_code=303,
    )


@app.get("/items/{code}", response_class=HTMLResponse)
def item_detail(
    request: Request,
    code: str,
):

    item = item_repo.get(code)

    if item is None:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        request,
        "item.html",
        {"item": item},
    )


@app.get("/sets", response_class=HTMLResponse)
def sets_page(
    request: Request,
    q: str = "",
    fighter_type: str = "",
    page: int = Query(1, ge=1),
):

    size = 24

    rows, total = set_repo.page(
        q=q,
        fighter_type=fighter_type,
        page=page,
        size=size,
    )

    return templates.TemplateResponse(
        request,
        "sets.html",
        {
            "rows": rows,
            "total": total,
            "page": page,
            "pages": max(1, math.ceil(total / size)),
            "q": q,
            "fighter_type": fighter_type,
            "types": [
                "Tank",
                "Mage",
                "Archer",
            ],
        },
    )


@app.get("/sets/{code}", response_class=HTMLResponse)
def set_detail(
    request: Request,
    code: str,
):

    item = set_repo.get_set(code)

    if item is None:
        raise HTTPException(status_code=404)

    materials = []

    for name in (
        "essence",
        "material1",
        "material2",
        "material3",
        "material4",
    ):

        title = getattr(item, name + "_name")

        if not title:
            continue

        materials.append(
            {
                "name": title,
                "image": getattr(item, name + "_image"),
            }
        )

    return templates.TemplateResponse(
        request,
        "set.html",
        {
            "item": item,
            "materials": materials,
            "recommended": recommended_item_repo.by_set(code),
        },
    )


@app.get("/units", response_class=HTMLResponse)
def units_page(request: Request):

    units = []

    for unit in unit_repo.all():

        equipment = unit_repo.equipment(unit.id)

        units.append(
            {
                "unit": unit,
                "equipment": equipment,
            }
        )

    return templates.TemplateResponse(
        request,
        "units.html",
        {
            "units": units,
            "slots": SLOTS,
            "owned_count": item_repo.count_owned(),
            "set_names": {
                s.code: s.name_en
                for s in set_repo.all_sets()
            },
        },
    )


@app.post("/units")
def unit_create(
    name: str = Form(""),
    fighter_type: str = Form(""),
    level: int = Form(0),
):

    if name.strip():

        unit_repo.create(
            name=name.strip(),
            fighter_type=fighter_type,
            level=level or None,
        )

    return RedirectResponse(
        "/units",
        status_code=303,
    )


@app.post("/units/{unit_id}/delete")
def unit_delete(unit_id: int):

    unit_repo.delete(unit_id)

    return RedirectResponse(
        "/units",
        status_code=303,
    )


@app.get("/units/{unit_id}", response_class=HTMLResponse)
def unit_detail(
    request: Request,
    unit_id: int,
):

    unit = unit_repo.get(unit_id)

    if unit is None:
        raise HTTPException(status_code=404)

    equipment = unit_repo.equipment(unit_id)

    choices = {}

    for slot in SLOTS:

        choices[slot] = item_repo.by_slot(
            slot=slot,
            fighter_type=unit.fighter_type,
        )

    chosen_set = (
        set_repo.get_set(unit.set_code)
        if unit.set_code
        else None
    )

    return templates.TemplateResponse(
        request,
        "unit.html",
        {
            "unit": unit,
            "slots": SLOTS,
            "equipment": equipment,
            "choices": choices,
            "sets": set_repo.all_sets(),
            "chosen_set": chosen_set,
        },
    )


@app.post("/units/{unit_id}/set")
def unit_set(
    unit_id: int,
    set_code: str = Form(""),
):

    unit_repo.assign_set(unit_id, set_code)

    return RedirectResponse(
        f"/units/{unit_id}",
        status_code=303,
    )


@app.post("/units/{unit_id}/slot")
def unit_assign(
    unit_id: int,
    slot: str = Form(""),
    code: str = Form(""),
):

    unit_repo.assign(
        unit_id,
        slot,
        code,
    )

    return RedirectResponse(
        f"/units/{unit_id}",
        status_code=303,
    )


@app.get("/runes", response_class=HTMLResponse)
def runes_page(
    request: Request,
    q: str = "",
    rune_type: str = "",
    page: int = Query(1, ge=1),
):

    size = 100

    rows, total = rune_repo.page(
        q=q,
        rune_type=rune_type,
        page=page,
        size=size,
    )

    return templates.TemplateResponse(
        request,
        "runes.html",
        {
            "rows": rows,
            "total": total,
            "page": page,
            "pages": max(1, math.ceil(total / size)),
            "q": q,
            "rune_type": rune_type,
            "types": rune_repo.types(),
        },
    )


@app.get("/runes/{code}", response_class=HTMLResponse)
def rune_detail(
    request: Request,
    code: str,
):

    rune = rune_repo.get(code)

    if rune is None:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        request,
        "rune.html",
        {"rune": rune},
    )
