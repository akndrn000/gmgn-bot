"""
embeds.py — Respons pesan bot GM/GN.

Mendukung dua mode otomatis:
  • Self-bot  (DISCORD_USER_TOKEN tanpa awalan 'Bot') → teks kotak dalam blok kode
  • Bot resmi (token dengan awalan 'Bot')              → Discord Embed dengan warna

Mode dipilih otomatis lewat is_selfbot() saat modul pertama kali diimport.
"""

from __future__ import annotations

import os
from datetime import datetime

import discord


# ── Deteksi mode ─────────────────────────────────────────────────────────────

def is_selfbot() -> bool:
    """True jika token adalah user token (self-bot), bukan bot resmi."""
    token = os.environ.get("DISCORD_USER_TOKEN", "").strip()
    return not token.startswith("Bot ")


_SELFBOT = is_selfbot()

FOOTER = "GM/GN Bot • Railway"


# ── Warna embed (hanya dipakai mode bot resmi) ───────────────────────────────

COLOR_GREEN  = 0x2ECC71
COLOR_RED    = 0xE74C3C
COLOR_BLUE   = 0x3498DB
COLOR_ORANGE = 0xE67E22
COLOR_GOLD   = 0xF1C40F
COLOR_PURPLE = 0x9B59B6

COLOR_GM_COMMON = 0xF9CA24
COLOR_GM_RARE   = 0xF0932B
COLOR_GM_EPIC   = 0x6AB04C

COLOR_GN_COMMON = 0x4834D4
COLOR_GN_RARE   = 0x686DE0
COLOR_GN_EPIC   = 0x30336B


# ── Helper ───────────────────────────────────────────────────────────────────

def _footer(embed: discord.Embed) -> discord.Embed:
    embed.timestamp = datetime.utcnow()
    embed.set_footer(text=FOOTER)
    return embed


def _ts() -> str:
    """Timestamp singkat untuk teks kotak."""
    return datetime.now().strftime("%H:%M")


def _box(*lines: str) -> str:
    """Bungkus baris-baris teks dalam blok kode Discord (``` ... ```)."""
    body = "\n".join(lines)
    return f"```\n{body}\n```"


# ── Notifikasi startup ────────────────────────────────────────────────────────

def msg_bot_online(username: str) -> str | discord.Embed:
    if _SELFBOT:
        return _box(
            "🤖  BOT GM/GN — ONLINE",
            "─" * 30,
            f"Login sebagai : {username}",
            f"Waktu         : {_ts()}",
            "Scheduler     : aktif",
            "─" * 30,
            "Ketik !menu untuk daftar perintah",
            "Ketik !list untuk konfigurasi aktif",
        )
    embed = discord.Embed(
        title="🤖  BOT GM/GN AUTOMATION — ONLINE",
        description=(
            f"Bot berhasil terhubung sebagai **{username}**.\n"
            "Scheduler aktif dan siap mengirim pesan terjadwal."
        ),
        color=COLOR_GREEN,
    )
    embed.add_field(
        name="━" * 30,
        value=(
            "Ketik **`!menu`** untuk melihat daftar perintah.\n"
            "Ketik **`!list`** untuk melihat konfigurasi aktif."
        ),
        inline=False,
    )
    return _footer(embed)


# ── Menu bantuan ──────────────────────────────────────────────────────────────

def msg_menu() -> str | discord.Embed:
    if _SELFBOT:
        return _box(
            "📌  MENU PERINTAH",
            "─" * 42,
            "!set <id1> <id2>        : Tambah channel target",
            "!time gm:07.00,gn:21.00 : Atur jadwal GM dan GN",
            "!list                   : Tampilkan konfigurasi aktif",
            "!stop <id>              : Hapus channel dari daftar",
            "!test gm / !test gn     : Kirim tes manual sekarang",
            "!menu                   : Tampilkan menu ini",
        )
    embed = discord.Embed(
        title="📌  MENU PERINTAH",
        description="Semua perintah hanya aktif di channel monitor ini.",
        color=COLOR_BLUE,
    )
    embed.add_field(name="📥  Kelola Target", value="`!set <id1> <id2>`\nTambah channel target.", inline=False)
    embed.add_field(name="⏰  Atur Jadwal",   value="`!time gm:07.00, gn:19.00`\nAtur jam GM dan GN.",  inline=False)
    embed.add_field(name="📋  Lihat Config",  value="`!list`\nTampilkan daftar target & jadwal.", inline=False)
    embed.add_field(name="🗑️  Hapus Target",  value="`!stop <id>`\nHapus channel dari daftar.",      inline=False)
    embed.add_field(name="🧪  Tes Manual",    value="`!test gm`  atau  `!test gn`\nKirim sekarang ke semua target.", inline=False)
    embed.add_field(name="❓  Bantuan",       value="`!menu`\nTampilkan menu ini.",                  inline=False)
    return _footer(embed)


