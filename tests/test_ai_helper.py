import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from routers.ai_helper import norm, find_locally
import asyncio


def test_norm():
    assert norm("Манки Шолдер!!!") == "манки шолдер"
    assert norm("  monkey   shoulder ") == "monkey shoulder"


def test_find_locally_hit():
    ans = asyncio.run(find_locally("манки"))
    assert ans is not None
    assert "Monkey Shoulder" in ans


def test_find_locally_miss():
    ans = asyncio.run(find_locally("несуществующий бренд"))
    assert ans is None
