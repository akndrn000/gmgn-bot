"""
commands.py — Parser dan handler perintah.

Semua respons dikirim lewat send() dari embeds.py yang otomatis memilih
format teks kotak (self-bot) atau Discord Embed (bot resmi).
"""

from __future__ import annotations

import asyncio
import logging
import random
import re

import discord

from .embeds import (
    msg_error,
    msg_gm,
    msg_gn,
    msg_list,
    msg_menu,
    msg_set_duplicate,
    msg_set_success,
    msg_stop_success,
    msg_test_done,
    msg_test_sending,
    msg_time_success,
    msg_warning,
    send,
)
from .messages import pick_gm, pick_gn
from .storage import load as load_config
from .storage import save as save_config

logger = logging.getLogger(__name__)

_TIME_RE = re.compile(
    r"gm\s*:\s*(\d{1,2})[.:](\d{2})\s*,\s*gn\s*:\s*(\d{1,2})[.:](\d{2})",
    re.IGNORECASE,
)


async def handle_command(client: discord.Client, message: discord.Message) -> None:
    parts = message.content.strip().split()
    cmd = parts[0].lower()

    handlers = {
        "!menu": _cmd_menu,
        "!set":  _cmd_set,
        "!time": _cmd_time,
        "!list": _cmd_list,
        "!stop": _cmd_stop,
        "!test": _cmd_test,
    }

    handler = handlers.get(cmd)
    if handler is None:
        await send(
            message.channel,
            msg_warning(f"Perintah `{cmd}` tidak dikenal.\nKetik `!menu` untuk daftar perintah."),
        )
        return

    await handler(client, message, parts[1:])


# ── !menu ─────────────────────────────────────────────────────────────────────

async def _cmd_menu(
    _client: discord.Client, message: discord.Message, _args: list[str]
) -> None:
    await send(message.channel, msg_menu())


# ── !set ──────────────────────────────────────────────────────────────────────

async def _cmd_set(
    _client: discord.Client, message: discord.Message, args: list[str]
) -> None:
    if not args:
        await send(message.channel, msg_error("Penggunaan: `!set <channel_id> [channel_id ...]`"))
        return

    valid_ids: list[int] = []
    invalid: list[str] = []
    for arg in args:
        if arg.isdigit():
            valid_ids.append(int(arg))
        else:
            invalid.append(arg)

    if invalid:
        await send(
            message.channel,
            msg_warning(f"ID tidak valid (harus angka): `{'`, `'.join(invalid)}`"),
        )
        if not valid_ids:
            return

    config = load_config()
    existing = set(config["target_channels"])
    new_ids = [i for i in valid_ids if i not in existing]

    if not new_ids:
        await send(message.channel, msg_set_duplicate())
        return

    config["target_channels"] = sorted(existing | set(new_ids))
    save_config(config)
    await send(message.channel, msg_set_success(new_ids, len(config["target_channels"])))


# ── !time ─────────────────────────────────────────────────────────────────────

async def _cmd_time(
    _client: discord.Client, message: discord.Message, args: list[str]
) -> None:
    raw = " ".join(args)
    match = _TIME_RE.search(raw)

    if not match:
        await send(message.channel, msg_error("Format salah.\nContoh: `!time gm:07.00, gn:21.00`"))
        return

    gm_h, gm_m, gn_h, gn_m = (int(x) for x in match.groups())

    errors: list[str] = []
    if not 0 <= gm_h <= 23: errors.append(f"Jam GM harus 0–23, dapat: {gm_h}")
    if not 0 <= gm_m <= 59: errors.append(f"Menit GM harus 0–59, dapat: {gm_m}")
    if not 0 <= gn_h <= 23: errors.append(f"Jam GN harus 0–23, dapat: {gn_h}")
    if not 0 <= gn_m <= 59: errors.append(f"Menit GN harus 0–59, dapat: {gn_m}")

    if errors:
        await send(message.channel, msg_error("\n".join(errors)))
        return

    config = load_config()
    config["gm_hour"]   = gm_h
    config["gm_minute"] = gm_m
    config["gn_hour"]   = gn_h
    config["gn_minute"] = gn_m
    save_config(config)
    await send(message.channel, msg_time_success(gm_h, gm_m, gn_h, gn_m))


# ── !list ─────────────────────────────────────────────────────────────────────

async def _cmd_list(
    _client: discord.Client, message: discord.Message, _args: list[str]
) -> None:
    config = load_config()
    await send(
        message.channel,
        msg_list(
            channels=config.get("target_channels", []),
            gm_h=config.get("gm_hour", 7),
            gm_m=config.get("gm_minute", 0),
            gn_h=config.get("gn_hour", 21),
            gn_m=config.get("gn_minute", 0),
        ),
    )


# ── !stop ─────────────────────────────────────────────────────────────────────

async def _cmd_stop(
    _client: discord.Client, message: discord.Message, args: list[str]
) -> None:
    if not args:
        await send(message.channel, msg_error("Penggunaan: `!stop <channel_id> [channel_id ...]`"))
        return

    valid_ids: list[int] = []
    invalid: list[str] = []
    for arg in args:
        if arg.isdigit():
            valid_ids.append(int(arg))
        else:
            invalid.append(arg)

    if invalid:
        await send(message.channel, msg_warning(f"ID tidak valid: `{'`, `'.join(invalid)}`"))
        if not valid_ids:
            return

    config = load_config()
    existing = set(config["target_channels"])
    not_found = [i for i in valid_ids if i not in existing]
    to_remove = [i for i in valid_ids if i in existing]

    if not_found:
        nf_str = ", ".join(f"`{i}`" for i in not_found)
        await send(message.channel, msg_warning(f"ID berikut tidak ada di daftar: {nf_str}"))

    if not to_remove:
        return

    config["target_channels"] = sorted(existing - set(to_remove))
    save_config(config)
    await send(message.channel, msg_stop_success(to_remove, len(config["target_channels"])))


# ── !test ─────────────────────────────────────────────────────────────────────

async def _cmd_test(
    client: discord.Client, message: discord.Message, args: list[str]
) -> None:
    if not args or args[0].lower() not in ("gm", "gn"):
        await send(message.channel, msg_error("Penggunaan: `!test gm` atau `!test gn`"))
        return

    kind = args[0].lower()
    config = load_config()
    targets: list[int] = config.get("target_channels", [])

    if not targets:
        await send(
            message.channel,
            msg_warning("Daftar target channel kosong.\nTambahkan dulu dengan `!set <id>`."),
        )
        return

    await send(message.channel, msg_test_sending(kind, len(targets)))

    sent = 0
    failed = 0

    for channel_id in targets:
        try:
            ch = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
            if hasattr(ch, "send"):
                msg = pick_gm() if kind == "gm" else pick_gn()
                content = msg_gm(msg.text, msg.rarity) if kind == "gm" else msg_gn(msg.text, msg.rarity)
                await send(ch, content)
                sent += 1
            else:
                failed += 1
        except Exception:
            logger.exception("Gagal kirim test ke %s", channel_id)
            failed += 1
        await asyncio.sleep(random.uniform(2, 8))  # noqa: S311

    await send(message.channel, msg_test_done(kind, sent, failed))
