from __future__ import annotations
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

router = Router()

class Mode(StatesGroup):
    ai_live = State()

def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

@dataclass
class BrandLocal:
    title: str
    summary: str

LOCAL_DB: Dict[str, BrandLocal] = {
    norm("Monkey Shoulder"): BrandLocal(
        title="Monkey Shoulder",
        summary="Blended Malt Scotch (100% солодовые). Мягкий профиль, силён в коктейлях и в чистом.",
    ),
}

OUR_ALTS: Dict[str, str] = {
    "dewars": "Monkey Shoulder",
    "ballantines": "Grant’s",
    "jameson": "Tullamore D.E.W.",
    "johnnie walker": "Grant’s",
    "chivas": "Glenfiddich 12",
}

def live_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Выйти из AI-режима", callback_data="ai:exit")
    return kb.as_markup()

def local_lookup(q: str) -> Optional[str]:
    key = norm(q)
    if key in LOCAL_DB:
        b = LOCAL_DB[key]
        return f"<b>{b.title}</b> — {b.summary}"
    for k, b in LOCAL_DB.items():
        if key and (key in k or k in key):
            return f"<b>{b.title}</b> — {b.summary}"
    return None

BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

async def bing_search(query: str, *, mkt: str = "ru-RU", count: int = 5) -> List[Dict]:
    api_key = os.getenv("BING_API_KEY")
    if not api_key:
        return []
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "mkt": mkt, "count": count, "textDecorations": False, "textFormat": "Raw"}
    async with aiohttp.ClientSession() as session:
        async with session.get(BING_ENDPOINT, headers=headers, params=params, timeout=15) as r:
            if r.status != 200:
                return []
            data = await r.json()
            return data.get("webPages", {}).get("value", [])

def pick_our_alt(q: str) -> Optional[str]:
    qn = norm(q)
    for k, v in OUR_ALTS.items():
        if k in qn:
            return v
    return None

def summarize_results(results: List[Dict]) -> Tuple[str, List[str]]:
    best_title = results[0]["name"] if results else ""
    facts: List[str] = []
    for item in results[:3]:
        s = (item.get("snippet") or "").strip()
        if s:
            facts.append(s)
    return best_title, facts

def build_comp_answer(query: str, facts: List[str], our_alt: Optional[str]) -> str:
    head = f"<b>{(query or '').title()}</b> — кратко\n" if query else ""
    body = "\n".join(f"— {f}" for f in facts if f) or "— Бренд: информация найдена, подробности на сайте производителя."
    if our_alt:
        why: List[str] = []
        if our_alt.lower() == "monkey shoulder":
            why = [
                "100% солодовые (не купаж с зерновыми)",
                "мягкий профиль и сильная коктейльная база",
                "стабильная поддержка в HoReCa",
            ]
        elif our_alt.lower() == "grant’s" or our_alt.lower() == "grant's":
            why = [
                "сильное соотношение цена/качество",
                "широкая узнаваемость",
                "линейка вкусовых позиций",
            ]
        elif our_alt.lower() == "tullamore d.e.w.":
            why = [
                "ирландский стиль, богатый профиль",
                "есть медовая версия для коктейлей",
                "поддержка барного сегмента",
            ]
        elif our_alt.lower() == "glenfiddich 12":
            why = [
                "100% солодовый single malt",
                "престиж и история Спейсайда",
                "сильная премиальная подача",
            ]
        pitch = "\n".join(f"— {w}" for w in why) if why else ""
        return f"{head}{body}\n\n<b>Наш аналог:</b> {our_alt}\n<b>Почему выгоднее:</b>\n{pitch}".strip()
    return f"{head}{body}"

@router.message(Command("ai_live"))
async def ai_live_start_cmd(m: Message, state: FSMContext):
    await state.set_state(Mode.ai_live)
    await m.answer("AI-режим с онлайн-поиском включен. Напишите бренд или вопрос.", reply_markup=live_kb())

@router.callback_query(F.data == "ai:enter")
async def ai_live_start_btn(c: CallbackQuery, state: FSMContext):
    await state.set_state(Mode.ai_live)
    await c.message.edit_text("AI-режим с онлайн-поиском включен. Напишите бренд или вопрос.", reply_markup=live_kb())
    await c.answer()

@router.message(Mode.ai_live, F.text.as_("q"))
async def ai_live_query(m: Message, state: FSMContext, q: str):
    ans = local_lookup(q)
    if ans:
        await m.answer(ans, reply_markup=live_kb())
        return

    results = await bing_search(q)
    our_alt = pick_our_alt(q)
    if results:
        title, facts = summarize_results(results)
        text = build_comp_answer(title or q, facts, our_alt)
        await m.answer(text, reply_markup=live_kb())
        return

    fallback = "Не нашёл точной информации. Уточните запрос (бренд/категория) или попробуйте другое написание."
    if our_alt:
        fallback += f"\n\n<b>Наш аналог:</b> {our_alt}"
    await m.answer(fallback, reply_markup=live_kb())

@router.message(Mode.ai_live, Command("exit"))
async def ai_live_exit_cmd(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Окей, вышли из AI-режима.")

@router.callback_query(F.data == "ai:exit")
async def ai_live_exit_btn(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Окей, вышли из AI-режима.")
    await c.answer()
