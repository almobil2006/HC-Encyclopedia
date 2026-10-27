import json
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
# База знаний «кому что» (knowledge/recommendations.json)
#


def load_advice() -> list[dict]:

    path = (
        config.root
        / "knowledge"
        / "recommendations.json"
    )

    if not path.exists():
        return []

    try:

        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

    except ValueError:
        return []

    entries = []

    for fighter, block in data.items():

        if fighter.startswith("_"):
            continue

        if not isinstance(block, dict):
            continue

        entries.append(
            {
                "fighter": fighter,
                "match": [
                    word.lower()
                    for word in block.get("match", [])
                ],
                "role": block.get("role", ""),
                "artifact": block.get("artifact", {}),
                "guardian": block.get("guardian", {}),
            }
        )

    return entries


ADVICE = load_advice()


def advice_for(unit) -> list[dict]:

    name = (unit.name or "").lower()

    return [
        entry
        for entry in ADVICE
        if any(
            word in name
            for word in entry["match"]
        )
    ]


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


#
# названия редкости (числа mg-bot)
#

RARITY_RU = {
    "3": "необычная",
    "4": "редкая",
    "5": "эпическая",
    "6": "эпическая",
    "7": "легендарная",
    "8": "мифическая",
    "9": "древняя",
}

templates.env.globals["rarity_ru"] = RARITY_RU

#
# имена статов (как в игре)
#

STAT_RU = {
    "HEALTH": "здоровье",
    "PHYSICAL_ARMOR": "физ. броня",
    "MAGICAL_ARMOR": "маг. броня",
    "CRITICAL_CHANCE": "шанс крита",
    "DODGE": "уклонение",
    "RESISTANCE": "сопротивление",
    "ACCURACY": "точность",
    "PHYSICAL_DISRUPTION": "физ. пробитие",
    "MAGICAL_DISRUPTION": "маг. пробитие",
    "CRIT_POWER": "сила крита",
    "FORTITUDE": "стойкость",
    "PIERCE": "разрыв",
    "MAGIC_PIERCE": "маг. разрыв",
    "MAGIC": "сила магии",
    "SPEED": "скорость",
    "RADIUS": "радиус",
    "FIGHTER": "уровень бойца",
}

templates.env.globals["stat_ru"] = STAT_RU

#
# цвета самоцветов как в игре
#

GEM_TYPES = [
    "Урон",
    "Маг. урон",
    "Сила магии",
    "Здоровье",
    "Защита",
    "Маг. защита",
    "Крит",
    "Уворот",
]

GEM_COLORS = [
    "Серый",
    "Зелёный",
    "Синий",
    "Фиолетовый",
    "Оранжевый",
    "Красный",
]

templates.env.globals["gem_types"] = GEM_TYPES
templates.env.globals["gem_colors"] = GEM_COLORS

templates.env.filters["fromjson"] = lambda raw: (
    json.loads(raw)
    if raw
    else []
)


#
# Состав сетов из mg-bot: тип элемента -> слот
#

#
# базовые руны: слот x класс юнита
#

RUNE_HINTS = {
    ("Weapon", "Tank"): "Руна силы",
    ("Weapon", "Archer"): "Руна ловкости",
    ("Weapon", "Mage"): "Руна мудрости",
    ("Armor", "Tank"): "Руна стойкости",
    ("Armor", "Archer"): "Руна ярости",
    ("Armor", "Mage"): "Руна магии",
}

MGBOT_CLASSES = {
    1: "Tank",
    2: "Archer",
    3: "Mage",
}

MGBOT_SLOTS = {
    1: "Оружие",
    2: "Броня",
    3: "Кольцо",
    4: "Амулет",
    5: "Артефакт",
    6: "Душа оружия",
    7: "Душа брони",
    8: "Тотем",
}


