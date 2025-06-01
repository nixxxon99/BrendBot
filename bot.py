import os
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = os.getenv("TOKEN")
if not API_TOKEN:
    raise RuntimeError("TOKEN env-var is required!")

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
bot: Bot = Bot(API_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher()

def kb(*labels: str, width: int = 2) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for text in labels:
        builder.add(KeyboardButton(text=text))
    builder.adjust(width)
    return builder.as_markup(resize_keyboard=True)

MAIN_KB = kb("🥃 Виски", "🧊 Водка", "🍺 Пиво", "🍷 Вино",
             "📋 Тесты", "🍹 Коктейли", "🦌 Ягермейстер")

main_router = Router()

@main_router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer("Привет! Выбери категорию:", reply_markup=MAIN_KB)

WHISKY_KB = kb(
    "Monkey Shoulder", "Glenfiddich 12 Years", "Fire & Cane",
    "IPA Experiment", "Grant's Classic", "Grant's Summer Orange",
    "Grant's Winter Dessert", "Grant's Tropical Fiesta",
    "Tullamore D.E.W.", "Tullamore D.E.W. Honey", "Назад",
    width=2
)

whisky_router = Router()

@whisky_router.message(F.text == "🥃 Виски")
async def whisky_menu(m: Message):
    await m.answer("🥃 Выбери бренд виски:", reply_markup=WHISKY_KB)

@whisky_router.message(F.text == "Назад")
async def whisky_back(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

@whisky_router.message(F.text == "Monkey Shoulder")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Glenfiddich 12 Years")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Fire & Cane")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "IPA Experiment")
async def ipa_experiment(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAIG52g4npbaJO1p_0s7aVNpQ5_r9nkEAAIT9TEb1P3ISRjGBYkQaU3hAQADAgADeQADNgQ",  # ← вставь свой file_id
        caption=(
            "<b>Glenfiddich IPA Experiment</b>\n"
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Grant's Classic")
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
        parse_mode="HTML"
    )


@whisky_router.message(F.text == "Grant's Summer Orange")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Grant's Winter Dessert")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Grant's Tropical Fiesta")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Tullamore D.E.W.")
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
        parse_mode="HTML"
    )

@whisky_router.message(F.text == "Tullamore D.E.W. Honey")
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
        )
    )

# ——— Клавиатура водки ———
VODKA_KB = kb(
    "Серебрянка", "Reyka", "Finlandia", "Зелёная марка",
    "Талка", "Русский стандарт", "Назад", width=2
)

vodka_router = Router()

@vodka_router.message(F.text == "🧊 Водка")
async def vodka_menu(m: Message):
    await m.answer("🧊 Выбери бренд водки:", reply_markup=VODKA_KB)

@vodka_router.message(F.text == "Назад")
async def vodka_back(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

@vodka_router.message(F.text == "Серебрянка")
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
        )
    )

    









    

tests_router = Router()
TESTS_MENU_KB = kb("🧪 Тест по Jägermeister", "Назад")

QUESTIONS = {
    "jager": {
        1: ("Сколько трав в составе Jägermeister?", ["56", "27", "12", "🤫 Секрет"], "56"),
    }
}
USER_STATE: dict[int, dict] = {}

@tests_router.message(F.text == "📋 Тесты")
async def tests_menu(m: Message):
    await m.answer("Выберите тест:", reply_markup=TESTS_MENU_KB)

@tests_router.message(F.text == "🧪 Тест по Jägermeister")
async def start_jager(m: Message):
    USER_STATE[m.from_user.id] = {"name": "jager", "step": 1, "score": 0}
    await ask(m)

@tests_router.message(F.text == "Назад")
async def tests_back(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

async def ask(m: Message):
    st = USER_STATE[m.from_user.id]
    qset = QUESTIONS[st["name"]]
    step = st["step"]
    if step > len(qset):
        await m.answer(f"Готово! Правильных ответов: {st['score']}/{len(qset)}",
                       reply_markup=ReplyKeyboardRemove())
        USER_STATE.pop(m.from_user.id, None)
        return
    q, variants, correct = qset[step]
    st["correct"] = correct
    await m.answer(f"Вопрос {step}: {q}", reply_markup=kb(*variants, width=1))

@tests_router.message(lambda m: m.from_user.id in USER_STATE)
async def test_answer(m: Message):
    st = USER_STATE[m.from_user.id]
    if m.text == st["correct"]:
        st["score"] += 1
        await m.answer("✅ Верно!")
    else:
        await m.answer(f"❌ Неверно. Правильный ответ: {st['correct']}")
    st["step"] += 1
    await ask(m)
@dp.message(F.photo)
async def get_file_id(m: Message):
    await m.answer(f"✅ Получен file_id:\n<code>{m.photo[-1].file_id}</code>")

dp.include_routers(main_router, whisky_router, tests_router, vodka_router)

