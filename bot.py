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


VODKA_KB = kb(
    "Серебрянка", "Reyka", "Finlandia", "Зелёная марка",
    "Талка", "Русский Стандарт", "Назад", width=2
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

@vodka_router.message(F.text == "Reyka")
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
        )
    )
    
@vodka_router.message(F.text == "Finlandia")
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
        )
    )

@vodka_router.message(F.text == "Зелёная марка")
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
        )
    )


@vodka_router.message(F.text == "Талка")
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
        )
    )

@vodka_router.message(F.text == "Русский Стандарт")
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
        )
    )

beer_router = Router()

BEER_KB = kb(
    "Paulaner", "Blue Moon",
    "London Pride", "Coors",
    "Staropramen", "Назад",
    width=2
)

@beer_router.message(F.text == "🍺 Пиво")
async def beer_menu(m: Message):
    await m.answer("🍺 Выбери бренд пива:", reply_markup=BEER_KB)

@beer_router.message(F.text == "Назад")
async def beer_back(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

@beer_router.message(F.text == "Paulaner")
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

@beer_router.message(F.text == "Blue Moon")
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
        )
    )
@beer_router.message(F.text == "London Pride")
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
        )
    )

@beer_router.message(F.text == "Coors")
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
        )
    )

@beer_router.message(F.text == "Staropramen")
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
        )
    )

WINE_KB = kb(
    "Mateus Original Rosé", "Undurraga Sauvignon Blanc",
    "Devil’s Rock Riesling", "Piccola Nostra",
    "Эль Санчес", "Шале де Сюд", "Назад", width=2
)

wine_router = Router()

@wine_router.message(F.text == "🍷 Вино")
async def wine_menu(m: Message):
    await m.answer("🍷 Выбери вино:", reply_markup=WINE_KB)

@wine_router.message(F.text == "Назад")
async def wine_back(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

@wine_router.message(F.text == "Mateus Rosé")
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
        )
    )

@wine_router.message(F.text == "Undurraga Sauvignon Blanc")
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
        )
    )

@wine_router.message(F.text == "Devil’s Rock Riesling")
async def devils_rock_riesling(m: Message):
    await m.answer_photo(
        photo="AgACAgIAAxkBAAILXmg8HL0ZOUJYurNUmx1RK7xZYadHAALc9zEbPHPgSdjIeJJeBYRdAQADAgADeQADNgQ",
        caption=(
            "<b>Devil’s Rock Riesling</b>\n"
            "• Белое полусухое вино из Германии\n"
            "• Сорт винограда: Riesling\n"
            "• Цвет: светло-золотистый с зелёными бликами\n"
            "• Аромат: яблоко, персик, цитрус, мёд\n"
            "• Вкус: лёгкий, сдержанно сладкий, хорошо сбалансированный\n"
            "• Крепость: 10.5 % ABV\n"
            "• Отличный выбор для лёгкой кухни и азиатских блюд\n"
            "• Подаётся охлаждённым до 8–10 °C\n"
            "• Современный стиль немецкого рислинга\n"
            "• Упаковка с запоминающимся дизайном и «дьявольским» характером"
        )
    )

@wine_router.message(F.text == "Piccola Nostra")
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
        )
    )

@wine_router.message(F.text == "Эль Санчес")
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
        )
    )

@wine_router.message(F.text == "Шале де Сюд")
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
        )
    )
    
jager_router = Router()

@jager_router.message(F.text == "Jägermeister")
async def jagermeister_info(m: Message):
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
        )
    )
      

from random import shuffle
from aiogram.types import ReplyKeyboardRemove

tests_router = Router()

TESTS_MENU_KB = kb(
    "Тест: Jägermeister", "Тест: Виски", "Тест: Водка",
    "Тест: Пиво", "Тест: Вино", "Назад", width=2
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
        3: ("Devil’s Rock Riesling — стиль вина:", ["Белое полусладкое", "Красное сухое", "Розовое сухое", "Игристое"], "Белое полусладкое"),
        4: ("Piccola Nostra — это вино:", ["Итальянское полусладкое", "Французское сухое", "Испанское игристое", "Немецкое белое"], "Итальянское полусладкое"),
        5: ("El Sanchez — это:", ["Испанское полусладкое", "Французское игристое", "Чилийское сухое", "Португальское красное"], "Испанское полусладкое"),
        6: ("Chalet des Sud — это:", ["Французское полусладкое", "Аргентинское красное", "Итальянское игристое", "Немецкое сладкое"], "Французское полусладкое"),
        7: ("К какому блюду подходит Mateus Rosé?", ["Салаты, лёгкие закуски", "Стейки", "Пицца", "Шоколад"], "Салаты, лёгкие закуски"),
        8: ("С чем хорошо сочетается Riesling?", ["Фрукты и морепродукты", "Бургеры", "Говядина", "Шашлык"], "Фрукты и морепродукты"),
        9: ("Типичный аромат Sauvignon Blanc:", ["Цитрус и трава", "Кофе", "Дуб", "Ваниль"], "Цитрус и трава"),
        10: ("El Sanchez подойдёт для:", ["Фруктовых закусок", "Жареного мяса", "Пельменей", "Пиццы"], "Фруктовых закусок")
        }
}

USER_STATE: dict[int, dict] = {}

@tests_router.message(F.text == "📋 Тесты")
async def tests_menu(m: Message):
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
    name = name_map[m.text]
    USER_STATE[m.from_user.id] = {"name": name, "step": 1, "score": 0}
    await ask(m)


@tests_router.message(lambda m: m.text == "Назад")
async def back_to_menu(m: Message):
    await m.answer("Главное меню", reply_markup=MAIN_KB)

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
        await m.answer(f"Готово! Правильных ответов: {score}/{total}\n{remark}",
                       reply_markup=ReplyKeyboardRemove())
        USER_STATE.pop(m.from_user.id, None)
        return

    q, variants, correct = qset[step]
    shuffled = variants[:]
    shuffle(shuffled)
    st["correct"] = correct
    await m.answer(f"Вопрос {step}: {q}", reply_markup=kb(*shuffled, width=1))

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

dp.include_routers(main_router, whisky_router, vodka_router, beer_router, wine_router, tests_router,jager_router)