def mgbot_elements(item) -> list[dict]:

    if not item.mgbot_elements:
        return []

    try:

        raw = json.loads(item.mgbot_elements)

    except ValueError:
        return []

    #
    # у комплекта бывают вещи разных классов
    # (оружие лучника + броня танка), поэтому
    # группируем по слоту И классу
    #

    groups: dict = {}

    for element in raw:

        key = (
            element.get("type"),
            element.get("battleClass"),
        )

        group = groups.setdefault(
            key,
            {
                "names": [],
                "rarities": [],
            },
        )

        name = element.get("name", "")

        if name and name not in group["names"]:
            group["names"].append(name)

        group["rarities"].append(
            element.get("rarity")
        )

    result = []

    for (slot_type, battle_class), group in sorted(
        groups.items(),
        key=lambda item: (
            item[0][0] or 0,
            item[0][1] or 0,
        ),
    ):

        rarities = sorted(
            r
            for r in set(group["rarities"])
            if r is not None
        )

        result.append(
            {
                "slot": MGBOT_SLOTS.get(
                    slot_type,
                    str(slot_type),
                ),
                "class": MGBOT_CLASSES.get(
                    battle_class,
                    "",
                ),
                "name": ", ".join(group["names"]),
                "rarities": " / ".join(
                    str(r)
                    for r in rarities
                ),
            }
        )

    return result


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
    owned: str = "",
    page: int = Query(1, ge=1),
):

    size = 24

    only_owned = owned == "1"

    rows, total = set_repo.page(
        q=q,
        fighter_type=fighter_type,
        owned=only_owned,
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
            "only_owned": only_owned,
            "types": [
                "Tank",
                "Mage",
                "Archer",
            ],
        },
    )


@app.post("/sets/{code}/own")
def set_toggle_owned(
    request: Request,
    code: str,
):

    item = set_repo.get_set(code)

    if item is None:
        raise HTTPException(status_code=404)

    set_repo.set_owned(
        code,
        not item.owned,
    )

    return RedirectResponse(
        request.headers.get("referer") or "/sets",
        status_code=303,
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
            "elements": mgbot_elements(item),
        },
    )


@app.get("/keepers", response_class=HTMLResponse)
def keepers_page(
    request: Request,
    q: str = "",
):

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    conditions = []
    params: dict = {}

    if q:
        conditions.append(
            "(lower(name) LIKE :q"
            " OR lower(obtained) LIKE :q)"
        )
        params["q"] = f"%{q.lower()}%"

    where = (
        "WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    with engine.begin() as conn:

        rows = conn.execute(
            sql_text(
                f"""
                SELECT
                    id,
                    name,
                    icon,
                    image_local,
                    power,
                    obtained,
                    abilities,
                    stats
                FROM keepers
                {where}
                ORDER BY power DESC
                """
            ),
            params,
        ).mappings()

        keepers = [
            dict(row)
            for row in rows
        ]

    return templates.TemplateResponse(
        request,
        "keepers.html",
        {
            "keepers": keepers,
            "q": q,
        },
    )


@app.get("/gems", response_class=HTMLResponse)
def gems_page(
    request: Request,
    q: str = "",
):

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    conditions = []
    params: dict = {}

    if q:
        conditions.append("lower(name) LIKE :q")
        params["q"] = f"%{q.lower()}%"

    where = (
        "WHERE " + " AND ".join(conditions)
        if conditions
        else ""
    )

    with engine.begin() as conn:

        rows = conn.execute(
            sql_text(
                f"""
                SELECT
                    id, name, icon, image_local,
                    stats, levels
                FROM gems
                {where}
                ORDER BY name
                """
            ),
            params,
        ).mappings()

        gems = [
            dict(row)
            for row in rows
        ]

    return templates.TemplateResponse(
        request,
        "gems.html",
        {
            "gems": gems,
            "q": q,
            "counter": gems_counter(),
        },
    )


@app.post("/gems/stock")
async def gems_stock_save(request: Request):

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    form = await request.form()

    with engine.begin() as conn:

        conn.execute(
            sql_text("DELETE FROM gem_stock")
        )

        for gtype in range(len(GEM_TYPES)):

            for color in range(len(GEM_COLORS)):

                for category in ("std", "max"):

                    field = f"stock_{gtype}_{color}_{category}"

                    count = form.get(field)

                    try:
                        count = int(count or 0)
                    except ValueError:
                        count = 0

                    if count <= 0:
                        continue

                    conn.execute(
                        sql_text(
                            """
                            INSERT INTO gem_stock
                                (type, color, category, count)
                            VALUES
                                (:type, :color, :category, :count)
                            """
                        ),
                        {
                            "type": gtype,
                            "color": color,
                            "category": category,
                            "count": count,
                        },
                    )

    return RedirectResponse(
        "/gems",
        status_code=303,
    )


def gems_counter() -> dict:

    #
    # надетые (из планов юнитов) и склад
    # по цветам и категориям
    #

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    inserted = {}
    stock = {}

    counter = {"inserted": inserted, "stock": stock}

    with engine.begin() as conn:

        rows = conn.execute(
            sql_text(
                """
                SELECT unit_id, slot, gems_json
                FROM unit_gems
                """
            )
        ).mappings()

        for row in rows:

            try:
                gems = json.loads(
                    row["gems_json"] or "[]"
                )
            except ValueError:
                continue

            for gem in gems:

                if not isinstance(gem, dict):
                    continue

                key = (
                    gem.get("t"),
                    gem.get("c"),
                    gem.get("cat"),
                )

                inserted[key] = (
                    inserted.get(key, 0) + 1
                )

        stock_rows = conn.execute(
            sql_text(
                """
                SELECT type, color, category, count
                FROM gem_stock
                """
            )
        ).mappings()

        for row in stock_rows:

            key = (
                row["type"],
                row["color"],
                row["category"],
            )

            stock[key] = stock.get(key, 0) + (
                row["count"] or 0
            )

    return counter


@app.get("/units", response_class=HTMLResponse)
def units_page(
    request: Request,
    sort: str = "desc",
):

    units = []

    for unit in unit_repo.all(order=sort):

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
                s.code: (s.name_ru or s.name_en)
                for s in set_repo.all_sets()
            },
            "sets_by_code": {
                s.code: s
                for s in set_repo.all_sets()
            },
            "keeper_names": {
                k["id"]: k["name"]
                for k in (
                    unit_repo.keeper_names()
                )
            },
            "owned_sets": set_repo.owned_sets(),
            "sort": sort if sort in ("asc", "desc") else "desc",
        },
    )


