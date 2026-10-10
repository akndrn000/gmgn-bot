"""
logging_setup.py — Konfigurasi logging.

FIX:
- Output ke stdout (bukan stderr) agar Railway log viewer menampilkan
  semua log dalam satu stream yang urut.
- Format timestamp yang mudah dibaca di Railway log.
- Level discord library di-set ke WARNING agar log tidak dibanjiri
  pesan internal discord.py-self yang verbose.
"""

from __future__ import annotations

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Konfigurasi root logger. Panggil sekali di awal program."""

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)

    # Hapus handler lama agar tidak duplikat jika dipanggil ulang
    root.handlers.clear()
    root.addHandler(handler)

    # Kurangi noise dari library internal
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
