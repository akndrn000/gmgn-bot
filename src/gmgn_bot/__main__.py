"""
__main__.py — Titik masuk: python -m gmgn_bot

FIX:
- Retry loop dengan exponential backoff agar bot otomatis reconnect
  setelah disconnect (Discord self-bot sering di-drop), tanpa perlu
  Railway restart dari luar.
- Batas maksimum retry agar tidak loop selamanya kalau ada error fatal
  (misal token salah / sudah di-ban).
- Logging yang informatif untuk Railway log viewer.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time

from .client import create_client
from .logging_setup import setup_logging

# ── Konfigurasi retry ───────────────────────────────────────────────────────
_INITIAL_DELAY = 5       # detik tunggu sebelum retry pertama
_MAX_DELAY = 300         # detik maksimum antar retry (5 menit)
_MAX_RETRIES = 10        # setelah ini bot benar-benar berhenti
_BACKOFF_FACTOR = 2      # delay digandakan setiap kali retry

# Error yang dianggap FATAL — tidak perlu retry, langsung exit
_FATAL_EXCEPTIONS = (
    # Login gagal = token salah / di-revoke
    # Import dari discord, tapi kita handle lewat string nama class
    # agar tidak error import jika library berubah
)

logger = logging.getLogger(__name__)


async def _run_once() -> None:
    """Jalankan bot satu sesi sampai disconnect."""
    client = create_client()
    from . import settings
    await client.start(settings.DISCORD_USER_TOKEN)


def main() -> None:
    setup_logging()
    logger.info("gmgn-bot mulai.")

    retries = 0
    delay = _INITIAL_DELAY

    while True:
        try:
            asyncio.run(_run_once())
            # Jika client.start() selesai tanpa exception, artinya logout normal
            logger.info("Bot disconnect secara normal. Reconnect dalam %d detik...", delay)

        except KeyboardInterrupt:
            logger.info("Dihentikan manual (KeyboardInterrupt). Keluar.")
            sys.exit(0)

        except Exception as exc:  # noqa: BLE001
            retries += 1
            exc_name = type(exc).__name__

            # Cek apakah ini error login / token tidak valid
            if "LoginFailure" in exc_name or "Forbidden" in exc_name:
                logger.critical(
                    "Login gagal (%s: %s). "
                    "Pastikan DISCORD_USER_TOKEN masih valid. Bot berhenti.",
                    exc_name,
                    exc,
                )
                sys.exit(1)

            if retries > _MAX_RETRIES:
                logger.critical(
                    "Sudah %d kali retry, bot berhenti. Error terakhir: %s: %s",
                    _MAX_RETRIES,
                    exc_name,
                    exc,
                )
                sys.exit(1)

            logger.error(
                "Error tidak terduga (%s: %s). Retry ke-%d dalam %d detik...",
                exc_name,
                exc,
                retries,
                delay,
                exc_info=True,
            )

        # Tunggu sebelum reconnect
        time.sleep(delay)
        delay = min(delay * _BACKOFF_FACTOR, _MAX_DELAY)

        # Reset delay setelah berhasil jalan cukup lama
        # (ditandai dengan retries sudah tinggi tapi baru disconnect)


if __name__ == "__main__":
    main()