@app.get("/units/analysis", response_class=HTMLResponse)
def units_analysis(request: Request):

    #
    # отчёт по отряду: сила, пустые слоты,
    # предметы чужого класса
    #

    report = []

    total_power = 0
    total_empty = 0
    total_mismatch = 0

    for unit in unit_repo.all():

        equipment = unit_repo.equipment(unit.id)

        power = 0
        empty = []
        mismatch = []

        for slot in SLOTS:

            item = equipment.get(slot)

            if item is None:
                empty.append(slot)
                continue

            if item.power_max:
                power += item.power_max

            if (
                item.fighter_type
                and unit.fighter_type
                and item.fighter_type != unit.fighter_type
            ):
                mismatch.append(slot)

        total_power += power
        total_empty += len(empty)
        total_mismatch += len(mismatch)

        chosen_set = (
            set_repo.get_set(unit.set_code)
            if unit.set_code
            else None
        )

        report.append(
            {
                "unit": unit,
                "power": power,
                "empty": empty,
                "mismatch": mismatch,
                "set": chosen_set,
            }
        )

    return templates.TemplateResponse(
        request,
        "analysis.html",
        {
            "report": report,
            "total_power": total_power,
            "total_empty": total_empty,
            "total_mismatch": total_mismatch,
        },
    )


@app.post("/units")
def unit_create(
    name: str = Form(""),
    fighter_type: str = Form(""),
    level: int = Form(0),
    priority: int = Form(0),
):

    if name.strip():

        unit_repo.create(
            name=name.strip(),
            fighter_type=fighter_type,
            level=level or None,
            priority=priority,
        )

    return RedirectResponse(
        "/units",
        status_code=303,
    )


@app.post("/units/{unit_id}/priority")
def unit_priority(
    unit_id: int,
    priority: int = Form(0),
):

    unit_repo.set_priority(unit_id, priority)

    return RedirectResponse(
        "/units",
        status_code=303,
    )


@app.post("/units/from-set/{set_code}")
def unit_from_set(set_code: str):

    chosen = set_repo.get_set(set_code)

    if chosen is None:
        raise HTTPException(status_code=404)

    unit_id = unit_repo.create(
        name=(chosen.name_ru or chosen.name_en),
        fighter_type=chosen.fighter_type,
        level=None,
    )

    unit_repo.assign_set(
        unit_id,
        set_code,
    )

    return RedirectResponse(
        f"/units/{unit_id}",
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
            any_class=True,
        )

    chosen_set = (
        set_repo.get_set(unit.set_code)
        if unit.set_code
        else None
    )

    all_sets = set_repo.all_sets()

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    keeper = None

    if unit.keeper_id:

        with engine.begin() as conn:

            row = conn.execute(
                sql_text(
                    """
                    SELECT
                        id, name, icon, image_local,
                        power, stats
                    FROM keepers
                    WHERE id=:keeper_id
                    """
                ),
                {"keeper_id": unit.keeper_id},
            ).mappings().first()

        keeper = dict(row) if row else None

    with engine.begin() as conn:

        rows = conn.execute(
            sql_text(
                """
                SELECT id, name, power
                FROM keepers
                ORDER BY power DESC
                """
            )
        ).mappings()

        all_keepers = [
            dict(row)
            for row in rows
        ]

        gem_rows = conn.execute(
            sql_text(
                """
                SELECT id, name, stats
                FROM gems
                ORDER BY name
                """
            )
        ).mappings()

        all_gems = [
            dict(row)
            for row in gem_rows
        ]

        gem_plans = conn.execute(
            sql_text(
                """
                SELECT slot, engr_id, gems_json
                FROM unit_gems
                WHERE unit_id=:unit_id
                """
            ),
            {"unit_id": unit_id},
        ).mappings()

        plans = {
            row["slot"]: {
                "engr_id": row["engr_id"],
                "gems": json.loads(
                    row["gems_json"] or "{}"
                ),
            }
            for row in gem_plans
        }

    gems_by_id = {
        g["id"]: g
        for g in all_gems
    }

    return templates.TemplateResponse(
        request,
        "unit.html",
        {
            "unit": unit,
            "slots": SLOTS,
            "equipment": equipment,
            "choices": choices,
            "sets": all_sets,
            "my_sets": [
                s
                for s in all_sets
                if s.owned
            ],
            "chosen_set": chosen_set,
            "rune_hints": RUNE_HINTS,
            "advice": advice_for(unit),
            "keeper": keeper,
            "all_keepers": all_keepers,
            "all_gems": all_gems,
            "gems_by_id": gems_by_id,
            "gem_plans": plans,
        },
    )