# ── Hasil !set ────────────────────────────────────────────────────────────────

def msg_set_success(new_ids: list[int], total: int) -> str | discord.Embed:
    if _SELFBOT:
        id_list = "\n".join(f"  + {i}" for i in new_ids)
        return _box(
            "✅  Channel Berhasil Ditambahkan",
            "─" * 30,
            id_list,
            "─" * 30,
            f"Total target : {total} channel",
        )
    embed = discord.Embed(title="✅  Channel Berhasil Ditambahkan", color=COLOR_GREEN)
    embed.add_field(name="Channel Baru", value="\n".join(f"`{i}`" for i in new_ids), inline=True)
    embed.add_field(name="Total Target", value=f"**{total}** channel", inline=True)
    return _footer(embed)


def msg_set_duplicate() -> str | discord.Embed:
    if _SELFBOT:
        return _box(
            "ℹ️  Tidak Ada Perubahan",
            "─" * 30,
            "Semua ID sudah ada di daftar.",
        )
    embed = discord.Embed(
        title="ℹ️  Tidak Ada Perubahan",
        description="Semua ID yang dimasukkan sudah ada di daftar.",
        color=COLOR_ORANGE,
    )
    return _footer(embed)


# ── Hasil !time ───────────────────────────────────────────────────────────────

def msg_time_success(gm_h: int, gm_m: int, gn_h: int, gn_m: int) -> str | discord.Embed:
    if _SELFBOT:
        return _box(
            "⏰  Jadwal Berhasil Diperbarui",
            "─" * 30,
            f"GM  : {gm_h:02d}:{gm_m:02d}",
            f"GN  : {gn_h:02d}:{gn_m:02d}",
        )
    embed = discord.Embed(title="⏰  Jadwal Berhasil Diperbarui", color=COLOR_PURPLE)
    embed.add_field(name="🌅  Waktu GM", value=f"**{gm_h:02d}:{gm_m:02d}**", inline=True)
    embed.add_field(name="🌙  Waktu GN", value=f"**{gn_h:02d}:{gn_m:02d}**", inline=True)
    return _footer(embed)


# ── Hasil !list ───────────────────────────────────────────────────────────────

def msg_list(
    channels: list[int],
    gm_h: int,
    gm_m: int,
    gn_h: int,
    gn_m: int,
) -> str | discord.Embed:
    if _SELFBOT:
        if channels:
            ch_lines = "\n".join(f"  • {c}" for c in channels)
        else:
            ch_lines = "  (kosong — gunakan !set <id>)"
        return _box(
            "📊  Konfigurasi Aktif",
            "─" * 30,
            f"GM  : {gm_h:02d}:{gm_m:02d}",
            f"GN  : {gn_h:02d}:{gn_m:02d}",
            f"Target ({len(channels)}) :",
            ch_lines,
        )
    embed = discord.Embed(title="📊  Konfigurasi Aktif", color=COLOR_GOLD)
    embed.add_field(name="🌅  Waktu GM", value=f"**{gm_h:02d}:{gm_m:02d}**", inline=True)
    embed.add_field(name="🌙  Waktu GN", value=f"**{gn_h:02d}:{gn_m:02d}**", inline=True)
    embed.add_field(
        name=f"📌  Target Channel  ({len(channels)})",
        value=(
            "\n".join(f"`{c}`" for c in channels)
            if channels
            else "_Belum ada channel target.\nGunakan `!set <id>` untuk menambahkan._"
        ),
        inline=False,
    )
    return _footer(embed)


