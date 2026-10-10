<div align="center">

<img src="docs/logo.svg" alt="GM/GN Bot" width="96" height="96">

# GM/GN Bot

<p>
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"></a>
  <a href="https://discord.com/"><img alt="Discord" src="https://img.shields.io/badge/Discord-5865F2?style=flat&logo=discord&logoColor=white"></a>
  <a href="Dockerfile"><img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white"></a>
  <a href="https://railway.app/"><img alt="Railway" src="https://img.shields.io/badge/Railway-0B0D0E?style=flat&logo=railway&logoColor=white"></a>
  <a href="https://docs.pytest.org/"><img alt="pytest" src="https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white"></a>
  <a href="https://docs.astral.sh/ruff/"><img alt="Ruff" src="https://img.shields.io/badge/Ruff-D7FF64?style=flat&logo=ruff&logoColor=black"></a>
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=flat"></a>
</p>

<p><a href="README.md">Bahasa Indonesia</a> · <a href="README.en.md">English</a></p>

<p><b>Automatic GM &amp; GN messages for multiple Discord channels.</b> Messages are picked with a rarity system so they look natural, and the schedule and targets are managed through text commands in a single monitor channel. Runs as a worker on Railway, with no dashboard and no database.</p>

<p>
  <a href="#try-it-now">Try it now</a> ·
  <a href="#features">Features</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#input-format">Input format</a> ·
  <a href="#privacy">Privacy</a> ·
  <a href="#development">Development</a> ·
  <a href="#contributing">Contributing</a>
</p>

</div>

---

## Try it now

Three steps from zero to a running bot:

