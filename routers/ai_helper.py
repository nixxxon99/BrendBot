from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dataclasses import dataclass
from typing import Optional, Dict, List
import os
import re
import time
import csv
from pathlib import Path

router = Router()

class Mode(StatesGroup):
    ai_helper = State()

def ai_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Выйти из AI-режима", callback_data="ai:exit")
    return kb.as_markup()

# --- анти-флуд (очень простой) ---
_last_hit: Dict[int, float] = {}
def rate_limited(user_id: int, interval: float = 2.0) -> bool:
    now = time.time()
    last = _last_hit.get(user_id, 0.0)
    if now - last < interval:
        return True
    _last_hit[user_id] = now
    return False

# --- логи ---
def log_event(user_id: int, query: str, source: str, answer_len: int) -> None:
    Path("logs").mkdir(exist_ok=True)
    path = Path("logs/ai_helper.csv")
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts","user_id","source","q","answer_len"])
        w.writerow([int(time.time()), user_id, source, query, answer_len])

# --- нормализация ---
def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()
# --- мини-БД (заглушка) ---
@dataclass
class BrandCard:
    title: str
    aliases: List[str]
    summary: str

_FAKE_DB: List[BrandCard] = [
    BrandCard(
        title="Monkey Shoulder",
        aliases=["манки шолдер","манки","monkey shoulder","монки шолдер","мэнки шолдер","monkey"],
        summary="Blended Malt Scotch. Мягкий вкус, хорош в чистом и в коктейлях.",
    ),
]

_INDEX: Dict[str, BrandCard] = {}
for c in _FAKE_DB:
    for a in [c.title] + c.aliases:
        _INDEX[norm(a)] = c

async def find_locally(query: str) -> Optional[str]:
    q = norm(query)
    if q in _INDEX:
        c = _INDEX[q]
        return f"<b>{c.title}</b> — {c.summary}"
    for k, c in _INDEX.items():
        if q and (q in k or k in q):
            return f"<b>{c.title}</b> — {c.summary}"
    return None

# --- утилита для API-ключа ---
def _get_api_key() -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    env_path = Path("env/.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=",1)[1].strip()
    return None

# --- LLM вызов ---
async def ask_llm(query: str) -> str:
    api_key = _get_api_key()
    if not api_key:
        return "AI сейчас недоступен."
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "AI сейчас недоступен."

@router.message(Command("ai"))
async def ai_start(m: Message, state: FSMContext):
    await state.set_state(Mode.ai_helper)
    await m.answer(
        "AI-помощник активирован. Напиши бренд/вопрос (например: «манки шолдер»).\n"
        "Команда /exit — выход.",
        reply_markup=ai_menu_kb()
    )

@router.message(Mode.ai_helper, F.text.as_("q"))
async def ai_answer(m: Message, state: FSMContext, q: str):
    if rate_limited(m.from_user.id):
        return
    local = await find_locally(q)
    if local:
        log_event(m.from_user.id, q, "local", len(local))
        await m.answer(local, reply_markup=ai_menu_kb())
        return
    llm = await ask_llm(q)
    log_event(m.from_user.id, q, "llm", len(llm))
    await m.answer(llm, reply_markup=ai_menu_kb())

@router.message(Mode.ai_helper, Command("exit"))
async def ai_exit_cmd(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Окей, вышли из AI-режима.")

@router.callback_query(F.data == "ai:exit")
async def ai_exit_btn(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Окей, вышли из AI-режима.")
    await c.answer()
