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
        photo="https://i.imgur.com/NO5rR64.png",
        caption="""<b>Monkey Shoulder</b>
• Купаж из Glenfiddich, Balvenie и Kininvie
• Аромат: ваниль, мёд, цитрус
• Вкус: карамель, специи, тосты
• Крепость: 40 %
• Идеален для Old Fashioned и Whisky Sour"""
    )

@whisky_router.message(F.text == "Glenfiddich 12 Years")
async def glenfiddich_12(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/I7x2LMf.png",
        caption="""<b>Glenfiddich 12 YO</b>
• Односолодовый виски из Спейсайда
• Аромат: груша, дуб, цветы
• Вкус: ваниль, яблоко, херес
• Крепость: 40 %
• Выдержка: 12 лет в бочках из-под бурбона и хереса"""
    )

@whisky_router.message(F.text == "Fire & Cane")
async def fire_and_cane(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/z4cKozt.png",
        caption="""<b>Glenfiddich Fire & Cane</b>
• Экспериментальный торфяной виски
• Аромат: дым, специи, цитрусы
• Вкус: сладкий дым, ириска, дуб
• Выдержан в бочках из-под рома"""
    )

@whisky_router.message(F.text == "IPA Experiment")
async def ipa_experiment(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/HzOE68J.png",
        caption="""<b>Glenfiddich IPA Experiment</b>
• Выдержан в бочках из-под IPA-пива
• Аромат: хмель, яблоко, ваниль
• Вкус: свежий, с фруктами и травами
• Идеален для крафтовых коктейлей"""
    )

@whisky_router.message(F.text == "Grant's Classic")
async def grants_classic(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/npfZdM2.png",
        caption="""<b>Grant's Triple Wood</b>
• Купаж из 25 виски, выдержан в 3 бочках
• Аромат: карамель, груша, ваниль
• Вкус: мед, специи, дуб
• Отличный выбор по цене"""
    )

@whisky_router.message(F.text == "Grant's Summer Orange")
async def grants_orange(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/M59uWKm.png",
        caption="""<b>Grant's Summer Orange</b>
• Виски с натуральным апельсином
• Аромат: апельсин, ваниль
• Вкус: цитрусы, мед, сливки
• Идеален в чистом виде и в коктейлях"""
    )

@whisky_router.message(F.text == "Grant's Winter Dessert")
async def grants_winter(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/qkCn5nW.png",
        caption="""<b>Grant's Winter Dessert</b>
• Виски с тёплыми специями и нотами яблочного пирога
• Вкус: яблоко, корица, карамель
• Уютный напиток для зимних вечеров"""
    )

@whisky_router.message(F.text == "Grant's Tropical Fiesta")
async def grants_fiesta(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/V9aRQnN.png",
        caption="""<b>Grant's Tropical Fiesta</b>
• Летняя версия с тропическими фруктами
• Аромат: ананас, маракуйя
• Вкус: экзотика, специи, виски
• Освежающий и лёгкий"""
    )

@whisky_router.message(F.text == "Tullamore D.E.W.")
async def tullamore_dew(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/p86DH2q.png",
        caption="""<b>Tullamore D.E.W.</b>
• Ирландский тройной дистилляции виски
• Аромат: яблоко, ваниль, мёд
• Вкус: орехи, сливки, древесина
• Крепость: 40 %
• Классика ирландского виски"""
    )

@whisky_router.message(F.text == "Tullamore D.E.W. Honey")
async def tullamore_honey(m: Message):
    await m.answer_photo(
        photo="https://i.imgur.com/QjRV6gt.png",
        caption="""<b>Tullamore Honey</b>
• Ирландский виски с натуральным мёдом
• Вкус: мягкий, сладкий, цветочный
• Идеален в шотах и на льду"""
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

dp.include_routers(main_router, whisky_router, tests_router)
