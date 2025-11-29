Camoufox Persistent State Analysis

Problem
When using Playwright's WebSocket connection to a browser server, each connection is ISOLATED:
- Connection A creates Context A with Page A
- Connection B cannot see Context A - it gets a fresh view
- This is by design in Playwright - contexts are scoped to the connection

Solutions

1. Single Script Approach (Recommended for sequential tasks)
   - One script does everything: login → extract → save
   - State naturally persists within the script execution
   - Best for: Tasks that can be completed in one session

2. Storage State Export/Import
   - Script 1: Login, export cookies/localStorage via context.storage_state(path="state.json")
   - Script 2: Load state via browser.new_context(storage_state="state.json")
   - Preserves: Authentication (cookies, tokens)
   - Does NOT preserve: Current page URL, DOM state, JavaScript variables
   - Best for: Multi-session workflows where auth is expensive

3. Persistent Browser Profile Directory
   - Configure browser with user data directory
   - Cookies/localStorage saved to disk automatically
   - Each connection loads profile but creates fresh context
   - Preserves: Authentication
   - Does NOT preserve: Page state
   - Best for: Long-running automation across days/weeks

4. Server-Managed Context via IPC (Advanced)
   - Server process creates and owns the context forever
   - Client scripts send commands via socket/file/queue
   - Server executes on behalf of clients, returns results
   - Preserves: Everything (full page state)
   - Complexity: High - requires custom protocol
   - Best for: Complex multi-script workflows needing true state sharing

Implementation: Storage State Approach

Script 1 - Login and Save State:
```python
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

WS_URL = Path(".camoufox_ws_url").read_text().strip()

async def login_and_save():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # Login
        await page.goto("https://demo.openemr.io/openemr/interface/login/login.php?site=default")
        await page.fill('input[name="authUser"]', 'admin')
        await page.fill('input[name="clearPass"]', 'pass')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # Save storage state (cookies, localStorage)
        await context.storage_state(path="browser_state.json")
        print(f"State saved! Current URL: {page.url}")

asyncio.run(login_and_save())
```

Script 2 - Load State and Continue:
```python
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

WS_URL = Path(".camoufox_ws_url").read_text().strip()

async def continue_with_state():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)

        # Load saved state - cookies will be restored
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            storage_state="browser_state.json"
        )
        page = await context.new_page()

        # Navigate to app - should be auto-authenticated
        await page.goto("https://demo.openemr.io/openemr/interface/main/tabs/main.php")
        await page.wait_for_load_state("networkidle")

        print(f"Restored session! URL: {page.url}")
        # Continue with extraction...

asyncio.run(continue_with_state())
```

Key Insight
The browser server (camoufox) is just a headless browser waiting for connections.
Playwright connections are like separate browser profiles - they don't share state.
To share state across scripts, you must EXPORT it (to file) and IMPORT it (in next script).

Recommendation for OpenEMR Task
Use the Storage State approach:
1. Script 1: Login, save state to browser_state.json
2. Script 2: Load state, extract menus, save to JSON
3. Both scripts can run independently, auth persists via saved cookies
