"""
messages.py — Kumpulan pesan GM/GN dengan sistem rarity.

Setiap pesan sekarang membawa rarity-nya ('common'/'rare'/'epic')
agar embed bisa tampil dengan warna yang berbeda sesuai kelangkaannya.
"""

from __future__ import annotations

import random
from typing import NamedTuple


class WeightedMessage(NamedTuple):
    text: str
    weight: int     # Semakin tinggi = semakin sering muncul
    rarity: str     # 'common' | 'rare' | 'epic'


# ── Pesan GM ──────────────────────────────────────────────────────────────────
_GM_MESSAGES: list[WeightedMessage] = [
    WeightedMessage("gm",               weight=50, rarity="common"),
    WeightedMessage("gm!",              weight=30, rarity="common"),
    WeightedMessage("gm everyone",      weight=10, rarity="rare"),
    WeightedMessage("good morning!",    weight=5,  rarity="rare"),
    WeightedMessage("rise and shine ☀️", weight=3,  rarity="epic"),
    WeightedMessage("gm fren 👋",        weight=2,  rarity="epic"),
]

# ── Pesan GN ──────────────────────────────────────────────────────────────────
_GN_MESSAGES: list[WeightedMessage] = [
    WeightedMessage("gn",               weight=50, rarity="common"),
    WeightedMessage("gn!",              weight=30, rarity="common"),
    WeightedMessage("gn everyone",      weight=10, rarity="rare"),
    WeightedMessage("good night!",      weight=5,  rarity="rare"),
    WeightedMessage("sleep well 🌙",    weight=3,  rarity="epic"),
    WeightedMessage("gn fren 👋",        weight=2,  rarity="epic"),
]


def _pick(messages: list[WeightedMessage]) -> WeightedMessage:
    """Pilih satu pesan berdasarkan bobot (weighted random)."""
    weights = [m.weight for m in messages]
    return random.choices(messages, weights=weights, k=1)[0]  # noqa: S311


def pick_gm() -> WeightedMessage:
    return _pick(_GM_MESSAGES)


def pick_gn() -> WeightedMessage:
    return _pick(_GN_MESSAGES)
