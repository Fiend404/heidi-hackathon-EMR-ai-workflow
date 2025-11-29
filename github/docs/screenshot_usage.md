Camoufox Screenshot Functions

These functions capture screenshots of pages and elements.

---

Page Screenshot
---------------

page.screenshot(path, type, full_page, clip, quality, omitBackground, animations, caret, scale, mask, maskColor, style, timeout)
    Captures a screenshot of the page.

    Parameters:
        path (str, optional): File path to save the screenshot
        type (str, optional): "png" or "jpeg"
        full_page (bool, optional): Capture entire scrollable page
        clip (dict, optional): Region to capture {"x", "y", "width", "height"}
        quality (int, optional): JPEG quality 0-100 (only for jpeg)
        omitBackground (bool, optional): Transparent background for png
        animations (str, optional): "allow" or "disabled"
        caret (str, optional): "hide" or "initial"
        scale (str, optional): "css" or "device"
        mask (list, optional): Locators to mask in screenshot
        maskColor (str, optional): Color for masked elements
        style (str, optional): CSS to inject before screenshot
        timeout (float, optional): Maximum wait time

    Returns:
        bytes: Screenshot image data

<screenshot_basic_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.screenshot(path="screenshot.png")

asyncio.run(main())
EOF
</screenshot_basic_example>
```

<screenshot_fullpage_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.screenshot(path="full.png", full_page=True)

asyncio.run(main())
EOF
</screenshot_fullpage_example>
```

<screenshot_clip_region_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.screenshot(
            path="region.png",
            clip={"x": 0, "y": 0, "width": 800, "height": 600}
        )

asyncio.run(main())
EOF
</screenshot_clip_region_example>
```

<screenshot_jpeg_quality_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.screenshot(
            path="photo.jpg",
            type="jpeg",
            quality=80
        )

asyncio.run(main())
EOF
</screenshot_jpeg_quality_example>
```

<screenshot_as_bytes_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        screenshot_bytes = await page.screenshot(type="png")
        print(f"Screenshot size: {len(screenshot_bytes)} bytes")

asyncio.run(main())
EOF
</screenshot_as_bytes_example>
```

---

Element Screenshot
------------------

locator.screenshot(path, type, quality, omitBackground, animations, caret, scale, mask, maskColor, style, timeout)
    Captures a screenshot of a specific element.

    Parameters:
        path (str, optional): File path to save the screenshot
        type (str, optional): "png" or "jpeg"
        quality (int, optional): JPEG quality 0-100
        omitBackground (bool, optional): Transparent background
        animations (str, optional): "allow" or "disabled"
        caret (str, optional): "hide" or "initial"
        scale (str, optional): "css" or "device"
        mask (list, optional): Locators to mask
        maskColor (str, optional): Mask color
        style (str, optional): CSS to inject
        timeout (float, optional): Maximum wait time

    Returns:
        bytes: Screenshot image data

<screenshot_element_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.locator("h1").screenshot(path="heading.png")

asyncio.run(main())
EOF
</screenshot_element_example>
```

<screenshot_element_jpeg_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.locator("form").screenshot(
            path="form.jpg",
            type="jpeg",
            quality=90
        )

asyncio.run(main())
EOF
</screenshot_element_jpeg_example>
```

<screenshot_element_bytes_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        element_bytes = await page.locator("div.hero").screenshot()
        print(f"Element screenshot: {len(element_bytes)} bytes")

asyncio.run(main())
EOF
</screenshot_element_bytes_example>
```

---

Complete Workflow Example
-------------------------

<screenshot_complete_workflow_example>
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

        await page.screenshot(path="viewport.png")

        await page.screenshot(path="full_page.png", full_page=True)

        await page.screenshot(
            path="top_section.png",
            clip={"x": 0, "y": 0, "width": 1280, "height": 400}
        )

        await page.locator("h1").screenshot(path="heading.png")

        screenshot_data = await page.screenshot(type="png")
        print(f"Screenshot size: {len(screenshot_data)} bytes")

asyncio.run(main())
EOF
</screenshot_complete_workflow_example>
```
