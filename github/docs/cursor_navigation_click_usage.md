Camoufox Cursor Navigation and Click Functions

These functions provide realistic mouse movement and clicking for browser automation.

---

Low-Level Mouse Control
-----------------------

page.mouse.move(x, y, steps)
    Moves the mouse cursor to coordinates with optional interpolation steps.

    Parameters:
        x (float): Target X coordinate
        y (float): Target Y coordinate
        steps (int, optional): Number of intermediate steps for realistic movement

<cursor_move_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.mouse.move(500, 300, steps=20)

asyncio.run(main())
EOF
</cursor_move_example>
```


page.mouse.click(x, y, delay, button, clickCount)
    Clicks at specific coordinates.

    Parameters:
        x (float): X coordinate to click
        y (float): Y coordinate to click
        delay (float, optional): Delay in ms between mousedown and mouseup
        button (str, optional): "left", "right", or "middle"
        clickCount (int, optional): Number of clicks (2 for double-click)

<cursor_click_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.mouse.click(500, 300, delay=50, button="left")

asyncio.run(main())
EOF
</cursor_click_example>
```


page.mouse.dblclick(x, y, delay, button)
    Double-clicks at specific coordinates.

<cursor_dblclick_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.mouse.dblclick(500, 300, delay=30)

asyncio.run(main())
EOF
</cursor_dblclick_example>
```

---

High-Level Locator Methods
--------------------------

locator.hover()
    Moves cursor to element center with realistic movement.

    Parameters:
        modifiers (list, optional): Keyboard modifiers ["Alt", "Control", "Meta", "Shift"]
        position (dict, optional): Offset within element {"x": 5, "y": 5}
        timeout (float, optional): Maximum wait time in ms
        force (bool, optional): Skip actionability checks
        trial (bool, optional): Only scroll into view, don't hover

<locator_hover_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.locator("button.submit").hover()
        await page.locator("a.menu").hover(position={"x": 10, "y": 5})

asyncio.run(main())
EOF
</locator_hover_example>
```


locator.click()
    Clicks on element with auto-scroll and visibility waiting.

    Parameters:
        modifiers (list, optional): Keyboard modifiers
        position (dict, optional): Offset within element
        delay (float, optional): Delay between mousedown/mouseup in ms
        button (str, optional): Mouse button
        clickCount (int, optional): Number of clicks
        timeout (float, optional): Maximum wait time
        force (bool, optional): Skip actionability checks
        noWaitAfter (bool, optional): Don't wait for navigation
        trial (bool, optional): Only scroll into view, don't click

<locator_click_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.locator("button.submit").click(delay=50)
        await page.locator("input").click(position={"x": 0, "y": 0}, clickCount=3)

asyncio.run(main())
EOF
</locator_click_example>
```

---

Complete Workflow Example
-------------------------

<cursor_complete_workflow_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.goto("https://example.com")

        button = page.locator("a")
        box = await button.bounding_box()

        await page.mouse.move(100, 100)
        await page.mouse.move(box["x"], box["y"], steps=20)

        await button.hover()
        await asyncio.sleep(0.3)

        await button.click(delay=50)

asyncio.run(main())
EOF
</cursor_complete_workflow_example>
```
