"""
storage.py — Baca/tulis config.json ke Railway Volume (/data/config.json).

FIX:
- Auto-create direktori /data jika belum ada (Railway Volume belum di-mount
  atau environment lokal).
- Skema config default yang lengkap agar tidak KeyError saat key baru
  diakses sebelum pernah di-set.
- Atomic write (tulis ke file .tmp dulu, lalu rename) agar tidak korup
  jika proses mati di tengah penulisan.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import Any

logger = logging.getLogger(__name__)

# Path penyimpanan config — bisa di-override lewat env var DATA_DIR
DATA_DIR = os.environ.get("DATA_DIR", "/data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

# Skema default — selalu lengkap agar tidak KeyError
_DEFAULT_CONFIG: dict[str, Any] = {
    "target_channels": [],
    "gm_hour": 7,
    "gm_minute": 0,
    "gn_hour": 21,
    "gn_minute": 0,
}


def _ensure_data_dir() -> None:
    """Buat direktori data jika belum ada."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as exc:
        # Log tapi jangan crash — mungkin sudah ada
        logger.warning("Tidak bisa membuat direktori %s: %s", DATA_DIR, exc)


def load() -> dict[str, Any]:
    """
    Baca config dari disk. Jika file tidak ada atau rusak,
    kembalikan config default dan simpan ke disk.
    """
    _ensure_data_dir()

    if not os.path.exists(CONFIG_PATH):
        logger.info("Config belum ada, membuat config default di %s", CONFIG_PATH)
        config = dict(_DEFAULT_CONFIG)
        save(config)
        return config

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        # Merge dengan default agar key baru yang ditambah ke _DEFAULT_CONFIG
        # tidak menyebabkan KeyError pada config lama yang sudah tersimpan.
        merged = dict(_DEFAULT_CONFIG)
        merged.update(data)
        return merged

    except (json.JSONDecodeError, OSError) as exc:
        logger.error(
            "Gagal membaca %s (%s). Menggunakan config default.", CONFIG_PATH, exc
        )
        config = dict(_DEFAULT_CONFIG)
        save(config)
        return config


def save(config: dict[str, Any]) -> None:
    """
    Tulis config ke disk secara atomik (tmp → rename).
    Mencegah file korup jika proses mati di tengah penulisan.
    """
    _ensure_data_dir()

    try:
        # Tulis ke file sementara di direktori yang sama agar rename atomic
        fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            os.unlink(tmp_path)
            raise

        os.replace(tmp_path, CONFIG_PATH)
        logger.debug("Config berhasil disimpan ke %s", CONFIG_PATH)

    except OSError as exc:
        logger.error("Gagal menyimpan config ke %s: %s", CONFIG_PATH, exc)
        raise
