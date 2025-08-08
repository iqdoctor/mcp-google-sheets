# How to Build a Python MCP Server (uv/uvx + hatchling)

This guide explains how to replicate the structure, tooling, and best practices of this repository to build another MCP server (e.g., a VoiceBot server in `../voice`).

It standardizes on:

- Python ≥ 3.10
- `uv`/`uvx` for running and distributing
- `hatchling` + `uv-dynamic-versioning` for builds and versions
- `mcp>=1.5.0` with `FastMCP` for the server

---

## 1) Reference Project Layout

```
<repo-root>/
├─ LICENSE
├─ README.md
├─ pyproject.toml
├─ uv.lock                  # resolved dependency lockfile (optional to commit)
├─ src/
│  └─ <package_name>/
│     ├─ __init__.py       # exposes main() and imports server
│     └─ server.py         # FastMCP server implementation
├─ docs/
│  └─ how_to_bulid_py_mcp.md
└─ .python-version          # optional, e.g., 3.11
```

Notes:

- Keep everything under `src/` with a proper Python package name, e.g., `mcp_google_sheets` or `mcp_voicebot`.
- Expose a console script via `[project.scripts]` in `pyproject.toml` so `uvx <package>@latest` runs the server.

---

## 2) Tooling Summary (What and Why)

- __uv / uvx__: ultra-fast package manager and runner.
  - `uv run <script>` runs your local project.
  - `uvx <package>@latest` runs the latest published version without cloning.
- __hatchling__: modern PEP 517 build backend.
- __uv-dynamic-versioning__: derive versions from VCS tags automatically.
- __mcp>=1.5.0__: official Model Context Protocol Python SDK, includes `FastMCP`.

---

## 3) Clean pyproject.toml Template

Replace placeholders: `<your-dist-name>`, `<your-import-package>`, `<your-name>`, `<your-email>`, and URLs.

```toml
[build-system]
requires = ["hatchling", "uv-dynamic-versioning"]
build-backend = "hatchling.build"

[project]
name = "<your-dist-name>"
dynamic = ["version"]
description = "An MCP server for <service-name>"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.5.0",
]

[[project.authors]]
name = "<your-name>"
email = "<your-email>"

[project.urls]
Homepage = "https://github.com/your-org/your-repo"
Repository = "https://github.com/your-org/your-repo.git"
Bug Tracker = "https://github.com/your-org/your-repo/issues"

[project.scripts]
<your-dist-name> = "<your-import-package>:main"

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.uv-dynamic-versioning]
pattern = "default"
strict = true
```

Add service-specific dependencies under `dependencies = []` as needed (see §7).

---

## 4) Package Skeleton

Create `src/<your-import-package>/__init__.py`:

```python
from . import server
import asyncio

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

__all__ = ["main", "server"]
```

Create `src/<your-import-package>/server.py`:

- Use `FastMCP` from `mcp.server.fastmcp`.
- Define a lifespan manager to initialize any clients, SDKs, or connections.
- Register tools with `@mcp.tool()` and (optionally) resources/prompts.
- Implement `main()` that starts `mcp.run()`.

Minimal example outline:

```python
#!/usr/bin/env python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any
from mcp.server.fastmcp import FastMCP, Context

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    # Initialize SDK clients here
    client = object()
    try:
        yield {"client": client}
    finally:
        pass

mcp = FastMCP("<Service Name>", lifespan=lifespan)

@mcp.tool()
def ping(ctx: Context | None = None) -> str:
    return "pong"

async def main() -> None:
    await mcp.run()
```

---

## 5) Dev Workflow (Local)

- __Install uv__ (if not already):
  - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
- __Run locally__ (from repo root):
  - `uv run <your-dist-name>`
  - Or: `uv run python -m <your-import-package>` if you implement module entry.
- __Lock (optional)__: `uv lock`

Publishing to PyPI allows `uvx <your-dist-name>@latest` usage.

---

## 6) Run via uvx (Users)

After publish to PyPI:

```bash
uvx <your-dist-name>@latest
```

Use `@latest` to avoid old cached versions.

---

## 7) Dependencies ("requirements/needs")

Start minimal and add only what you need. Common sets:

- __Core__
  - `mcp>=1.5.0`
