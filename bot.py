import os
import logging
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, Contact
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = os.getenv("TOKEN")
if not API_TOKEN:
    raise RuntimeError("TOKEN env-var is required!")

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
bot: Bot = Bot(API_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher()

ADMIN_IDS = {1294415669}


INFO_FILE = "user_info.json"
try:
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        USER_INFO = json.load(f)
except FileNotFoundError:
    USER_INFO = {}

def save_info() -> None:
    with open(INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_INFO, f, ensure_ascii=False, indent=2)

def ensure_user(u) -> None:
    uid = str(u.id)
    info = USER_INFO.setdefault(uid, {})
    changed = False
    if info.get("username") != u.username:
        info["username"] = u.username
        changed = True
    if info.get("first_name") != u.first_name:
        info["first_name"] = u.first_name
        changed = True
    if info.get("last_name") != u.last_name:
        info["last_name"] = u.last_name
        changed = True
    if changed:
        save_info()

def set_phone(user_id: int, phone: str) -> None:
    info = USER_INFO.setdefault(str(user_id), {})
    if info.get("phone") != phone:
        info["phone"] = phone
        save_info()

def display_name(uid: int) -> str:
    info = USER_INFO.get(str(uid), {})
    name = (info.get("first_name", "") + " " + info.get("last_name", "")).strip()
    username = info.get("username")
    if username:
        username = f"@{username}"
    else:
        username = ""
    return " ".join(part for part in [name, username] if part).strip() or f"id {uid}"

def format_stats(uid: int) -> str:
    st = get_stats(uid)
    info = USER_INFO.get(str(uid), {})
    phone = info.get("phone", "—")
    header = f"Имя: {display_name(uid)} (id: {uid}, телефон: {phone})"
    categories = ["Виски", "Водка", "Пиво", "Вино", "Ликёр"]
    counts = {c: 0 for c in categories}
    for cat in st["brands"].values():
        counts[cat] = counts.get(cat, 0) + 1
    brand_lines = "\n".join(f"  — {c}: {counts.get(c, 0)}" for c in categories)
    return (
        f"{header}\n"
        f"Лучший результат в Блице: {st['best_blitz']}\n"
        f"Завершено тестов: {st['tests']}\n"
        f"Правильных ответов: {st['points']}\n"
        f"Просмотренные бренды:\n{brand_lines}"
    )

STATS_FILE = "user_stats.json"
try:
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        USER_STATS = json.load(f)
except FileNotFoundError:
    USER_STATS = {}

def save_stats() -> None:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_STATS, f, ensure_ascii=False, indent=2)

def get_stats(user_id: int) -> dict:
    uid = str(user_id)
    if uid not in USER_STATS:
        USER_STATS[uid] = {
            "tests": 0,
            "brands": {},  # {brand_name: category}
            "points": 0,
            "last": "",
            "best_truth": 0,
            "best_assoc": 0,
            "best_blitz": 0
        }
    return USER_STATS[uid]

def record_brand_view(user_id: int, brand: str, category: str) -> None:
    """Store the brand under its category for the user."""
    stats = get_stats(user_id)
    if brand not in stats["brands"]:
        stats["brands"][brand] = category
    stats["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats()

def record_test_result(user_id: int, points: int) -> None:
    stats = get_stats(user_id)
    stats["tests"] += 1
    stats["points"] += points
    stats["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats()

def record_truth_result(user_id: int, points: int) -> int:
    """Update user's best score for truth-or-dare game and total points."""
    stats = get_stats(user_id)
    if points > stats.get("best_truth", 0):
        stats["best_truth"] = points
    stats["points"] += points
    stats["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats()
    return stats["best_truth"]

def record_assoc_result(user_id: int, points: int) -> int:
    """Update user's best score for associations game and total points."""
    stats = get_stats(user_id)
    if points > stats.get("best_assoc", 0):
        stats["best_assoc"] = points
    stats["points"] += points
    stats["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats()
    return stats["best_assoc"]

def record_blitz_result(user_id: int, points: int) -> int:
    """Update user's best score for blitz game and total points."""
    stats = get_stats(user_id)
    if points > stats.get("best_blitz", 0):
        stats["best_blitz"] = points
    stats["points"] += points
    stats["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_stats()
    return stats["best_blitz"]

def track_brand(name: str, category: str):
    """Decorator to record a brand view with its category."""
    def decorator(func):
        async def wrapper(m: Message, *a, **kw):
            kw.pop("bot", None)  # aiogram may inject bot kwarg
            record_brand_view(m.from_user.id, name, category)
            await func(m, *a, **kw)
        return wrapper
    return decorator

def clear_user_state(user_id: int) -> None:
    """Reset search and quiz states for given user."""
    SEARCH_ACTIVE.discard(user_id)
    USER_STATE.pop(user_id, None)
    GAME_STATE.pop(user_id, None)
    ASSOC_STATE.pop(user_id, None)
    BLITZ_STATE.pop(user_id, None)

def normalize(text: str) -> str:
    """Return lowercased text without spaces or punctuation for matching."""
    return "".join(ch.lower() for ch in text if ch.isalnum())

def kb(*labels: str, width: int = 2) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for text in labels:
        builder.add(KeyboardButton(text=text))
    builder.adjust(width)
    return builder.as_markup(resize_keyboard=True)

MAIN_KB = kb(
    "🗂️ Меню брендов",
    "🔍 Поиск",
    "🍹 Коктейли",
    "🧠 Тренажёр знаний",
    "📊 Моя статистика",
    width=2
)

ADMIN_MAIN_KB = kb(
    "🗂️ Меню брендов",
    "🔍 Поиск",
    "🍹 Коктейли",
    "🧠 Тренажёр знаний",
    "📊 Моя статистика",
    "👑 Админ-панель",
    width=2
)

def main_kb(uid: int) -> ReplyKeyboardMarkup:
    return ADMIN_MAIN_KB if uid in ADMIN_IDS else MAIN_KB

ADMIN_KB = kb(
    "📊 Топ-10 по блицу",
    "📝 Топ-10 по тестам",
    "🏷️ Топ-10 по брендам",
    "🔍 Поиск по user_id",
    "🔍 Поиск по имени",
    "🔍 По номеру телефона",
    "🏠 Главное меню",
    width=1,
)

CONTACT_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить номер", request_contact=True)], [KeyboardButton(text="Отмена")]],
    resize_keyboard=True,
)

BRAND_MENU_KB = kb(
    "🍷 Вино", "🧊 Водка",
    "🥃 Виски", "🍺 Пиво",
    "🦌 Ягермейстер", "Назад",
    width=2
)

def get_whisky_kb() -> ReplyKeyboardMarkup:
    return kb(
        "Monkey Shoulder", "Glenfiddich 12 Years", "Glenfiddich Fire & Cane",
        "Glenfiddich IPA", "Grant's Classic", "Grant's Summer Orange",
        "Grant's Winter Dessert", "Grant's Tropical Fiesta",
        "Tullamore D.E.W.", "Tullamore D.E.W. Honey", "Назад к категориям",
        width=2,
    )

def get_vodka_kb() -> ReplyKeyboardMarkup:
    return kb(
        "Серебрянка", "Reyka", "Finlandia", "Зелёная марка",
        "Талка", "Русский Стандарт", "Назад к категориям", width=2,
    )

def get_beer_kb() -> ReplyKeyboardMarkup:
    return kb(
        "Paulaner", "Blue Moon",
        "London Pride", "Coors",
        "Staropramen", "Назад к категориям",
        width=2,
    )

def get_wine_kb() -> ReplyKeyboardMarkup:
    return kb(
        "Mateus Original Rosé", "Undurraga Sauvignon Blanc",
        "Devil’s Rock Riesling", "Piccola Nostra",
        "Эль Санчес", "Шале де Сюд", "Назад к категориям", width=2,
    )

def get_jager_kb() -> ReplyKeyboardMarkup:
    return kb("Jägermeister", "Назад к категориям", width=2)

main_router = Router()
brand_menu_router = Router()
admin_router = Router()

@main_router.message(CommandStart())
async def cmd_start(m: Message):
    clear_user_state(m.from_user.id)
    ensure_user(m.from_user)
    await m.answer("Привет! Выбери категорию:", reply_markup=main_kb(m.from_user.id))

@main_router.message(F.text == "📊 Моя статистика")
async def show_stats(m: Message):
    clear_user_state(m.from_user.id)
    st = get_stats(m.from_user.id)
    last = st["last"] or "—"
    categories = ["Виски", "Водка", "Пиво", "Вино", "Ликёр"]
    counts = {c: 0 for c in categories}
    for cat in st["brands"].values():
        counts[cat] = counts.get(cat, 0) + 1
    brand_lines = "\n".join(f"— {c}: {counts.get(c, 0)}" for c in categories)
    await m.answer(
        f"Пройдено тестов: {st['tests']}\n"
        f"Набрано баллов: {st['points']}\n"
        f"Рекорд в игре \"Верю — не верю\": {st['best_truth']}\n"
        f"Рекорд в игре \"Ассоциации\": {st['best_assoc']}\n"
        f"Рекорд в игре \"Блиц\": {st['best_blitz']}\n"
        "Просмотренные бренды:\n"
        f"{brand_lines}\n"
        f"Последняя активность: {last}",
        reply_markup=main_kb(m.from_user.id),
    )

@main_router.message(F.text == "🗂️ Меню брендов")
async def show_brand_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Выберите категорию:", reply_markup=BRAND_MENU_KB)

@main_router.message(F.text == "📞 Поделиться контактом")
async def request_phone(m: Message):
    await m.answer("Нажмите кнопку, чтобы отправить ваш номер", reply_markup=CONTACT_KB)

@dp.message(lambda m: m.contact is not None)
async def save_phone(m: Message):
    set_phone(m.from_user.id, m.contact.phone_number)
    await m.answer("Спасибо! Телефон сохранён", reply_markup=main_kb(m.from_user.id))

@main_router.message(lambda m: m.text == "👑 Админ-панель" and m.from_user.id in ADMIN_IDS)
async def admin_menu(m: Message):
    await m.answer("Админ-панель", reply_markup=ADMIN_KB)

def _top_by(key: str) -> list[tuple[int, int]]:
    data = []
    for uid, st in USER_STATS.items():
        data.append((int(uid), st.get(key, 0)))
    data.sort(key=lambda x: x[1], reverse=True)
    return data[:10]

@admin_router.message(F.text == "📊 Топ-10 по блицу")
async def top_blitz(m: Message):
    lines = [f"{i}. {display_name(uid)} (id {uid}) — {score}" for i, (uid, score) in enumerate(_top_by("best_blitz"), 1)]
    await m.answer("\n".join(lines) or "Нет данных", reply_markup=ADMIN_KB)

@admin_router.message(F.text == "📝 Топ-10 по тестам")
async def top_tests(m: Message):
    lines = [f"{i}. {display_name(uid)} (id {uid}) — {score}" for i, (uid, score) in enumerate(_top_by("tests"), 1)]
    await m.answer("\n".join(lines) or "Нет данных", reply_markup=ADMIN_KB)

@admin_router.message(F.text == "🏷️ Топ-10 по брендам")
async def top_brands(m: Message):
    data = []
    for uid, st in USER_STATS.items():
        data.append((int(uid), len(st.get("brands", {}))))
    data.sort(key=lambda x: x[1], reverse=True)
    lines = [f"{i}. {display_name(uid)} (id {uid}) — {count}" for i, (uid, count) in enumerate(data[:10], 1)]
    await m.answer("\n".join(lines) or "Нет данных", reply_markup=ADMIN_KB)

@admin_router.message(F.text == "🔍 Поиск по user_id")
async def ask_uid(m: Message):
    ADMIN_STATE[m.from_user.id] = {"mode": "uid"}
    await m.answer("Введите user_id:", reply_markup=ReplyKeyboardRemove())

@admin_router.message(F.text == "🔍 Поиск по имени")
async def ask_name(m: Message):
    ADMIN_STATE[m.from_user.id] = {"mode": "name"}
    await m.answer("Введите имя, фамилию или username:", reply_markup=ReplyKeyboardRemove())

@admin_router.message(F.text == "🔍 По номеру телефона")
async def ask_phone_admin(m: Message):
    ADMIN_STATE[m.from_user.id] = {"mode": "phone"}
    await m.answer("Введите номер телефона:", reply_markup=ReplyKeyboardRemove())

@admin_router.message(F.text == "🏠 Главное меню")
async def admin_to_main(m: Message):
    ADMIN_STATE.pop(m.from_user.id, None)
    await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))

@admin_router.message(lambda m: m.from_user.id in ADMIN_STATE)
async def handle_admin_input(m: Message):
    state = ADMIN_STATE.pop(m.from_user.id)
    mode = state["mode"]
    if mode == "uid":
        uid = m.text.strip()
        if uid.isdigit() and uid in USER_STATS:
            await m.answer(format_stats(int(uid)), reply_markup=ADMIN_KB)
        else:
            await m.answer("Пользователь не найден", reply_markup=ADMIN_KB)
    elif mode == "name":
        q = m.text.lower()
        matches = []
        for uid, info in USER_INFO.items():
            if (
                q in (info.get("username") or "").lower()
                or q in (info.get("first_name") or "").lower()
                or q in (info.get("last_name") or "").lower()
            ):
                matches.append(int(uid))
        if not matches:
            await m.answer("Пользователь не найден", reply_markup=ADMIN_KB)
        elif len(matches) == 1:
            await m.answer(format_stats(matches[0]), reply_markup=ADMIN_KB)
        else:
            builder = ReplyKeyboardBuilder()
            for uid in matches:
                builder.add(KeyboardButton(text=f"{display_name(uid)} | {uid}"))
            builder.adjust(1)
            ADMIN_STATE[m.from_user.id] = {"mode": "choose", "list": matches}
            await m.answer("Несколько совпадений. Выберите пользователя:", reply_markup=builder.as_markup(resize_keyboard=True))
    elif mode == "phone":
        phone = m.text.strip()
        for uid, info in USER_INFO.items():
            if info.get("phone") == phone:
                await m.answer(format_stats(int(uid)), reply_markup=ADMIN_KB)
                break
        else:
            await m.answer("Пользователь не найден", reply_markup=ADMIN_KB)
    elif mode == "choose":
        # user picks from previous list
        for uid in state.get("list", []):
            if m.text == f"{display_name(uid)} | {uid}":
                await m.answer(format_stats(uid), reply_markup=ADMIN_KB)
                break
        else:
            await m.answer("Пользователь не найден", reply_markup=ADMIN_KB)

@brand_menu_router.message(F.text == "Назад")
async def brand_menu_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))



