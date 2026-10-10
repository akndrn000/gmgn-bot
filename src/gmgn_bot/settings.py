"""
settings.py — Baca dan validasi environment variable.

FIX:
- Validasi lengkap semua env var wajib sebelum bot mulai.
- Pesan error yang jelas kalau ada yang kurang, sehingga Railway log
  langsung menunjukkan variabel mana yang belum di-set.
- TIMEZONE default ke Asia/Jakarta jika tidak di-set.
"""

from __future__ import annotations

import logging
import os
import sys

import pytz

logger = logging.getLogger(__name__)


def _require(name: str) -> str:
    """Ambil env var; exit dengan pesan jelas jika tidak ada."""
    value = os.environ.get(name, "").strip()
    if not value:
        logger.critical(
            "Environment variable '%s' wajib diisi tapi tidak ditemukan. "
            "Tambahkan di Railway → Variables.",
            name,
        )
        sys.exit(1)
    return value


def _load_timezone(name: str = "TIMEZONE", default: str = "Asia/Jakarta") -> pytz.BaseTzInfo:
    tz_str = os.environ.get(name, default).strip()
    try:
        tz = pytz.timezone(tz_str)
        logger.info("Timezone: %s", tz_str)
        return tz
    except pytz.UnknownTimeZoneError:
        logger.error(
            "Timezone '%s' tidak dikenal. Menggunakan default '%s'.", tz_str, default
        )
        return pytz.timezone(default)


# ── Nilai yang di-load saat modul ini diimport ─────────────────────────────

DISCORD_USER_TOKEN: str = _require("DISCORD_USER_TOKEN")
MONITOR_CHANNEL_ID: int

_raw_channel = _require("MONITOR_CHANNEL_ID")
try:
    MONITOR_CHANNEL_ID = int(_raw_channel)
except ValueError:
    logger.critical(
        "MONITOR_CHANNEL_ID harus berupa angka, tapi nilainya: '%s'", _raw_channel
    )
    sys.exit(1)

TIMEZONE: pytz.BaseTzInfo = _load_timezone()