@app.post("/units/{unit_id}/gems/{slot}")
async def unit_gems_save(
    unit_id: int,
    slot: str,
    request: Request,
):

    from sqlalchemy import text as sql_text

    from hcenc.db.engine import engine

    form = await request.form()

    engr_id = 0

    try:
        engr_id = int(form.get("engr_id") or 0)
    except (ValueError, TypeError):
        engr_id = 0

    gems = []

    for index in range(6):

        gtype = form.get(f"gem_{index}_type")
        gcolor = form.get(f"gem_{index}_color")
        gcat = form.get(f"gem_{index}_cat")

        if gtype in (None, ""):
            continue

        try:
            gtype = int(gtype)
        except (ValueError, TypeError):
            continue

        if gtype < 0 or gtype >= len(GEM_TYPES):
            continue

        try:
            gcolor = int(gcolor)
        except (ValueError, TypeError):
            gcolor = 0

        if gcolor < 0 or gcolor >= len(GEM_COLORS):
            gcolor = 0

        if gcat not in ("std", "max"):
            gcat = "std"

        gems.append(
            {
                "t": gtype,
                "c": gcolor,
                "cat": gcat,
            }
        )

    gems_json = (
        json.dumps(gems, ensure_ascii=False)
        if gems
        else ""
    )

    with engine.begin() as conn:

        if engr_id and gems_json:

            conn.execute(
                sql_text(
                    """
                    INSERT INTO unit_gems
                        (unit_id, slot, engr_id, gems_json)
                    VALUES
                        (:unit_id, :slot, :engr_id, :gems_json)
                    ON CONFLICT (unit_id, slot)
                    DO UPDATE SET
                        engr_id=:engr_id,
                        gems_json=:gems_json
                    """
                ),
                {
                    "unit_id": unit_id,
                    "slot": slot,
                    "engr_id": engr_id,
                    "gems_json": gems_json,
                },
            )

        else:

            conn.execute(
                sql_text(
                    """
                    DELETE FROM unit_gems
                    WHERE unit_id=:unit_id
                      AND slot=:slot
                    """
                ),
                {
                    "unit_id": unit_id,
                    "slot": slot,
                },
            )

    return RedirectResponse(
        f"/units/{unit_id}",
        status_code=303,
    )


@app.post("/units/{unit_id}/keeper")
def unit_keeper(
    unit_id: int,
    keeper_id: int = Form(0),
):

    unit_repo.set_keeper(
        unit_id,
        keeper_id or None,
    )

    return RedirectResponse(
        f"/units/{unit_id}",
        status_code=303,
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


@app.post("/units/{unit_id}/auto")
def unit_auto_pick(
    unit_id: int,
):

    unit = unit_repo.get(unit_id)

    if unit is None:
        raise HTTPException(status_code=404)

    equipment = unit_repo.equipment(unit_id)

    used = unit_repo.equipped_codes()

    for slot in SLOTS:

        #
        # заполняем только пустые слоты,
        # ручной выбор не трогаем
        #

        if equipment.get(slot):
            continue

        for candidate in item_repo.by_slot(
            slot=slot,
            fighter_type=unit.fighter_type,
        ):

            if candidate.code in used:
                continue

            unit_repo.assign(
                unit_id,
                slot,
                candidate.code,
            )

            used.add(candidate.code)

            break

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