whisky_router = Router()

@whisky_router.message(F.text == "🥃 Виски")
async def whisky_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("🥃 Выбери бренд виски:", reply_markup=get_whisky_kb())

@whisky_router.message(F.text == "Назад к категориям")
async def whisky_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Категории", reply_markup=BRAND_MENU_KB)

@track_brand("Monkey Shoulder", "Виски")
async def monkey_shoulder(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG1Gg4mSjJixcbMGy0c8I78DrLN9OpAAJe7jEbCVnJSTfCOMW8hxrQAQADAgADeAADNgQ",  # твой file_id
        caption=(
            "<b>Monkey Shoulder</b>\n"
            "• Купажированный шотландский виски от William Grant & Sons\n"
            "• Состоит из солодов Glenfiddich, Balvenie и Kininvie\n"
            "• Название отсылает к травме плеча у солодовщиков\n"
            "• Яркий ванильно-медовый аромат с нотами цитруса\n"
            "• Вкус: тёплая карамель, специи, тосты\n"
            "• Бархатистый и мягкий, идеально сбалансирован\n"
            "• Крепость: 40 % ABV\n"
            "• Идеален для коктейлей: Old Fashioned, Whisky Sour\n"
            "• Три медные обезьяны на бутылке — символ тройного бленда"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Glenfiddich 12 Years", "Виски")
async def glenfiddich_12(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG2Gg4ncf9Rpxv9rooJ0Ha2FD40CORAAK_8jEbPObJSR3uT8xKG0UpAQADAgADeQADNgQ",  # ← сюда вставь свой file_id без кавычек
        caption=(
            "<b>Glenfiddich 12 Years Old</b>\n"
            "• Односолодовый шотландский виски из региона Спейсайд\n"
            "• Аромат: груша, дуб, свежесть\n"
            "• Вкус: зелёные яблоки, ваниль, лёгкий дуб\n"
            "• Выдержан минимум 12 лет в бочках из-под бурбона и хереса\n"
            "• Производится на самой продаваемой винокурне в мире\n"
            "• Символ — олень на эмблеме (в переводе: «долина оленей»)\n"
            "• Крепость: 40 % ABV\n"
            "• Идеален для знакомства с миром односолодовых виски\n"
            "• Отлично подойдёт как в чистом виде, так и со льдом"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Glenfiddich Fire & Cane", "Виски")
async def fire_and_cane(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG2mg4ncuOjEqivJgv27H62zK4XOvFAAIK9TEb1P3ISXHpOhsLyQ4DAQADAgADeQADNgQ",  # ← вставь свой file_id
        caption=(
            "<b>Glenfiddich Fire & Cane</b>\n"
            "• Экспериментальная линейка от Glenfiddich\n"
            "• Купажированный односолодовый виски с торфяным дымком\n"
            "• Аромат: сладкий дым, дуб, зелёное яблоко\n"
            "• Вкус: карамель, специи, жареный сахар, дым\n"
            "• Финиш: насыщенный, с оттенками костра и специй\n"
            "• Выдержка в бочках из-под бурбона и рома из Латинской Америки\n"
            "• Отличное сочетание сладости и торфа\n"
            "• Крепость: 43 % ABV\n"
            "• Подходит тем, кто хочет попробовать «дым» впервые\n"
            "• Подчёркивает инновации Glenfiddich"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Glenfiddich IPA", "Виски")
async def ipa_experiment(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG52g4npbaJO1p_0s7aVNpQ5_r9nkEAAIT9TEb1P3ISRjGBYkQaU3hAQADAgADeQADNgQ",  # ← вставь свой file_id
        caption=(
            "<b>Glenfiddich IPA</b>\n"
            "• Первая в мире коллаборация виски и крафтового IPA-пива\n"
            "• Выдержан в бочках из-под индийского светлого эля\n"
            "• Аромат: хмель, свежие травы, яблоко, груша\n"
            "• Вкус: ваниль, зелёные яблоки, цитрусы, хмелевая горчинка\n"
            "• Экспериментальный и освежающий профиль\n"
            "• Отлично подойдёт для пивных любителей, начинающих знакомство с виски\n"
            "• Крепость: 43 % ABV\n"
            "• Часть линейки Experimental Series от Glenfiddich\n"
            "• Ограниченное издание — подчеркивает креативность бренда\n"
            "• Идеален для дегустаций и обсуждений вкусов"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Grant's Classic", "Виски")
async def grants_classic(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG3Gg4nc5TGsJHjrEPyk-J7PNFHVvAAAIL9TEb1P3ISZjP54Yf2Z6PAQADAgADeQADNgQ",  # ← вставь свой file_id
        caption=(
            "<b>Grant’s Triple Wood (Classic)</b>\n"
            "• Классический купажированный шотландский виски\n"
            "• Выдержан в трёх типах бочек: бурбон, американский новый дуб, херес\n"
            "• Аромат: ваниль, карамель, яблоко, специи\n"
            "• Вкус: мягкий, с нотами ванили, дуба и пряностей\n"
            "• Финиш: длительный, гладкий, немного сладковатый\n"
            "• Крепость: 40 % ABV\n"
            "• Отличный выбор для коктейлей или чистого вида\n"
            "• Самый популярный вариант в линейке Grant’s\n"
            "• Идеален для повседневного употребления\n"
            "• Баланс цены и качества"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )


@track_brand("Grant's Summer Orange", "Виски")
async def grants_summer_orange(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG4mg4ndf9tfQikXAQPk-lIxaS4yMsAAIO9TEb1P3ISWY8m8SH7F44AQADAgADeQADNgQ",  # ← сюда вставь свой file_id
        caption=(
            "<b>Grant’s Summer Orange</b>\n"
            "• Купажированный шотландский виски с натуральным вкусом апельсина\n"
            "• Яркий, фруктовый и освежающий профиль\n"
            "• Аромат: цедра апельсина, ваниль, мёд\n"
            "• Вкус: сладкий апельсин, специи, лёгкая дубовая горчинка\n"
            "• Крепость: 35 % ABV — мягкий и лёгкий\n"
            "• Идеален со льдом, содовой или в коктейлях\n"
            "• Летняя лимитка, созданная для освежающих напитков\n"
            "• Отличный вариант для тех, кто не любит крепкий виски\n"
            "• Современный стиль, ориентированный на молодую аудиторию\n"
            "• Хорош для вечеринок, летних террас и лёгкого ужина"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Grant's Winter Dessert", "Виски")
async def grants_winter_dessert(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG3mg4ndDXJWAkbTrFKLhtgoVbFaDsAAIM9TEb1P3ISZq_Ca_jZFUSAQADAgADeQADNgQ",  # ← сюда вставь свой file_id
        caption=(
            "<b>Grant’s Winter Dessert</b>\n"
            "• Десертный купажированный виски с акцентом на тёплые, зимние ноты\n"
            "• Аромат: сливочная карамель, глинтвейн, печёные яблоки\n"
            "• Вкус: ваниль, тёмный шоколад, пряности, корица\n"
            "• Мягкий, согревающий характер\n"
            "• Крепость: 35 % ABV — деликатный и уютный\n"
            "• Идеален с тёплым яблочным соком или в десертных коктейлях\n"
            "• Отлично сочетается с выпечкой и шоколадом\n"
            "• Лимитированный выпуск на холодный сезон\n"
            "• Подходит для подарков и уютных зимних вечеров\n"
            "• Яркий пример вкусового виски без лишней крепости"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Grant's Tropical Fiesta", "Виски")
async def grants_tropical_fiesta(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG4Gg4ndPl6Fi0nM3zF9P8Va09iX6LAAIN9TEb1P3ISQ2wk7vc2-toAQADAgADeQADNgQ",  # ← сюда вставь свой file_id
        caption=(
            "<b>Grant’s Tropical Fiesta</b>\n"
            "• Лимитированная версия виски с тропическим характером\n"
            "• Аромат: ананас, манго, кокос, сладкие специи\n"
            "• Вкус: лёгкий, фруктовый, с нотами ванили и карамели\n"
            "• Основа — классический Grant’s с добавлением натуральных ароматов\n"
            "• Крепость: 35 % ABV — мягкий и лёгкий для пития\n"
            "• Отличен в охлаждённом виде или с соком\n"
            "• Подходит для летних коктейлей и вечеринок\n"
            "• Стильная бутылка с ярким тропическим дизайном\n"
            "• Отличный выбор для любителей мягкого виски\n"
            "• Создан для новых поколений потребителей"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Tullamore D.E.W.", "Виски")
async def tullamore_dew(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG5Gg4npCx1IL5QMiN-XatPLCICdo1AALG8jEbPObJSSzMH93C0bHVAQADAgADeQADNgQ",  # ← сюда вставь свой file_id
        caption=(
            "<b>Tullamore D.E.W.</b>\n"
            "• Ирландский трипл-бленд виски (солод + зерно + пот-стилл)\n"
            "• Аромат: зелёное яблоко, ваниль, сливки\n"
            "• Вкус: мягкий, слегка сладковатый, с фруктовыми и древесными нотами\n"
            "• Выдержан в бочках из-под бурбона и хереса\n"
            "• Крепость: 40 % ABV\n"
            "• Один из самых узнаваемых ирландских виски в мире\n"
            "• Идеален для начинающих и коктейлей\n"
            "• История бренда с 1829 года (г. Талламор, Ирландия)\n"
            "• Название D.E.W. — инициалы первого владельца: Daniel E. Williams\n"
            "• Слоган: ‘Give every man his D.E.W.’"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )

@track_brand("Tullamore D.E.W. Honey", "Виски")
async def tullamore_honey(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG_2g4qxyZA7ZsneXEwpn9IZwP00efAAJn9TEb1P3ISSXBLkMW4PngAQADAgADeAADNgQ",  # ← сюда вставь свой file_id
        caption=(
            "<b>Tullamore D.E.W. Honey</b>\n"
            "• Ирландский виски ликёр на основе оригинального Tullamore D.E.W.\n"
            "• Настоян на натуральном мёде\n"
            "• Аромат: цветочный, мёд, ваниль, немного трав\n"
            "• Вкус: сладкий, сливочный, мягкий — с нотами виски и мёда\n"
            "• Крепость: 35 % ABV\n"
            "• Подаётся охлаждённым или со льдом\n"
            "• Идеален для шотов и коктейлей\n"
            "• Новинка для любителей мягких вкусов\n"
            "• Стильная бутылка с тиснением\n"
            "• Отличный выбор для женской аудитории и новичков"
        ),
        reply_markup=get_whisky_kb(),
        parse_mode="HTML"
    )



vodka_router = Router()

@vodka_router.message(F.text == "🧊 Водка")
async def vodka_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("🧊 Выбери бренд водки:", reply_markup=get_vodka_kb())

@vodka_router.message(F.text == "Назад к категориям")
async def vodka_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Категории", reply_markup=BRAND_MENU_KB)

@track_brand("Серебрянка", "Водка")
async def srebryanka(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIK-Gg8CRgDjmxfkUP-Ui86uo8Lm4OSAAJS9zEbPHPgSVUkEXccwFmIAQADAgADeQADNgQ",
        caption=(
            "<b>Серебрянка</b>\n"
            "• Казахстанская водка\n"
            "• Отличается мягким вкусом и чистым послевкусием\n"
            "• Фильтрация через серебро — отсюда и название\n"
            "• Прекрасно подходит для классических застолий\n"
            "• Крепость: 40 %\n"
            "• Форматы: 0.5 и 0.7 л\n"
            "• Представлена в трёх вариантах: Классическая, Лайт (37,5%) и Rey\n"
            "• Идеальна в паре с солёными закусками и мясом"
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )

@track_brand("Reyka", "Водка")
async def reyka(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILCWg8EVlyH6R2QScf7Q4nZzXoKgw4AAKG9zEbPHPgSUK7bfwT0QdLAQADAgADbQADNgQ",  
        caption=(
            "<b>Reyka</b>\n"
            "• Премиальная водка из Исландии\n"
            "• Изготавливается из чистейшей родниковой воды\n"
            "• Перегоняется в медных аламбиках Carter-Head\n"
            "• Фильтруется через лаву вулкана\n"
            "• Аромат: мягкий, чистый, с намёком на минералы\n"
            "• Вкус: гладкий, с лёгкой сладостью и нотками перца\n"
            "• Крепость: 40 % ABV\n"
            "• Прекрасно подходит для чистого употребления и коктейлей\n"
            "• Часто ассоциируется с экологичностью и натуральностью"
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )
    
@track_brand("Finlandia", "Водка")
async def finlandia(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILC2g8Eli-TYUT9EM8fzglAi5soVNhAAKJ9zEbPHPgSekXdAio1hxGAQADAgADeQADNgQ",
        caption=(
            "<b>Finlandia</b>\n"
            "• Всемирно известная водка из Финляндии\n"
            "• Производится из шести рядного ячменя и чистейшей ледниковой воды\n"
            "• Перегоняется более 200 раз для исключительной чистоты\n"
            "• Аромат: нейтральный, слегка злаковый\n"
            "• Вкус: гладкий, холодный, мягкий\n"
            "• Крепость: 40 % ABV\n"
            "• Идеальна в шотах, коктейлях или с лёгкой закуской\n"
            "• Символ северной чистоты и минимализма\n"
            "• Доступна в разных вариантах: Classic, Lime, Grapefruit и др."
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )

@track_brand("Зелёная марка", "Водка")
async def zelenaya_marka(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILB2g8EThJMJe1UMamIxOOc_dAAnWJAAKD9zEbPHPgSRx1MKEz6FkVAQADAgADeAADNgQ",  
        caption=(
            "<b>Зелёная марка</b>\n"
            "• Традиционная российская водка\n"
            "• Производится с использованием ржаного спирта и родниковой воды\n"
            "• Сбалансированный вкус с лёгкой зерновой нотой\n"
            "• Аромат: мягкий, хлебный\n"
            "• Крепость: 40 % ABV\n"
            "• Идеально подходит для классических застолий\n"
            "• Линейка включает: Классическая, Пшеничная, Сибирская, Особая и др.\n"
            "• Упаковка оформлена в винтажном стиле — отсылка к традициям\n"
            "• Одна из самых узнаваемых марок в РФ и СНГ"
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )


@track_brand("Талка", "Водка")
async def talka(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILDWg8EwSC0zkdPOWDiuPJwDjZnD6-AAKO9zEbPHPgSVVZcdKwdwxDAQADAgADeQADNgQ",
        caption=(
            "<b>Талка</b>\n"
            "• Натуральная водка из Сибири\n"
            "• Производится из талой воды и спирта класса «Люкс»\n"
            "• Аромат: нейтральный, лёгкий\n"
            "• Вкус: мягкий, чистый, с коротким финишем\n"
            "• Крепость: 40 % ABV\n"
            "• Природная тематика подчёркивается снежным дизайном бутылки\n"
            "• Подходит для подачи в чистом виде и для настоек\n"
            "• Часто выбирается потребителями за натуральность и мягкость"
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )

@track_brand("Русский Стандарт", "Водка")
async def russkiy_standart(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILD2g8EzK_RPkeZPk2_gPWpB5xh_4CAAKP9zEbPHPgSWZgm1smh6zxAQADAgADeQADNgQ", 
        caption=(
            "<b>Русский Стандарт</b>\n"
            "• Один из самых узнаваемых российских брендов водки\n"
            "• Производится в Санкт-Петербурге по рецепту Менделеева\n"
            "• Используется озёрная вода Ладоги и спирт «Люкс»\n"
            "• Аромат: чистый, слегка зерновой\n"
            "• Вкус: сбалансированный, мягкий, с легкой маслянистостью\n"
            "• Крепость: 40 % ABV\n"
            "• Часто подаётся охлаждённой к русской кухне\n"
            "• Идеальна как в чистом виде, так и в коктейлях"
        ),
        reply_markup=get_vodka_kb(),
        parse_mode="HTML"
    )

beer_router = Router()

@beer_router.message(F.text == "🍺 Пиво")
async def beer_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("🍺 Выбери бренд пива:", reply_markup=get_beer_kb())

@beer_router.message(F.text == "Назад к категориям")
async def beer_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Категории", reply_markup=BRAND_MENU_KB)

@track_brand("Paulaner", "Пиво")
async def paulaner(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILKmg8FzKSP73SszDZhdcxRRRWag1hAAKl9zEbPHPgSSyVatusTBp3AQADAgADeQADNgQ",
        caption=(
            "<b>Paulaner</b>\n"
            "• Знаменитое немецкое пиво с историей более 400 лет\n"
            "• Производится в Мюнхене, Германия\n"
            "• Популярные стили: Hefe-Weißbier, Münchner Hell, Oktoberfest Bier\n"
            "• Вкус: насыщенный, с нотками банана, гвоздики, солода\n"
            "• Отличается мягкостью и натуральным брожением\n"
            "• Отлично сочетается с колбасками, курицей и сыром\n"
            "• Поставляется в бутылках и кегах\n"
            "• Один из официальных участников Октоберфеста"
        )
    )    

@track_brand("Blue Moon", "Пиво")
async def blue_moon(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILOGg8GB7izbq1UzrpiNATph1gsPAGAAKv9zEbPHPgSYK1lfCxnUKEAQADAgADeAADNgQ",
        caption=(
            "<b>Blue Moon</b>\n"
            "• Американское пшеничное пиво в бельгийском стиле\n"
            "• Варится с добавлением апельсиновой цедры\n"
            "• Аромат: цитрусовый, пряный, с нотами кориандра\n"
            "• Вкус: освежающий, слегка сладковатый, мягкий\n"
            "• Алкоголь: 5.4 % ABV\n"
            "• Подаётся традиционно с долькой апельсина\n"
            "• Идеально для жаркой погоды и лёгких блюд\n"
            "• Стильная бутылка с лунным логотипом\n"
            "• Отлично заходит тем, кто не любит горечь IPA"
        ),
        reply_markup=get_beer_kb(),
        parse_mode="HTML"
    )
@track_brand("London Pride", "Пиво")
async def london_pride(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILOmg8GJPTpk3KYW-eQheQ_ptxulNjAAK09zEbPHPgSel9dYZxhnk8AQADAgADeAADNgQ",
        caption=(
            "<b>London Pride</b>\n"
            "• Знаменитый английский эль от пивоварни Fuller’s\n"
            "• Стиль: классический британский Bitter\n"
            "• Аромат: карамель, орех, лёгкая хмелевая нота\n"
            "• Вкус: сбалансированный, с мягкой горчинкой и солодовым телом\n"
            "• Алкоголь: 4.7 % ABV\n"
            "• Отлично сочетается с мясными и жареными блюдами\n"
            "• Фирменная бутылка с красным лейблом\n"
            "• Один из самых узнаваемых элей Великобритании\n"
            "• Истинный вкус лондонских пабов"
        ),
        reply_markup=get_beer_kb(),
        parse_mode="HTML"
    )

@track_brand("Coors", "Пиво")
async def coors(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILPGg8GOm6MQNr5kSeEHSivJDvs3fGAAK39zEbPHPgST-l5QL573P0AQADAgADeQADNgQ",
        caption=(
            "<b>Coors</b>\n"
            "• Легендарное американское светлое пиво\n"
            "• Стиль: American Lager\n"
            "• Аромат: лёгкий, с нотками кукурузы и хмеля\n"
            "• Вкус: освежающий, мягкий, нейтральный\n"
            "• Алкоголь: 4.2 % ABV\n"
            "• Отлично пьётся охлаждённым в жаркую погоду\n"
            "• Характерный серебристый дизайн банки\n"
            "• Часто используется в массовых и спортивных мероприятиях\n"
            "• Один из крупнейших брендов пива в США"
        ),
        reply_markup=get_beer_kb(),
        parse_mode="HTML"
    )

@track_brand("Staropramen", "Пиво")
async def staropramen(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILPmg8GS-vTMPmpwqAdJaQn_-TcBnYAAK59zEbPHPgSYKtiAbkwYS3AQADAgADeAADNgQ",
        caption=(
            "<b>Staropramen</b>\n"
            "• Чешское пиво с богатой историей с 1869 года\n"
            "• Стиль: Czech Pilsner / Lager\n"
            "• Аромат: солодовый, с оттенками хмеля\n"
            "• Вкус: чистый, сбалансированный, слегка горьковатый\n"
            "• Алкоголь: 5.0 % ABV\n"
            "• Отличается насыщенным телом и классическим чешским характером\n"
            "• Производится в Праге, экспортируется по всему миру\n"
            "• Идеален к мясным блюдам и сытным закускам\n"
            "• Один из символов чешской пивной культуры"
        ),
        reply_markup=get_beer_kb(),
        parse_mode="HTML"
    )



wine_router = Router()

@wine_router.message(F.text == "🍷 Вино")
async def wine_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("🍷 Выбери вино:", reply_markup=get_wine_kb())

@wine_router.message(F.text == "Назад к категориям")
async def wine_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Категории", reply_markup=BRAND_MENU_KB)

@track_brand("Mateus Original Rosé", "Вино")
async def mateus_rose(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILUGg8Gx2S1sAohmNgv870lc1VvUdaAALC9zEbPHPgSZwxOkkyUzl2AQADAgADeQADNgQ",
        caption=(
            "<b>Mateus Original Rosé</b>\n"
            "• Лёгкое полусухое розовое вино из Португалии\n"
            "• Сорт винограда: Baga и другие португальские автохтоны\n"
            "• Цвет: светло-розовый, с лёгким блеском\n"
            "• Аромат: клубника, малина, цветочные тона\n"
            "• Вкус: свежий, фруктовый, сбалансированный\n"
            "• Крепость: 11 % ABV\n"
            "• Подача: охлаждённым, идеально летом\n"
            "• Подходит к лёгким закускам, салатам и морепродуктам\n"
            "• Узнаваемая пузатая бутылка — символ бренда\n"
            "• Отличный выбор для новичков и лёгких вечеринок"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )

@track_brand("Undurraga Sauvignon Blanc", "Вино")
async def undurraga_sb(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILVmg8HAghUtu6l0-rE7dGF0PLdzGYAALU9zEbPHPgSduFfYYWlxmOAQADAgADeQADNgQ",
        caption=(
            "<b>Undurraga Sauvignon Blanc</b>\n"
            "• Белое сухое вино из Чили\n"
            "• Виноград: Совиньон Блан\n"
            "• Цвет: светло-соломенный\n"
            "• Аромат: цитрус, зелёное яблоко, свежая трава\n"
            "• Вкус: свежий, сухой, с яркой кислотностью\n"
            "• Крепость: 12.5 % ABV\n"
            "• Отлично сочетается с морепродуктами и салатами\n"
            "• Подача при 8–10 °C\n"
            "• Современный стиль нового света\n"
            "• Надёжный выбор по доступной цене"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )

@track_brand("Devil’s Rock Riesling", "Вино")
async def devils_rock_riesling(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILXmg8HL0ZOUJYurNUmx1RK7xZYadHAALc9zEbPHPgSdjIeJJeBYRdAQADAgADeQADNgQ",
        caption=(
            "<b>Devil’s Rock Riesling</b>\n"
            "• Белое сухое вино из Германии\n"
            "• Сорт винограда: Riesling\n"
            "• Цвет: светло-золотистый с зелёными бликами\n"
            "• Аромат: яблоко, персик, цитрус, мёд\n"
            "• Вкус: сухой, освежающий, хорошо сбалансированный\n"
            "• Крепость: 10.5 % ABV\n"
            "• Отличный выбор для лёгкой кухни и азиатских блюд\n"
            "• Подаётся охлаждённым до 8–10 °C\n"
            "• Современный стиль немецкого рислинга\n"
            "• Упаковка с запоминающимся дизайном и «дьявольским» характером"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )

@track_brand("Piccola Nostra", "Вино")
async def piccola_nostra(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILXGg8HLGVozwsE57zvCpYkQn_IDiaAALb9zEbPHPgSZzW-CvfBN3OAQADAgADeQADNgQ",
        caption=(
            "<b>Piccola Nostra</b>\n"
            "• Итальянское полусладкое вино\n"
            "• Лёгкое, фруктовое, с мягким сладким послевкусием\n"
            "• Цвет: от соломенного до янтарного (в зависимости от вида)\n"
            "• Аромат: груша, персик, цветы\n"
            "• Крепость: 9–10 % ABV\n"
            "• Отлично сочетается с десертами и лёгкими блюдами\n"
            "• Подходит для ежедневного употребления\n"
            "• Часто выбирается за сбалансированную сладость\n"
            "• Привлекательная цена и доступность\n"
            "• Подходит для тёплых вечеров и романтических встреч"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )

@track_brand("Эль Санчес", "Вино")
async def el_sanches(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILWGg8HJ5SEDUTg8UUswi8qdBrKBdsAALZ9zEbPHPgScB4ihQKmAVmAQADAgADeQADNgQ",
        caption=(
            "<b>Эль Санчес</b>\n"
            "• Полусладкое красное вино из Испании\n"
            "• Изготовлено из винограда Гренаш и Темпранильо\n"
            "• Цвет: насыщенный рубиновый\n"
            "• Аромат: вишня, слива, ваниль\n"
            "• Вкус: мягкий, слегка пряный, сладковатый\n"
            "• Крепость: 10.5–11.5 % ABV\n"
            "• Идеально с мясом на гриле и закусками\n"
            "• Приятное вино на каждый день\n"
            "• Подходит как для застолий, так и для ужина на двоих\n"
            "• Популярно за доступную цену и дружелюбный вкус"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )

@track_brand("Шале де Сюд", "Вино")
async def chale_de_sud(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILWmg8HKjtY9IaTW5OgLBx1LZ4NbU2AALa9zEbPHPgSfWt245fgG4PAQADAgADeAADNgQ",
        caption=(
            "<b>Шале де Сюд</b>\n"
            "• Французское полусладкое вино\n"
            "• Цвет: от светло-розового до золотистого\n"
            "• Аромат: клубника, мед, яблоко\n"
            "• Вкус: лёгкий, фруктовый, с мягкой сладостью\n"
            "• Крепость: около 10 % ABV\n"
            "• Подаётся охлаждённым\n"
            "• Универсально для салатов, десертов, лёгких закусок\n"
            "• Часто ассоциируется с летними вечеринками\n"
            "• Привлекательный внешний вид бутылки\n"
            "• Хороший выбор для новичков и поклонников сладких вин"
        ),
        reply_markup=get_wine_kb(),
        parse_mode="HTML"
    )
    
jager_router = Router()

@jager_router.message(F.text == "🦌 Ягермейстер")
async def jager_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Выберите бренд ликёра:", reply_markup=get_jager_kb())

@jager_router.message(F.text == "Назад к категориям")
async def jager_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Категории", reply_markup=BRAND_MENU_KB)

@jager_router.message(F.text == "Jägermeister")
@track_brand("Jägermeister", "Ликёр")
async def jagermeister_info(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIMG2g8Lf1fleLtxA30kh_bN-YFxQx9AAKM-DEbPHPgSXiVPEBRiD1GAQADAgADeAADNgQ",
        caption=(
            "<b>Jägermeister</b>\n"
            "• Немецкий травяной ликёр с крепостью 35 %\n"
            "• Производится с 1935 года в Вольфенбюттеле\n"
            "• Состоит из 56 трав, корней и специй\n"
            "• Настойка выдерживается 12 месяцев в дубовых бочках\n"
            "• Аромат: пряный, травяной, с нотами аниса и цитруса\n"
            "• Вкус: насыщенный, горьковатый, слегка сладкий\n"
            "• Классическая подача — шот, охлаждённый до -18°C\n"
            "• Отличный ингредиент для коктейлей (Jägerbomb и др.)\n"
            "• Логотип — олень с сияющим крестом между рогами"
        ),
        reply_markup=get_jager_kb(),
        parse_mode="HTML"
    )




search_router = Router()
SEARCH_ACTIVE: set[int] = set()

BRANDS: dict[str, tuple[callable, list[str]]] = {
    "Monkey Shoulder": (monkey_shoulder, [
        "monkey shoulder", "monkey", "mon", "манки", "монки", "манкей", "манки шолдер"
    ]),
    "Glenfiddich 12 Years": (glenfiddich_12, [
        "glenfiddich 12", "glen", "гленфиддик 12", "глен", "glenfiddich"
    ]),
    "Glenfiddich Fire & Cane": (fire_and_cane, [
        "glenfiddich fire & cane", "fire & cane", "fire and cane", "фаер кейн", "fire cane", "гленфиддик фаер", "фаер"
    ]),
    "Glenfiddich IPA": (ipa_experiment, [
        "glenfiddich ipa", "ipa experiment", "ipa", "эксперимент", "ипа"
    ]),
    "Grant's Classic": (grants_classic, [
        "grant's classic", "grants classic", "грантс классик", "грантс"
    ]),
    "Grant's Summer Orange": (grants_summer_orange, [
        "grant's summer orange", "summer orange", "грантс саммер", "грантс апельсин"
    ]),
    "Grant's Winter Dessert": (grants_winter_dessert, [
        "grant's winter dessert", "winter dessert", "грантс десерт"
    ]),
    "Grant's Tropical Fiesta": (grants_tropical_fiesta, [
        "grant's tropical fiesta", "tropical fiesta", "грантс тропик", "грантс фиеста"
    ]),
    "Tullamore D.E.W.": (tullamore_dew, [
        "tullamore d.e.w.", "tullamore", "тулламор", "тулламор дью"
    ]),
    "Tullamore D.E.W. Honey": (tullamore_honey, [
        "tullamore d.e.w. honey", "tullamore honey", "тулламор хани", "тулламор мед"
    ]),
    "Серебрянка": (srebryanka, [
        "серебрянка", "serebryanka", "серебро"
    ]),
    "Reyka": (reyka, [
        "reyka", "рейка"
    ]),
    "Finlandia": (finlandia, [
        "finlandia", "финляндия", "финлянд"
    ]),
    "Зелёная марка": (zelenaya_marka, [
        "зелёная марка", "зеленая марка", "zelenaya marka"
    ]),
    "Талка": (talka, [
        "талка", "talka"
    ]),
    "Русский Стандарт": (russkiy_standart, [
        "русский стандарт", "russkiy standart"
    ]),
    "Paulaner": (paulaner, [
        "paulaner", "пауланер"
    ]),
    "Blue Moon": (blue_moon, [
        "blue moon", "блю мун"
    ]),
    "London Pride": (london_pride, [
        "london pride", "лондон прайд"
    ]),
    "Coors": (coors, [
        "coors", "курс"
    ]),
    "Staropramen": (staropramen, [
        "staropramen", "старопрамен"
    ]),
    "Mateus Original Rosé": (mateus_rose, [
        "mateus original rose", "mateus rose", "матеус", "матеуш"
    ]),
    "Undurraga Sauvignon Blanc": (undurraga_sb, [
        "undurraga sauvignon blanc", "undurraga", "ундарага", "совиньон блан"
    ]),
    "Devil’s Rock Riesling": (devils_rock_riesling, [
        "devil's rock riesling", "devils rock", "дэвилс рок", "рислинг"
    ]),
    "Piccola Nostra": (piccola_nostra, [
        "piccola nostra", "пиккола ностра"
    ]),
    "Эль Санчес": (el_sanches, [
        "эль санчес", "el sanches", "санчес"
    ]),
    "Шале де Сюд": (chale_de_sud, [
        "шале де сюд", "chalet des sud", "шале"
    ]),
    "Jägermeister": (jagermeister_info, [
        "jagermeister", "ягермейстер", "ягер", "jager"
    ]),
}
# Map normalized brand aliases to canonical names
ALIAS_MAP: dict[str, str] = {}
for _name, (_, _aliases) in BRANDS.items():
    ALIAS_MAP[normalize(_name)] = _name
    for _a in _aliases:
        ALIAS_MAP[normalize(_a)] = _name

brand_lookup_router = Router()

@brand_lookup_router.message(
    lambda m: (
        m.from_user.id not in USER_STATE
        and m.from_user.id not in GAME_STATE
        and m.from_user.id not in ASSOC_STATE
        and m.from_user.id not in BLITZ_STATE
        and normalize(m.text) in ALIAS_MAP
    )
)
async def show_brand(m: Message):
    """Send brand card regardless of how the button was created."""
    clear_user_state(m.from_user.id)
    canonical = ALIAS_MAP[normalize(m.text)]
    handler, _ = BRANDS[canonical]
    await handler(m)

# Router to suggest brands when user enters a partial name
suggest_router = Router()

def _has_partial_match(m: Message) -> bool:
    if (
        m.from_user.id in SEARCH_ACTIVE
        or m.from_user.id in USER_STATE
        or m.from_user.id in GAME_STATE
        or m.from_user.id in ASSOC_STATE
        or m.from_user.id in BLITZ_STATE
    ):
        return False
    if not m.text:
        return False
    normalized = normalize(m.text)
    # Skip if exact match for existing alias
    if normalized in ALIAS_MAP:
        return False
    for brand, (_, aliases) in BRANDS.items():
        for alias in aliases + [brand]:
            if normalized in normalize(alias):
                return True
    return False


@suggest_router.message(_has_partial_match)
async def suggest_brands(m: Message):
    normalized = normalize(m.text)
    matches: list[str] = []
    for brand, (_, aliases) in BRANDS.items():
        for alias in aliases + [brand]:
            if normalized in normalize(alias):
                matches.append(brand)
                break
    if not matches:
        return
    matches = list(dict.fromkeys(matches))
    builder = ReplyKeyboardBuilder()
    for brand in matches:
        builder.add(KeyboardButton(text=brand))
    builder.adjust(1)
    await m.answer("Возможно, вы имели в виду:", reply_markup=builder.as_markup(resize_keyboard=True))


# Map canonical brand names in lowercase for exact-match check
CANONICAL_MAP = {name.lower(): name for name in BRANDS}

@search_router.message(F.text == "🔍 Поиск")
async def search_start(m: Message):
    SEARCH_ACTIVE.add(m.from_user.id)
    await m.answer(
        "Введите часть названия бренда (например: глен, glen, грант, пауланер):",
        reply_markup=ReplyKeyboardRemove(),
    )


@search_router.message(
    lambda m: m.from_user.id in SEARCH_ACTIVE
    and normalize(m.text) not in ALIAS_MAP
)
async def process_search(m: Message):
    text = m.text.strip()
    normalized = normalize(text)

    if normalized in {"отмена", "назад"}:
        SEARCH_ACTIVE.discard(m.from_user.id)
        await m.answer("Поиск отменён", reply_markup=main_kb(m.from_user.id))
        return


    # Ищем все бренды, где есть совпадение
    matches: list[str] = []
    for brand_name, (_, aliases) in BRANDS.items():
        for alias in aliases + [brand_name]:
            if normalized in normalize(alias):
                matches.append(brand_name)
                break

    # Убираем дубликаты
    matches = list(dict.fromkeys(matches))

    if not matches:
        await m.answer("Ничего не найдено. Попробуйте ещё раз или нажмите Отмена.")
        return

    builder = ReplyKeyboardBuilder()
    for brand in matches:
        builder.add(KeyboardButton(text=brand))
    builder.add(KeyboardButton(text="Отмена"))
    builder.adjust(1)
    await m.answer("Выберите бренд:", reply_markup=builder.as_markup(resize_keyboard=True))
from random import shuffle, sample

tests_router = Router()
game_router = Router()

TESTS_MENU_KB = kb(
    "Тест: Jägermeister", "Тест: Виски", "Тест: Водка",
    "Тест: Пиво", "Тест: Вино", "Назад к меню", width=2
)


QUESTIONS = {
    "jager": {
        1: ("Сколько трав входит в состав Jägermeister?", ["56", "27", "12", "🤫 Секрет"], "56"),
        2: ("Из какой страны Jägermeister?", ["Германия", "Австрия", "Швейцария", "Польша"], "Германия"),
        3: ("Какой цвет имеет Jägermeister?", ["Тёмно-коричневый", "Прозрачный", "Золотистый", "Красный"], "Тёмно-коричневый"),
        4: ("Как правильно подавать Jägermeister?", ["Охлаждённым", "Тёплым", "С лимоном", "С содовой"], "Охлаждённым"),
        5: ("Крепость Jägermeister?", ["35%", "40%", "38%", "30%"], "35%"),
        6: ("Что изображено на логотипе Jägermeister?", ["Олень с крестом", "Медведь", "Трава", "Волк"], "Олень с крестом"),
        7: ("Где чаще всего используют Jägermeister?", ["Шоты", "Вино", "Пиво", "Пюре"], "Шоты"),
        8: ("Один из вкусов Jägermeister:", ["Горький, травяной", "Карамельный", "Цитрусовый", "Медовый"], "Горький, травяной"),
        9: ("Как долго настаивается Jägermeister?", ["12 мес.", "6 мес.", "2 недели", "1 год"], "12 мес."),
        10: ("Какая подача Jägermeister считается классической?", ["Замороженный шот", "Со льдом", "С тоником", "С пивом"], "Замороженный шот")
    },
    "whisky": {
        1: ("Какие солодовые виски входят в Monkey Shoulder?", ["Glenfiddich, Balvenie, Kininvie", "Tullamore, Glen Grant", "Jack Daniel’s, Glenkinchie"], "Glenfiddich, Balvenie, Kininvie"),
        2: ("Где производится Glenfiddich 12?", ["Спейсайд", "Айла", "Кэмпбелтаун"], "Спейсайд"),
        3: ("Вкус Grant's Summer Orange:", ["Апельсиновый ликёр", "Мёд", "Карамель"], "Апельсиновый ликёр"),
        4: ("Аромат Tullamore Honey:", ["Мёд, ваниль, цветы", "Торф", "Кофе, шоколад"], "Мёд, ваниль, цветы"),
        5: ("Крепость Jack Daniel’s Honey:", ["35%", "40%", "43%"], "35%"),
        6: ("Вкус Aerstone Sea Cask:", ["Морской солоноватый", "Карамель", "Фруктовый"], "Морской солоноватый"),
        7: ("Сколько лет выдержка Glenfiddich 12?", ["12", "10", "14"], "12"),
        8: ("Grant’s Tropical Fiesta — это:", ["Тропический фруктовый вкус", "Торф", "Имбирь"], "Тропический фруктовый вкус"),
        9: ("Производитель Tullamore D.E.W.:", ["Ирландия", "Шотландия", "США"], "Ирландия"),
        10: ("Monkey Shoulder лучше всего для:", ["Коктейлей", "Чистого пития", "Фляг"], "Коктейлей")
    },
    "vodka": {
        1: ("Страна происхождения Reyka:", ["Исландия", "Россия", "Казахстан"], "Исландия"),
        2: ("Фильтрация Серебрянки:", ["Через серебро", "Через уголь", "Без фильтрации"], "Через серебро"),
        3: ("Форматы выпуска Серебрянки:", ["0.5 и 0.7 л", "1.0 л", "Только 0.5 л"], "0.5 и 0.7 л"),
        4: ("Особенность Finlandia:", ["Ледниковая вода", "Цитрус", "Травы"], "Ледниковая вода"),
        5: ("Вкус Reyka:", ["Гладкий, слегка сладкий", "Горький", "Кислый"], "Гладкий, слегка сладкий"),
        6: ("Крепость большинства водок:", ["40%", "35%", "45%"], "40%"),
        7: ("Зелёная марка — это:", ["Российская классическая водка", "Американская", "Финская"], "Российская классическая водка"),
        8: ("Что делает Талка особенной?", ["Талая вода", "Фрукты", "Травы"], "Талая вода"),
        9: ("Происхождение Русский Стандарт:", ["Санкт-Петербург", "Москва", "Новосибирск"], "Санкт-Петербург"),
        10: ("Рекомендуется подавать водку:", ["Охлаждённой", "Тёплой", "С лимоном"], "Охлаждённой")
     },
    "beer": {
        1: ("Какой стиль у Paulaner Weissbier?", ["Пшеничное нефильтрованное", "Лагер", "Портер", "Стаут"], "Пшеничное нефильтрованное"),
        2: ("Откуда родом Paulaner?", ["Германия", "Бельгия", "США", "Чехия"], "Германия"),
        3: ("Особенность вкуса Blue Moon:", ["Цедра апельсина и кориандр", "Горький хмель", "Шоколад", "Мёд"], "Цедра апельсина и кориандр"),
        4: ("Страна происхождения London Pride:", ["Англия", "Шотландия", "Ирландия", "США"], "Англия"),
        5: ("Стиль Coors Light:", ["Лёгкий лагер", "IPA", "Портер", "Сидр"], "Лёгкий лагер"),
        6: ("Какой стиль у Staropramen?", ["Чешский лагер", "Бельгийский эль", "Стаут", "Кислое пиво"], "Чешский лагер"),
        7: ("Paulaner хорошо сочетается с:", ["Колбасками и мягким сыром", "Суши", "Десертами", "Молочными коктейлями"], "Колбасками и мягким сыром"),
        8: ("Как подавать Blue Moon?", ["С долькой апельсина", "С лаймом", "С мятой", "Без ничего"], "С долькой апельсина"),
        9: ("Где производится Coors?", ["США", "Канада", "Англия", "Франция"], "США"),
        10: ("Staropramen — это пиво из:", ["Чехии", "Германии", "Италии", "Испании"], "Чехии")
    },
    "wine": {
        1: ("Mateus Original Rosé — это:", ["Португальское розовое полусухое", "Красное сухое", "Игристое", "Белое сладкое"], "Португальское розовое полусухое"),
        2: ("Undurraga Sauvignon Blanc — страна:", ["Чили", "Аргентина", "Франция", "Португалия"], "Чили"),
        3: ("Devil’s Rock Riesling — стиль вина:", ["Белое сухое", "Красное сухое", "Розовое сухое", "Игристое"], "Белое сухое"),
        4: ("Piccola Nostra — это вино:", ["Итальянское полусладкое", "Французское сухое", "Испанское игристое", "Немецкое белое"], "Итальянское полусладкое"),
        5: ("El Sanchez — это:", ["Испанское полусладкое", "Французское игристое", "Чилийское сухое", "Португальское красное"], "Испанское полусладкое"),
        6: ("Chalet des Sud — это:", ["Французское полусладкое", "Аргентинское красное", "Итальянское игристое", "Немецкое сладкое"], "Французское полусладкое"),
        7: ("К какому блюду подходит Mateus Rosé?", ["Салаты, лёгкие закуски", "Стейки", "Пицца", "Шоколад"], "Салаты, лёгкие закуски"),
        8: ("С чем хорошо сочетается Riesling?", ["Фрукты и морепродукты", "Бургеры", "Говядина", "Шашлык"], "Фрукты и морепродукты"),
        9: ("Типичный аромат Sauvignon Blanc:", ["Цитрус и трава", "Кофе", "Дуб", "Ваниль"], "Цитрус и трава"),
        10: ("El Sanchez подойдёт для:", ["Фруктовых закусок", "Жареного мяса", "Пельменей", "Пиццы"], "Фруктовых закусок")
        }
}

GAME_MENU_KB = kb(
    "🟢 Верю — не верю",
    "🔗 Ассоциации",
    "⚡️ Блиц",
    "📋 Тесты",
    "Назад к меню",
    width=1,
)

TRUTH_QUESTIONS: list[tuple[str, bool]] = [
    ("Monkey Shoulder — это односолодовый виски.", False),
    ("Glenfiddich переводится как \"Долина оленя\".", True),
    ("В составе Jägermeister — 56 трав и специй.", True),
    ("Jack Daniel’s производится только в штате Теннесси.", True),
    ("Grant’s — купажированный шотландский виски.", True),
    ("Водка Серебрянка производится в Казахстане.", True),
    ("Paulaner — это французское пиво.", False),
    ("Glenfiddich IPA выдерживается в бочках из-под пива.", True),
    ("Monkey Shoulder отлично подходит для коктейлей.", True),
    ("В Grant’s Summer Orange есть вкус апельсина.", True),
    ("Jack Daniel’s Tennessee Honey — это крепкий ром.", False),
    ("Jägermeister традиционно подают сильно охлаждённым.", True),
    ("Grant’s Tropical Fiesta — с нотами ананаса и манго.", True),
    ("Glenfiddich Fire & Cane имеет копчёный вкус.", True),
    ("Водка Серебрянка выпускается в пластиковых бутылках.", False),
    ("Paulaner — один из старейших мюнхенских пивоваров.", True),
    ("Jack Daniel’s используют только уголь из клёна для фильтрации.", True),
    ("В Monkey Shoulder сочетаются солоды Glenfiddich, Balvenie и Kininvie.", True),
    ("Jägermeister производится с 1887 года.", False),
    ("Grant’s выпускает только один вид виски.", False),
]

# (associations, correct brand)
ASSOCIATIONS: list[tuple[str, str]] = [
    ("Обезьяны, купаж, коктейли", "Monkey Shoulder"),
    ("56 трав, Германия, ликёр", "Jägermeister"),
    ("12 лет, олень, Спейсайд", "Glenfiddich 12 Years"),
    ("Виски, торф, карамель", "Glenfiddich Fire & Cane"),
    ("Виски, IPA, эксперимент", "Glenfiddich IPA"),
    ("Апельсин, летний, виски", "Grant's Summer Orange"),
    ("Мёд, Ирландия, ликёр", "Tullamore D.E.W. Honey"),
    ("Пшеничное, мюнхен, Германия", "Paulaner"),
    ("Американское, апельсин, кориандр", "Blue Moon"),
    ("Серебро, Казахстан, водка", "Серебрянка"),
    ("Исландия, лава, водка", "Reyka"),
    ("Немецкое, рислинг, белое", "Devil’s Rock Riesling"),
    ("Водка, ледниковая, Финляндия", "Finlandia"),
    ("Красное полусладкое, Испания, вино", "Эль Санчес"),
    ("Чешское, лагер, Прага", "Staropramen"),
]

BLITZ_QUESTIONS: list[tuple[str, list[str], str]] = [
    ("Monkey Shoulder — это купаж или односолодовый виски?",
     ["Купаж", "Односолодовый"], "Купаж"),
    ("В каком городе делают Paulaner?",
     ["Мюнхен", "Берлин", "Лондон", "Прага"], "Мюнхен"),
    ("Главный ингредиент для Jack Daniel’s Honey?",
     ["Виски", "Ром", "Джин", "Водка"], "Виски"),
    ("Какой бренд выпускает Summer Orange и Tropical Fiesta?",
     ["Grant’s", "Glenfiddich", "Jack Daniel’s", "Paulaner"], "Grant’s"),
    ("Страна происхождения Jägermeister?",
     ["Германия", "Ирландия", "США", "Россия"], "Германия"),
    ("Glenfiddich IPA — это виски, выдержанный в бочках из-под...",
     ["Пива", "Рома", "Вина", "Коньяка"], "Пива"),
    ("Серебрянка — это...",
     ["Водка", "Пиво", "Ликёр", "Виски"], "Водка"),
    ("Jack Daniel’s производится в...",
     ["Теннесси", "Кентукки", "Лондон", "Мюнхен"], "Теннесси"),
    ("В каком напитке 56 трав?",
     ["Jägermeister", "Grant’s", "Glenfiddich", "Paulaner"], "Jägermeister"),
    ("Какой бренд традиционно ассоциируется с Октоберфестом?",
     ["Paulaner", "Glenfiddich", "Jack Daniel’s", "Monkey Shoulder"], "Paulaner"),
    ("В каком году появился Jägermeister?",
     ["1934", "1890", "1950", "2000"], "1934"),
    ("Glenfiddich переводится как...",
     ["Долина оленя", "Лес виски", "Грант и сыновья", "Зеленая лужайка"], "Долина оленя"),
    ("В каком стиле выдержан Glenfiddich Fire & Cane?",
     ["Копченый с нотами рома", "Яблочный сидр", "Медовый", "Ваниль"], "Копченый с нотами рома"),
    ("Какой напиток производится в Казахстане?",
     ["Серебрянка", "Glenfiddich", "Jägermeister", "Jack Daniel’s"], "Серебрянка"),
    ("У какого бренда логотип с оленем?",
     ["Glenfiddich", "Jack Daniel’s", "Grant’s", "Monkey Shoulder"], "Glenfiddich"),
    ("Какой коктейль классически делают с Monkey Shoulder?",
     ["Old Fashioned", "Mojito", "Margarita", "Daiquiri"], "Old Fashioned"),
    ("Сколько сортов пива производит Paulaner?",
     ["Более 10", "Только 1", "3", "0"], "Более 10"),
    ("К какому классу относится Grant’s?",
     ["Купажированный шотландский виски", "Ром", "Бурбон", "Водка"], "Купажированный шотландский виски"),
    ("Какой цвет часто встречается на этикетках Jägermeister?",
     ["Зеленый", "Синий", "Желтый", "Красный"], "Зеленый"),
    ("В каком напитке есть вкус мёда?",
     ["Jack Daniel’s Honey", "Paulaner", "Grant’s", "Glenfiddich IPA"], "Jack Daniel’s Honey"),
    ("Какой бренд выпускает лимитированные вкусы Summer Orange и Tropical Fiesta?",
     ["Grant’s", "Monkey Shoulder", "Paulaner", "Jack Daniel’s"], "Grant’s"),
    ("Сколько трав входит в состав Jägermeister?",
     ["56", "12", "21", "7"], "56"),
    ("Какой виски выдерживают в бочках из-под IPA?",
     ["Glenfiddich", "Grant’s", "Monkey Shoulder", "Jack Daniel’s"], "Glenfiddich"),
    ("Какой бренд родом из Германии?",
     ["Paulaner", "Jack Daniel’s", "Glenfiddich", "Grant’s"], "Paulaner"),
    ("Как называется серия Grant’s с ярко выраженными фруктовыми нотами?",
     ["Tropical Fiesta", "Classic", "IPA", "Fire & Cane"], "Tropical Fiesta"),
    ("В каком бренде используется фильтрация через кленовый уголь?",
     ["Jack Daniel’s", "Glenfiddich", "Paulaner", "Jägermeister"], "Jack Daniel’s"),
    ("Что добавляют в Grant’s Summer Orange?",
     ["Апельсин", "Ваниль", "Мята", "Мед"], "Апельсин"),
    ("Какой бренд выпускает IPA Experiment?",
     ["Glenfiddich", "Grant’s", "Monkey Shoulder", "Paulaner"], "Glenfiddich"),
    ("Какой продукт производится методом тройной дистилляции?",
     ["Tullamore D.E.W.", "Paulaner", "Grant’s", "Glenfiddich"], "Tullamore D.E.W."),
    ("Какой бренд используют для коктейлей \"Whiskey Sour\"?",
     ["Monkey Shoulder", "Paulaner", "Jack Daniel’s", "Jägermeister"], "Monkey Shoulder"),
    ("Где находится родина Jack Daniel’s?",
     ["США", "Германия", "Шотландия", "Ирландия"], "США"),
    ("Какой из брендов НЕ относится к виски?",
     ["Paulaner", "Glenfiddich", "Grant’s", "Monkey Shoulder"], "Paulaner"),
    ("Какой бренд ассоциируется с фестивалем Октоберфест?",
     ["Paulaner", "Jack Daniel’s", "Glenfiddich", "Grant’s"], "Paulaner"),
    ("Какой напиток подают сильно охлаждённым?",
     ["Jägermeister", "Grant’s", "Paulaner", "Glenfiddich"], "Jägermeister"),
    ("Что изображено на этикетке Grant’s?",
     ["Треугольник", "Медведь", "Олень", "Корабль"], "Треугольник"),
    ("Какой бренд славится медовым вкусом?",
     ["Jack Daniel’s Honey", "Glenfiddich", "Paulaner", "Grant’s"], "Jack Daniel’s Honey"),
    ("Monkey Shoulder отлично подходит для...",
     ["Коктейлей", "Пива", "Ликёров", "Водки"], "Коктейлей"),
    ("Какой бренд выпускает Fire & Cane?",
     ["Glenfiddich", "Paulaner", "Grant’s", "Jack Daniel’s"], "Glenfiddich"),
    ("Серебрянка производится в...",
     ["Казахстане", "Германии", "США", "Шотландии"], "Казахстане"),
    ("Какой напиток делают из ячменя?",
     ["Виски", "Ром", "Пиво", "Джин"], "Виски"),
    ("Какой напиток крепче — Jägermeister или Grant’s?",
     ["Grant’s", "Jägermeister"], "Grant’s"),
    ("Какой бренд выпускает Irish Honey?",
     ["Tullamore D.E.W.", "Glenfiddich", "Paulaner", "Grant’s"], "Tullamore D.E.W."),
    ("Какой из брендов НЕ производится в Европе?",
     ["Jack Daniel’s", "Paulaner", "Glenfiddich", "Grant’s"], "Jack Daniel’s"),
    ("Какой бренд известен своим \"оленем\"?",
     ["Glenfiddich", "Monkey Shoulder", "Paulaner", "Jack Daniel’s"], "Glenfiddich"),
    ("Какой бренд делают из солода?",
     ["Glenfiddich", "Grant’s", "Paulaner", "Jack Daniel’s"], "Glenfiddich"),
    ("В каком продукте больше 50 трав?",
     ["Jägermeister", "Glenfiddich", "Grant’s", "Paulaner"], "Jägermeister"),
    ("Какой напиток бывает нефильтрованным?",
     ["Пиво", "Виски", "Водка", "Ликёр"], "Пиво"),
    ("Какой напиток делают на заводе в Мюнхене?",
     ["Paulaner", "Grant’s", "Glenfiddich", "Jack Daniel’s"], "Paulaner"),
    ("Какой бренд больше всего ассоциируется с вечеринками?",
     ["Jägermeister", "Glenfiddich", "Paulaner", "Grant’s"], "Jägermeister"),
    ("Какой напиток делают из картофеля?",
     ["Водка", "Виски", "Пиво", "Джин"], "Водка"),
]

USER_STATE: dict[int, dict] = {}
GAME_STATE: dict[int, dict] = {}
ASSOC_STATE: dict[int, dict] = {}
BLITZ_STATE: dict[int, dict] = {}
ADMIN_STATE: dict[int, dict] = {}

@tests_router.message(F.text == "📋 Тесты")
async def tests_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Выберите категорию:", reply_markup=TESTS_MENU_KB)

@tests_router.message(lambda m: m.text in [
    "Тест: Jägermeister", "Тест: Виски", "Тест: Водка",
    "Тест: Пиво", "Тест: Вино"
])
async def start_test(m: Message):
    name_map = {
        "Тест: Jägermeister": "jager",
        "Тест: Виски": "whisky",
        "Тест: Водка": "vodka",
        "Тест: Пиво": "beer",
        "Тест: Вино": "wine"
    }
    clear_user_state(m.from_user.id)
    name = name_map[m.text]
    USER_STATE[m.from_user.id] = {"name": name, "step": 1, "score": 0}
    await ask(m)


@tests_router.message(lambda m: m.text == "Назад к меню")
async def back_to_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Меню тренажёра", reply_markup=GAME_MENU_KB)

async def ask(m: Message):
    st = USER_STATE[m.from_user.id]
    qset = QUESTIONS[st["name"]]
    step = st["step"]

    if step > len(qset):
        score = st['score']
        total = len(qset)
        if score <= 3:
            remark = "😕 Нужно подтянуть знания"
        elif 4 <= score <= 6:
            remark = "🙂 Уже неплохо!"
        elif 7 <= score <= 9:
            remark = "👍 Отличный результат!"
        else:
            remark = "🏆 Ты — эксперт!"
        record_test_result(m.from_user.id, score)
        await m.answer(
            f"Готово! Правильных ответов: {score}/{total}\n{remark}",
            reply_markup=ReplyKeyboardRemove()
        )
        USER_STATE.pop(m.from_user.id, None)
        await m.answer("Выберите игру:", reply_markup=GAME_MENU_KB)
        return

    q, variants, correct = qset[step]
    shuffled = variants[:]
    shuffle(shuffled)
    st["correct"] = correct
    await m.answer(
        f"Вопрос {step}: {q}",
        reply_markup=kb(*(shuffled + ["Главное меню"]), width=1)
    )

@tests_router.message(lambda m: m.from_user.id in USER_STATE)
async def test_answer(m: Message):
    st = USER_STATE[m.from_user.id]
    if m.text == "Главное меню":
        USER_STATE.pop(m.from_user.id, None)
        await m.answer("Вы вернулись в главное меню", reply_markup=main_kb(m.from_user.id))
        return
    if m.text == st["correct"]:
        st["score"] += 1
        await m.answer("✅ Верно!")
    else:
        await m.answer(f"❌ Неверно. Правильный ответ: {st['correct']}")
    st["step"] += 1
    await ask(m)

# --- Тренажёр знаний handlers ---
@main_router.message(F.text == "🧠 Тренажёр знаний")
async def game_menu(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Выберите игру:", reply_markup=GAME_MENU_KB)

@game_router.message(F.text == "🟢 Верю — не верю")
async def start_truth_game(m: Message):
    clear_user_state(m.from_user.id)
    GAME_STATE[m.from_user.id] = {"step": 0, "score": 0}
    await m.answer(
        "Отвечайте Верю или Не верю на 20 утверждений о брендах.",
        reply_markup=kb("Верю", "Не верю", "Главное меню", width=2),
    )
    await send_truth(m)

@game_router.message(F.text == "🔗 Ассоциации")
async def start_assoc_game(m: Message):
    clear_user_state(m.from_user.id)
    ASSOC_STATE[m.from_user.id] = {"step": 0, "score": 0}
    await send_assoc(m)

@game_router.message(F.text == "⚡️ Блиц")
async def start_blitz_game(m: Message):
    clear_user_state(m.from_user.id)
    BLITZ_STATE[m.from_user.id] = {"step": 0, "score": 0}
    await send_blitz(m)

@game_router.message(lambda m: m.text == "Назад к меню")
async def game_back(m: Message):
    clear_user_state(m.from_user.id)
    await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))

async def send_truth(m: Message):
    st = GAME_STATE[m.from_user.id]
    step = st["step"]
    if step >= len(TRUTH_QUESTIONS):
        score = st["score"]
        best = record_truth_result(m.from_user.id, score)
        total = len(TRUTH_QUESTIONS)
        if score <= 10:
            remark = "😕 Попробуй ещё раз!"
        elif 11 <= score <= 15:
            remark = "🙂 Неплохой результат!"
        elif 16 <= score <= 19:
            remark = "👍 Отлично!"
        else:
            remark = "🏆 Идеально!"
        await m.answer(
            f"Игра окончена! Правильных ответов: {score}/{total}\n{remark}\nРекорд: {best}",
            reply_markup=main_kb(m.from_user.id),
        )
        GAME_STATE.pop(m.from_user.id, None)
        return
    statement, truth = TRUTH_QUESTIONS[step]
    st["answer"] = truth
    await m.answer(
        f"{step + 1}/20. {statement}",
        reply_markup=kb("Верю", "Не верю", "Главное меню", width=2),
    )

@game_router.message(lambda m: m.from_user.id in GAME_STATE)
async def truth_answer(m: Message):
    if m.text not in {"Верю", "Не верю"}:
        if m.text == "Главное меню":
            GAME_STATE.pop(m.from_user.id, None)
            await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))
        return
    st = GAME_STATE[m.from_user.id]
    user_val = m.text == "Верю"
    if user_val == st["answer"]:
        st["score"] += 1
        await m.answer("✅ Верно!")
    else:
        await m.answer("❌ Неверно")
    st["step"] += 1
    await send_truth(m)

async def send_assoc(m: Message):
    st = ASSOC_STATE[m.from_user.id]
    step = st["step"]
    if step >= len(ASSOCIATIONS):
        score = st["score"]
        best = record_assoc_result(m.from_user.id, score)
        total = len(ASSOCIATIONS)
        if score <= 7:
            remark = "😕 Попробуй ещё раз!"
        elif 8 <= score <= 11:
            remark = "🙂 Неплохой результат!"
        elif 12 <= score <= 14:
            remark = "👍 Отлично!"
        else:
            remark = "🏆 Идеально!"
        await m.answer(
            f"Игра окончена! Правильных ответов: {score}/{total}\n{remark}\nРекорд: {best}",
            reply_markup=main_kb(m.from_user.id),
        )
        ASSOC_STATE.pop(m.from_user.id, None)
        return
    hint, correct = ASSOCIATIONS[step]
    st["correct"] = correct
    options = [correct] + sample([b for b in BRANDS if b != correct], 3)
    shuffle(options)
    await m.answer(
        f"{step + 1}/{len(ASSOCIATIONS)}. {hint}",
        reply_markup=kb(*(options + ["🏠 Главное меню"]), width=1),
    )

@game_router.message(lambda m: m.from_user.id in ASSOC_STATE)
async def assoc_answer(m: Message):
    if m.text == "🏠 Главное меню":
        ASSOC_STATE.pop(m.from_user.id, None)
        await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))
        return
    st = ASSOC_STATE[m.from_user.id]
    if m.text == st["correct"]:
        st["score"] += 1
        await m.answer("✅ Верно!")
    else:
        await m.answer(f"❌ Неверно. Правильный ответ: {st['correct']}")
    st["step"] += 1
    await send_assoc(m)

async def send_blitz(m: Message):
    st = BLITZ_STATE[m.from_user.id]
    step = st["step"]
    if step >= len(BLITZ_QUESTIONS):
        score = st["score"]
        best = record_blitz_result(m.from_user.id, score)
        total = len(BLITZ_QUESTIONS)
        if score <= 25:
            remark = "😕 Попробуй ещё раз!"
        elif 26 <= score <= 40:
            remark = "🙂 Хороший результат!"
        elif 41 <= score <= 49:
            remark = "👍 Отлично!"
        else:
            remark = "🏆 Идеально!"
        await m.answer(
            f"Игра окончена! Правильных ответов: {score}/{total}\n{remark}\nРекорд: {best}",
            reply_markup=main_kb(m.from_user.id),
        )
        BLITZ_STATE.pop(m.from_user.id, None)
        return
    question, options, correct = BLITZ_QUESTIONS[step]
    shuffled = options[:]
    shuffle(shuffled)
    st["correct"] = correct
    await m.answer(
        f"{step + 1}/{len(BLITZ_QUESTIONS)}. {question}",
        reply_markup=kb(*(shuffled + ["🏠 Главное меню"]), width=1),
    )

@game_router.message(lambda m: m.from_user.id in BLITZ_STATE)
async def blitz_answer(m: Message):
    if m.text == "🏠 Главное меню":
        BLITZ_STATE.pop(m.from_user.id, None)
        await m.answer("Главное меню", reply_markup=main_kb(m.from_user.id))
        return
    st = BLITZ_STATE[m.from_user.id]
    if m.text == st["correct"]:
        st["score"] += 1
        await m.answer("✅ Верно!")
    else:
        await m.answer(f"❌ Неверно. Правильный ответ: {st['correct']}")
    st["step"] += 1
    await send_blitz(m)


@dp.message(F.photo)
async def get_file_id(m: Message):
    await m.answer(f"✅ Получен file_id:\n<code>{m.photo[-1].file_id}</code>")

dp.include_routers(
    search_router,
    brand_lookup_router,
    main_router,
    admin_router,
    whisky_router,
    vodka_router,
    beer_router,
    wine_router,
    game_router,
    tests_router,
    jager_router,
    brand_menu_router,
    suggest_router,
)


@dp.message(
    lambda m: (
        m.from_user.id not in USER_STATE
        and m.from_user.id not in GAME_STATE
        and m.from_user.id not in ASSOC_STATE
        and m.from_user.id not in BLITZ_STATE
        and normalize(m.text) in ALIAS_MAP
    )
)
async def fallback_brand(m: Message):
    """Final handler to show brand info if text matches a known brand."""
    await show_brand(m)




