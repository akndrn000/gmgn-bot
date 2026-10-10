"""
client.py — Pembuatan client Discord dan event handler.

Mendukung dua mode otomatis (lihat embeds.py):
  • Self-bot  → respons teks kotak dalam blok kode
  • Bot resmi → respons Discord Embed
"""

from __future__ import annotations

import logging

import discord

from . import settings
from .commands import handle_command
from .embeds import msg_bot_online, msg_error, send
from .scheduler import start_scheduler

logger = logging.getLogger(__name__)


def create_client() -> discord.Client:
    """Buat dan konfigurasikan instance discord.Client."""

    client = discord.Client()

    @client.event
    async def on_ready() -> None:
        username = str(client.user) if client.user else "Unknown"
        logger.info("Bot siap. Login sebagai: %s", username)
        logger.info("Monitor channel ID: %s", settings.MONITOR_CHANNEL_ID)

        # ── Kirim notifikasi BOT ONLINE ke monitor channel ──────────────────
        try:
            channel = client.get_channel(settings.MONITOR_CHANNEL_ID)
            if channel is None:
                channel = await client.fetch_channel(settings.MONITOR_CHANNEL_ID)
            if hasattr(channel, "send"):
                await send(channel, msg_bot_online(username))
                logger.info(
                    "Notifikasi BOT ONLINE terkirim ke channel %s",
                    settings.MONITOR_CHANNEL_ID,
                )
            else:
                logger.warning(
                    "Monitor channel %s tidak bisa menerima pesan.",
                    settings.MONITOR_CHANNEL_ID,
                )
        except Exception:
            logger.exception("Gagal kirim notifikasi BOT ONLINE.")

        await start_scheduler(client)

    @client.event
    async def on_disconnect() -> None:
        logger.warning("Bot disconnect dari Discord. Menunggu reconnect otomatis...")

    @client.event
    async def on_resumed() -> None:
        logger.info("Koneksi Discord berhasil dilanjutkan (resumed).")

    @client.event
    async def on_error(event: str, *args, **kwargs) -> None:  # noqa: ANN002
        logger.exception("Unhandled error di event '%s'", event)

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.channel.id != settings.MONITOR_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content.startswith("!"):
            return

        logger.info("Perintah diterima: %s", content)
        try:
            await handle_command(client, message)
        except Exception:  # noqa: BLE001
            logger.exception("Error saat memproses perintah: %s", content)
            try:
                await send(message.channel, msg_error("Terjadi error saat memproses perintah."))
            except Exception:  # noqa: BLE001
                pass

    return client
