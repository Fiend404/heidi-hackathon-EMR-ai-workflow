#!/usr/bin/env python3
"""
Camoufox Client Connector

Connects to a running camoufox server and demonstrates browser control.

Usage:
    uv run python connect_client.py ws://127.0.0.1:XXXXX
    uv run python connect_client.py ws://127.0.0.1:XXXXX --url https://google.com
"""

import argparse
import asyncio
from playwright.async_api import async_playwright


async def run_demo(ws_endpoint: str, target_url: str):
    print("=" * 50)
    print("CAMOUFOX CLIENT")
    print("=" * 50)
    print(f"Connecting to: {ws_endpoint}")

    async with async_playwright() as p:
        browser = await p.firefox.connect(ws_endpoint)
        print("Connected to browser!")

        context = await browser.new_context()
        page = await context.new_page()

        print(f"\n[1] Navigating to {target_url}...")
        await page.goto(target_url)
        await page.wait_for_load_state("networkidle")
        print("    Page loaded!")

        print("\n[2] TESTING: Cursor Navigation + Click")
        h1 = page.locator("h1")
        if await h1.count() > 0:
            await h1.hover()
            print("    - Hovered over H1")
            box = await h1.bounding_box()
            if box:
                await page.mouse.move(box["x"], box["y"], steps=15)
                print(f"    - Moved cursor to ({box['x']:.0f}, {box['y']:.0f})")
            await h1.click(delay=30)
            print("    - Clicked H1")
        else:
            print("    - No H1 found, clicking body")
            await page.click("body")
        print("    SUCCESS!")

        print("\n[3] TESTING: JavaScript Execution")
        title = await page.evaluate("document.title")
        print(f"    - document.title = '{title}'")

        result = await page.evaluate("([a, b]) => a + b", [10, 20])
        print(f"    - JS calculation 10 + 20 = {result}")

        await page.evaluate("""
            () => {
                const banner = document.createElement('div');
                banner.id = 'client-banner';
                banner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:green;color:white;padding:10px;z-index:9999;text-align:center;';
                banner.textContent = 'Connected via Camoufox Server!';
                document.body.prepend(banner);
            }
        """)
        print("    - Injected banner via JS")
        print("    SUCCESS!")

        await asyncio.sleep(1)

        print("\n[4] TESTING: Screenshot")
        screenshot_path = "client_screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"    - Screenshot saved to: {screenshot_path}")
        print("    SUCCESS!")

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nBrowser connection remains open.")
        print("Press Ctrl+C to disconnect.")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nDisconnecting...")

        await context.close()


def main():
    parser = argparse.ArgumentParser(
        description="Connect to a running camoufox server"
    )
    parser.add_argument(
        "ws_endpoint",
        help="WebSocket endpoint URL (e.g., ws://127.0.0.1:12345)"
    )
    parser.add_argument(
        "--url",
        default="https://example.com",
        help="URL to navigate to (default: https://example.com)"
    )

    args = parser.parse_args()

    if not args.ws_endpoint:
        parser.print_help()
        return

    asyncio.run(run_demo(args.ws_endpoint, args.url))


if __name__ == "__main__":
    main()