# ── Hasil !stop ───────────────────────────────────────────────────────────────

def msg_stop_success(removed: list[int], remaining: int) -> str | discord.Embed:
    if _SELFBOT:
        id_list = "\n".join(f"  - {i}" for i in removed)
        return _box(
            "🗑️  Channel Berhasil Dihapus",
            "─" * 30,
            id_list,
            "─" * 30,
            f"Sisa target : {remaining} channel",
        )
    embed = discord.Embed(title="🗑️  Channel Berhasil Dihapus", color=COLOR_RED)
    embed.add_field(name="Dihapus",      value="\n".join(f"`{i}`" for i in removed), inline=True)
    embed.add_field(name="Sisa Target",  value=f"**{remaining}** channel",           inline=True)
    return _footer(embed)


# ── Hasil !test ───────────────────────────────────────────────────────────────

def msg_test_sending(kind: str, count: int) -> str | discord.Embed:
    label = "GM 🌅" if kind == "gm" else "GN 🌙"
    if _SELFBOT:
        return _box(
            f"🧪  Mengirim Tes {label}",
            "─" * 30,
            f"Mengirim ke {count} channel target...",
        )
    embed = discord.Embed(
        title=f"🧪  Mengirim Tes {label}",
        description=f"Mengirim ke **{count}** channel target...",
        color=COLOR_PURPLE,
    )
    return _footer(embed)


def msg_test_done(kind: str, sent: int, failed: int) -> str | discord.Embed:
    label = "GM 🌅" if kind == "gm" else "GN 🌙"
    if _SELFBOT:
        return _box(
            f"✅  Tes {label} Selesai",
            "─" * 30,
            f"Berhasil : {sent}",
            f"Gagal    : {failed}",
        )
    color = COLOR_GREEN if failed == 0 else COLOR_ORANGE
    embed = discord.Embed(title=f"✅  Tes {label} Selesai", color=color)
    embed.add_field(name="Berhasil", value=f"**{sent}**",  inline=True)
    embed.add_field(name="Gagal",    value=f"**{failed}**", inline=True)
    return _footer(embed)


# ── Pesan GM / GN ke channel target ──────────────────────────────────────────

def msg_gm(text: str, rarity: str = "common") -> str | discord.Embed:
    if _SELFBOT:
        return f"🌅 {text}"
    color_map = {"common": COLOR_GM_COMMON, "rare": COLOR_GM_RARE, "epic": COLOR_GM_EPIC}
    embed = discord.Embed(
        title="🌅  Good Morning!",
        description=f"## {text}",
        color=color_map.get(rarity, COLOR_GM_COMMON),
    )
    embed.timestamp = datetime.utcnow()
    embed.set_footer(text="GM/GN Bot • Automated")
    return embed


def msg_gn(text: str, rarity: str = "common") -> str | discord.Embed:
    if _SELFBOT:
        return f"🌙 {text}"
    color_map = {"common": COLOR_GN_COMMON, "rare": COLOR_GN_RARE, "epic": COLOR_GN_EPIC}
    embed = discord.Embed(
        title="🌙  Good Night!",
        description=f"## {text}",
        color=color_map.get(rarity, COLOR_GN_COMMON),
    )
    embed.timestamp = datetime.utcnow()
    embed.set_footer(text="GM/GN Bot • Automated")
    return embed


# ── Error / peringatan ────────────────────────────────────────────────────────

def msg_error(description: str) -> str | discord.Embed:
    if _SELFBOT:
        return _box("⚠️  Error", "─" * 30, description)
    embed = discord.Embed(title="⚠️  Error", description=description, color=COLOR_RED)
    return _footer(embed)


def msg_warning(description: str) -> str | discord.Embed:
    if _SELFBOT:
        return _box("⚠️  Peringatan", "─" * 30, description)
    embed = discord.Embed(title="⚠️  Peringatan", description=description, color=COLOR_ORANGE)
    return _footer(embed)


# ── Helper kirim (abstraksi send) ─────────────────────────────────────────────

async def send(channel: discord.abc.Messageable, content: str | discord.Embed) -> None:
    """Kirim str atau Embed ke channel secara transparan."""
    if isinstance(content, str):
        await channel.send(content)
    else:
        await channel.send(embed=content)