- __Google APIs (example from Sheets server)__
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-api-python-client`
- __Voice / Speech (ideas for a VoiceBot)__
  - Pick one STT/TTS provider and keep the surface small:
    - OpenAI audio: `openai` (if using Realtime or audio APIs)
    - ElevenLabs: `elevenlabs`
    - Google Cloud: `google-cloud-speech`, `google-cloud-texttospeech`
    - Vosk (offline): `vosk`
  - HTTP/WS utilities if needed: `httpx`, `websockets`

Add them to `[project.dependencies]` in `pyproject.toml` and lock with `uv lock`.

---

## 8) Environment Variables & Auth

Document and validate required variables in your server lifespan:

- Example (Sheets): `SERVICE_ACCOUNT_PATH`, `CREDENTIALS_PATH`, `TOKEN_PATH`, `CREDENTIALS_CONFIG`, `GOOGLE_APPLICATION_CREDENTIALS`, `DRIVE_FOLDER_ID`.
- Example (VoiceBot):
  - `VOICEBOT_TTS_API_KEY`
  - `VOICEBOT_STT_API_KEY`
  - `VOICEBOT_MODEL` (e.g., `tts-<provider>-v1`)
  - `VOICEBOT_LANG` (e.g., `en-US`)

Provide sane defaults and clear error messages when missing.

---

## 9) MCP Patterns to Replicate

- __Lifespan__: centralize client creation and cleanup.
- __Context__: access clients via `ctx.request_context.lifespan_context`.
- __Tools__: small, single-purpose functions with clear params and returns. Use structured types (lists/dicts) to keep clients deterministic.
- __Resources (optional)__: expose metadata or static content via `@mcp.resource()` if needed.
- __Logging__: print concise progress and parameter info to aid agent reasoning.

---

## 10) Client Integration (Claude Desktop example)

`claude_desktop_config.json` snippet (Windows/macOS path caveats included):

```json
{
  "mcpServers": {
    "<short-name>": {
      "command": "uvx",
      "args": ["<your-dist-name>@latest"],
      "env": {
        "VOICEBOT_TTS_API_KEY": "...",
        "VOICEBOT_STT_API_KEY": "..."
      }
    }
  }
}
```

If `uvx` isn’t on PATH (macOS): use full path, e.g. `/Users/<you>/.local/bin/uvx`.

---

## 11) Creating a New VoiceBot MCP in `../voice`

Example step-by-step to mirror this repo:

1. __Create repo skeleton__
   - Path: `../voice`
   - Package: `mcp_voicebot`
   - Dist name: `mcp-voicebot`
2. __Files__
   - `README.md`: describe features, env vars, quick start with `uvx mcp-voicebot@latest`.
   - `pyproject.toml`: use the template in §3 and add needed deps (see §7).
   - `src/mcp_voicebot/__init__.py`: per §4.
   - `src/mcp_voicebot/server.py`: implement lifespan and tools:
     - `synthesize_speech(text, voice, speed, format)`
     - `transcribe_audio(file_url|bytes, language)`
     - `list_voices()`
     - Keep parameters stringly-typed or simple types for robustness.
3. __Local run__
   - From `../voice`: `uv run mcp-voicebot`
4. __Test via Claude Desktop__
   - Add config from §10 with your environment variables.
5. __Publish (optional)__
   - Build: `uv build`
   - Upload: `uv publish` (requires PyPI creds)

---

## 12) Versioning & Releases

- Tag in git (e.g., `v0.1.0`), `uv-dynamic-versioning` will produce the version at build time.
- CI can run `uv build` on tags and publish to PyPI.

---

## 13) Quality of Life (Optional)

- __Pre-commit__: formatters/linters (ruff, black, isort, mypy).
- __.python-version__: pin local Python, e.g., `3.11`.
- __.markdownlint.jsonc__: for docs style.
- __Logging__: prefer structured, but `print(...)` is acceptable for MCP agent logs.

---

## 14) Quick Checklist

- __Project__
  - `pyproject.toml` uses `hatchling` + `uv-dynamic-versioning`.
  - `[project.scripts]` exposes console entry.
  - `src/<package>/server.py` with `FastMCP` and tools.
  - `src/<package>/__init__.py` defines `main()`.
- __Tooling__
  - `uv` installed; `uv run` works locally.
  - (Optional) Publish -> `uvx <dist>@latest` works.
- __Docs__
  - README quick start + env vars.
  - This guide copied to `docs/how_to_bulid_py_mcp.md`.

You can copy this file and the `pyproject.toml` template into a new project to bootstrap an MCP server with nearly identical tooling and layout.