1. **Deploy** this repo to Railway with **Deploy from GitHub repo** ([railway.app/new](https://railway.app/new)).
2. Set three **Variables**: `DISCORD_USER_TOKEN`, `MONITOR_CHANNEL_ID`, `TIMEZONE`, then add a **Volume** mounted at `/data`.
3. Open the monitor channel and type:

```
!set 1234567890 0987654321
!time gm:07.00, gn:19.00
!list
```

That's it: the bot sends `gm` and `gn` to the target channels at the configured times. Full walkthrough in [Usage](#usage).

> **Warning:** this bot automates a user account (self-bot), which violates Discord's Terms of Service. Read [Privacy](#privacy) and [Contributing](#contributing) before using it.

## Features

**Message delivery**

- **Message rarity system**: short messages (`gm` / `gn`) appear most often, while other phrasings show up randomly as variety, so it doesn't look robotic.
- **Multi-channel**: one bot for many target channels at once.
- **Random delay between sends** (*human-like delay*) to avoid looking like spam.
- **Separate GM and GN schedules**, with a configurable timezone via `TIMEZONE` (e.g. `Asia/Jakarta`, `Asia/Makassar`).

**Control and operational safety**

- **Text-command control panel**: `!menu`, `!set`, `!time`, `!list`, `!stop`, `!test`. No code changes or redeploys needed to change targets or schedule.
- **Locked monitor channel**: commands are only answered in the channel set by `MONITOR_CHANNEL_ID`.
- **Persistent configuration** in `/data/config.json` (Railway Volume), kept across restarts and redeploys.

**Code quality**

- Code split by module (settings, storage, messages, scheduler, commands, client).
- Behavior tests with **pytest**, lint and formatting with **Ruff**.
- Production-ready with a **Dockerfile** and **Procfile**.

## Usage

> [!NOTE]
> The bot replies in Indonesian. The screenshots below show an English translation of those replies; the commands themselves are the same.

**1. Deploy and set environment variables.** Follow [Deploy to Railway](#deploy-to-railway). Once running, the bot posts its status in the monitor channel.

![Environment variables on Railway](docs/screenshots/en/railway.svg)

**2. List the commands** with `!menu` in the monitor channel.

![Help menu](docs/screenshots/en/menu.svg)

**3. Add target channels** with `!set` followed by one or more channel IDs, separated by spaces.

![Set targets](docs/screenshots/en/set.svg)

**4. Set the send times** with `!time`. GM and GN times go in a single command.

![Set schedule](docs/screenshots/en/time.svg)

**5. Check the configuration** with `!list` to see the GM and GN times, the target count, and the list of active target IDs.

![Configuration list](docs/screenshots/en/list.svg)

**6. The bot sends messages** to the target channels at the configured times.

![Sent messages](docs/screenshots/en/result.svg)

**7. Remove a target** any time with `!stop 1234567890`.

## Input format

### Commands

All commands **only work in the monitor channel**.

| Command | Purpose | Example |
| ------- | ------- | ------- |
| `!menu` | Show the help guide | `!menu` |
| `!set` | Add one or more target channel IDs | `!set 1234567890 0987654321` |
| `!time` | Set the automatic GM and GN send times | `!time gm:07.00, gn:19.00` |
| `!list` | Show the active configuration and target IDs | `!list` |
| `!stop` | Remove a channel ID from the targets | `!stop 1234567890` |
| `!test` | Send a manual GM or GN test to all targets | `!test gm` |

Quick rules:

- Channel IDs are separated by **spaces** in `!set`.
- Times use a **dot** (`07.00`), and the `gm:` and `gn:` pairs are separated by a **comma** in `!time`.
- To get a channel ID: enable **Developer Mode** in Discord (Settings > Advanced), right-click the channel, choose **Copy Channel ID**.

### Environment variables

A full example is in `.env.example`.

| Variable | Example | Description |
| -------- | ------- | ----------- |
| `DISCORD_USER_TOKEN` | `MTI3...` | Token of the Discord account the bot runs on (**secret**) |
| `MONITOR_CHANNEL_ID` | `123456789012345678` | Channel where the bot posts status and receives commands |
| `TIMEZONE` | `Asia/Jakarta` | Reference timezone for the schedule |

### Storage

Targets and schedule are stored in `/data/config.json`. Make sure `/data` is a **Railway Volume** so the file survives container rebuilds.

## Privacy

- The token is stored **only** in Railway environment variables. Never commit a token; `.env.example` only contains placeholders.
- The bot exposes no web service, uses no database, and has no analytics. The only stored data is `config.json`, containing target channel IDs and the schedule.
- A token is equivalent to your account password. If it leaks, **change the account password** to reset the token.
- Use a **dedicated account**, not your main one.
- This bot automates a user account (self-bot), which **violates Discord's Terms of Service**. The account may be limited or banned. Use at your own risk.

## Development

Requires Python and pip. Run from the repo root.

### Run locally

```
pip install -r requirements.txt
pip install -e .
```

Linux / macOS:

```
export DISCORD_USER_TOKEN=your_token
export MONITOR_CHANNEL_ID=123456789012345678
export TIMEZONE=Asia/Jakarta
python -m gmgn_bot
```

Windows (CMD):

```
set DISCORD_USER_TOKEN=your_token
set MONITOR_CHANNEL_ID=123456789012345678
set TIMEZONE=Asia/Jakarta
python -m gmgn_bot
```

### Tests and lint

```
pip install -r requirements-dev.txt
pytest
ruff check .
ruff format --check .
```

### Run with Docker

```
docker build -t gmgn-bot .
docker run --env-file .env -v gmgn-data:/data gmgn-bot
```

### Deploy to Railway

1. Create a new GitHub repository and push this folder.
2. Open <https://railway.app/>, create a new project, choose **Deploy from GitHub repo**, and connect that repository.
3. In **Variables**, add `DISCORD_USER_TOKEN`, `MONITOR_CHANNEL_ID`, and `TIMEZONE`.
4. Add a **Volume** and mount it at `/data` so `config.json` persists.
5. Railway builds with the `Dockerfile` and runs the worker defined in the `Procfile`.

### Tech stack

- **Python** with a `src/` layout, run via `python -m gmgn_bot`
- **Dockerfile** and **Procfile** for Railway
- **pytest** for behavior tests, **Ruff** for lint and formatting
- Persistent config as a single JSON file, no database

### Folder structure

```
src/gmgn_bot/
  __init__.py           Public package exports
  __main__.py           Entry point: python -m gmgn_bot
  settings.py           Read and validate env vars (single place)
  storage.py            Read/write config.json
  messages.py           Message pool + rarity selection
  scheduler.py          Schedule and periodic sending logic
  commands.py           Parser and handlers for !menu/!set/!time/!list/!stop/!test
  client.py             Discord client setup and thin event handlers
  logging_setup.py      Logging configuration
tests/                  Behavior tests (pytest)
docs/                   Logo and screenshots for the README
.env.example            Example environment variables (no real token)
pyproject.toml          Ruff and pytest configuration
requirements.txt        Runtime dependencies (pinned versions)
requirements-dev.txt    Development dependencies (pytest, ruff)
Dockerfile              Container for Docker/Railway
Procfile                Worker start command
```

### Known limitations

- **Commands only work in the monitor channel**; the bot ignores other channels.
- **Without a Volume, the configuration is lost** when the container is recreated.
- **Account risk**: automated sending through a user account can trigger Discord restrictions, and some servers forbid automated messages. Follow each server's rules.

## Contributing

Contributions are welcome.

1. **Fork** this repo and create a new branch, e.g. `feature/your-feature`.
2. Install dev dependencies: `pip install -r requirements-dev.txt`.
3. Change code in `src/gmgn_bot/` and **add or update tests** in `tests/`.
4. Make sure everything passes before opening a PR:

   ```
   pytest
   ruff check .
   ruff format --check .
   ```

5. Open a **Pull Request** with a short description of what changed and why.

For bugs or feature requests, open an **Issue** with reproduction steps and logs (without tokens).

This project is not affiliated with Discord Inc. Released under the [MIT](LICENSE) license.
