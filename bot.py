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
        photo="https://upload.wikimedia.org/wikipedia/commons/8/8d/Monkey_Shoulder_scotch_bottle.jpg",
        caption="""<b>Monkey Shoulder</b>
• Купажированный шотландский виски (Glenfiddich + Balvenie + Kininvie)
• Аромат: ваниль, мёд, цитрус
• Вкус: карамель, тёплые специи, тостовый хлеб
• Крепость 40 %
• Идеален для Old Fashioned и Whisky Sour
• Бронзовые «плечи» на бутылке — символ тройного солода"""
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
