#!/usr/bin/env python3
"""
Camoufox Server Launcher with Persistent State

Starts a camoufox browser and maintains a persistent context/page.
The server keeps the browser connection alive so state persists across script executions.

Usage:
    uv run python start_server.py
    uv run python start_server.py --headless
"""

import argparse
import asyncio
import base64
import re
import secrets
import signal
import subprocess
import sys
from pathlib import Path

import orjson
from playwright._impl._driver import compute_driver_executable
from playwright.async_api import async_playwright

from camoufox.pkgman import LOCAL_DATA
from camoufox.utils import launch_options


LAUNCH_SCRIPT: Path = LOCAL_DATA / "launchServer.js"
WS_URL_FILE = Path(__file__).parent / ".camoufox_ws_url"
SESSION_ID_FILE = Path(__file__).parent / ".camoufox_session_id"
WS_URL = None
SESSION_ID = None


def camel_case(snake_str: str) -> str:
    if len(snake_str) < 2:
        return snake_str
    camel_case_str = ''.join(x.capitalize() for x in snake_str.lower().split('_'))
    return camel_case_str[0].lower() + camel_case_str[1:]


def to_camel_case_dict(data: dict) -> dict:
    return {camel_case(key): value for key, value in data.items()}


def get_nodejs() -> str:
    _nodejs = compute_driver_executable()[0]
    if isinstance(_nodejs, tuple):
        return _nodejs[0]
    return _nodejs


def cleanup(signum, frame):
    print("\n[SHUTDOWN] Cleaning up...", flush=True)
    if WS_URL_FILE.exists():
        WS_URL_FILE.unlink()
    if SESSION_ID_FILE.exists():
        SESSION_ID_FILE.unlink()
    sys.exit(0)


async def launch_browser(headless: bool = False):
    """Launch camoufox browser and return WebSocket URL."""
    config = launch_options(headless=headless)

    if 'proxy' in config and config['proxy'] is None:
        del config['proxy']

    nodejs = get_nodejs()
    data = orjson.dumps(to_camel_case_dict(config))

    process = await asyncio.create_subprocess_exec(
        nodejs, str(LAUNCH_SCRIPT),
        cwd=Path(nodejs).parent / "package",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if process.stdin:
        process.stdin.write(base64.b64encode(data))
        await process.stdin.drain()
        process.stdin.close()

    ws_pattern = re.compile(r'(ws://localhost:\d+/[a-f0-9]+)')

    print("[STEP 1] Launching browser...", flush=True)

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        line_str = line.decode()
        print(line_str, end='', flush=True)

        match = ws_pattern.search(line_str)
        if match:
            return match.group(1), process

    return None, process


async def main(headless: bool = False):
    global WS_URL, SESSION_ID

    # Generate session ID
    SESSION_ID = secrets.token_hex(16)
    SESSION_ID_FILE.write_text(SESSION_ID)

    print("=" * 50, flush=True)
    print("CAMOUFOX SERVER WITH PERSISTENT STATE", flush=True)
    print("=" * 50, flush=True)
    print(f"Headless: {headless}", flush=True)
    print("=" * 50, flush=True)
    print(f"SESSION_ID = \"{SESSION_ID}\"", flush=True)
    print("=" * 50, flush=True)

    # Launch browser
    WS_URL, browser_process = await launch_browser(headless)

    if not WS_URL:
        print("[ERROR] Failed to capture WebSocket URL", flush=True)
        return

    print(f"\n[STEP 2] WebSocket URL: {WS_URL}", flush=True)
    WS_URL_FILE.write_text(WS_URL)
    print(f"[STEP 3] Saved to {WS_URL_FILE}", flush=True)

    # Connect to browser and create persistent context/page
    print("[STEP 4] Creating persistent context and page...", flush=True)

    p = await async_playwright().start()
    browser = await p.firefox.connect(WS_URL)

    context = await browser.new_context(viewport={"width": 1920, "height": 1080})
    page = await context.new_page()

    print("[STEP 5] Persistent context and page created!", flush=True)
    print("=" * 50, flush=True)
    print("SERVER READY - State will persist across scripts", flush=True)
    print("=" * 50, flush=True)

    # Keep the connection alive forever
    try:
        while True:
            await asyncio.sleep(60)
            # Heartbeat - check if browser is still connected
            try:
                contexts = browser.contexts
                print(f"[HEARTBEAT] {len(contexts)} context(s), page URL: {page.url}", flush=True)
            except Exception as e:
                print(f"[ERROR] Browser disconnected: {e}", flush=True)
                break
    except asyncio.CancelledError:
        print("[SHUTDOWN] Server stopping...", flush=True)
    finally:
        await p.stop()
        if WS_URL_FILE.exists():
            WS_URL_FILE.unlink()
        if SESSION_ID_FILE.exists():
            SESSION_ID_FILE.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch camoufox with persistent state")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    asyncio.run(main(headless=args.headless))
