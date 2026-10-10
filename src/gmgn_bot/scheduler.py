"""
scheduler.py — Logika jadwal dan pengiriman pesan GM/GN berkala.

Pesan GM/GN dikirim lewat send() dari embeds.py yang otomatis memilih
teks biasa (self-bot) atau Discord Embed (bot resmi).
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime

import discord

from . import settings
from .embeds import msg_gm, msg_gn, send
from .messages import pick_gm, pick_gn
from .storage import load as load_config

logger = logging.getLogger(__name__)

_scheduler_started = False


async def start_scheduler(client: discord.Client) -> None:
    """Mulai background task scheduler. Hanya berjalan sekali."""
    global _scheduler_started  # noqa: PLW0603
    if _scheduler_started:
        logger.debug("Scheduler sudah berjalan, skip.")
        return
    _scheduler_started = True
    asyncio.create_task(_scheduler_loop(client), name="gmgn-scheduler")
    logger.info("Scheduler dimulai.")


async def _scheduler_loop(client: discord.Client) -> None:
    """Loop utama yang berjalan selamanya dan cek jadwal setiap menit."""
    while True:
        try:
            await _tick(client)
        except Exception:  # noqa: BLE001
            logger.exception("Error di scheduler loop, melanjutkan...")
        now = datetime.now(tz=settings.TIMEZONE)
        seconds_until_next_minute = 60 - now.second
        await asyncio.sleep(seconds_until_next_minute)


async def _tick(client: discord.Client) -> None:
    """Satu siklus pengecekan jadwal."""
    config = load_config()
    now = datetime.now(tz=settings.TIMEZONE)

    is_gm_time = (now.hour == config["gm_hour"] and now.minute == config["gm_minute"])
    is_gn_time = (now.hour == config["gn_hour"] and now.minute == config["gn_minute"])

    if not (is_gm_time or is_gn_time):
        return

    target_channels: list[int] = config.get("target_channels", [])
    if not target_channels:
        logger.info("Waktunya kirim pesan tapi daftar target_channels kosong.")
        return

    kind  = "gm" if is_gm_time else "gn"
    label = "GM" if is_gm_time else "GN"
    logger.info("Waktunya kirim %s ke %d channel.", label, len(target_channels))

    for channel_id in target_channels:
        msg = pick_gm() if kind == "gm" else pick_gn()
        content = msg_gm(msg.text, msg.rarity) if kind == "gm" else msg_gn(msg.text, msg.rarity)
        await _send_to_channel(client, channel_id, content, label)
        await asyncio.sleep(random.uniform(3, 15))  # noqa: S311


async def _send_to_channel(
    client: discord.Client,
    channel_id: int,
    content: object,
    label: str,
) -> None:
    """Kirim pesan ke satu channel, dengan penanganan error per-channel."""
    try:
        channel = client.get_channel(channel_id)
        if channel is None:
            channel = await client.fetch_channel(channel_id)

        if not hasattr(channel, "send"):
            logger.warning(
                "Channel %s tidak bisa menerima pesan (type: %s), dilewati.",
                channel_id,
                type(channel).__name__,
            )
            return

        await send(channel, content)
        name = getattr(channel, "name", str(channel_id))
        logger.info("✓ Berhasil kirim %s ke #%s (%s)", label, name, channel_id)

    except discord.Forbidden:
        logger.error("✗ Tidak punya izin kirim pesan ke channel %s.", channel_id)
    except discord.NotFound:
        logger.error(
            "✗ Channel %s tidak ditemukan. Hapus dengan !stop %s",
            channel_id, channel_id,
        )
    except discord.HTTPException as exc:
        logger.error(
            "✗ HTTP error saat kirim ke channel %s: %s (status %s)",
            channel_id, exc.text, exc.status,
        )
    except Exception:  # noqa: BLE001
        logger.exception("✗ Error tak terduga saat kirim ke channel %s", channel_id)
