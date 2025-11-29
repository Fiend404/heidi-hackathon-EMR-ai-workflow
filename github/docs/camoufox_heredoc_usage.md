Camoufox HEREDOC Orchestration

Control a persistent camoufox browser instance using HEREDOC + EOF Python scripts.

---

Setup
-----
Terminal 1 - Start Server:

    uv run python start_server.py

Output:

    Websocket endpoint: ws://localhost:XXXXX/token

Save the WebSocket URL for use in HEREDOC scripts.

---

Basic Connection Template
-------------------------

    uv run python3 << 'EOF'
    import asyncio
    from playwright.async_api import async_playwright

    WS_URL = "ws://localhost:XXXXX/token"  # Replace with actual URL

    async def main():
        async with async_playwright() as p:
            browser = await p.firefox.connect(WS_URL)

            # Get or create context/page
            contexts = browser.contexts
            context = contexts[0] if contexts else await browser.new_context()
            pages = context.pages
            page = pages[0] if pages else await context.new_page()

            # Your actions here
            await page.goto("https://example.com")

    asyncio.run(main())
    EOF

---

Example 1: Cursor Navigation + Click
------------------------------------

    uv run python3 << 'EOF'
    import asyncio
    from playwright.async_api import async_playwright

    WS_URL = "ws://localhost:XXXXX/token"

    async def main():
        async with async_playwright() as p:
            browser = await p.firefox.connect(WS_URL)
            page = browser.contexts[0].pages[0]

            # Hover over element
            button = page.locator("button.submit")
            await button.hover()

            # Get element position
            box = await button.bounding_box()

            # Move cursor with realistic steps
            await page.mouse.move(box["x"], box["y"], steps=20)

            # Click with delay
            await button.click(delay=50)

            print("Clicked button!")

    asyncio.run(main())
    EOF

---

Example 2: JavaScript Execution
-------------------------------

    uv run python3 << 'EOF'
    import asyncio
    from playwright.async_api import async_playwright

    WS_URL = "ws://localhost:XXXXX/token"

    async def main():
        async with async_playwright() as p:
            browser = await p.firefox.connect(WS_URL)
            page = browser.contexts[0].pages[0]

            # Get page title
            title = await page.evaluate("document.title")
            print(f"Title: {title}")

            # Execute JS with arguments
            result = await page.evaluate("([a, b]) => a * b", [7, 6])
            print(f"Result: {result}")

            # Modify DOM
            await page.evaluate("""
                () => {
                    document.body.style.background = 'lightblue';
                    const div = document.createElement('div');
                    div.textContent = 'Injected by HEREDOC!';
                    document.body.prepend(div);
                }
            """)

            # Execute JS on specific element
            text = await page.locator("h1").evaluate("el => el.textContent")
            print(f"H1 text: {text}")

    asyncio.run(main())
    EOF

---

Example 3: Screenshot
---------------------

    uv run python3 << 'EOF'
    import asyncio
    from playwright.async_api import async_playwright

    WS_URL = "ws://localhost:XXXXX/token"

    async def main():
        async with async_playwright() as p:
            browser = await p.firefox.connect(WS_URL)
            page = browser.contexts[0].pages[0]

            # Full page screenshot
            await page.screenshot(path="full_page.png", full_page=True)

            # Viewport only
            await page.screenshot(path="viewport.png")

            # Specific region
            await page.screenshot(
                path="region.png",
                clip={"x": 0, "y": 0, "width": 800, "height": 400}
            )

            # Element screenshot
            await page.locator("h1").screenshot(path="element.png")

            # Screenshot as bytes
            data = await page.screenshot(type="png")
            print(f"Screenshot: {len(data)} bytes")

    asyncio.run(main())
    EOF

---

Example 4: Complete Workflow
----------------------------

    uv run python3 << 'EOF'
    import asyncio
    from playwright.async_api import async_playwright

    WS_URL = "ws://localhost:XXXXX/token"

    async def main():
        async with async_playwright() as p:
            browser = await p.firefox.connect(WS_URL)

            # Create fresh context and page
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate
            await page.goto("https://google.com")
            await page.wait_for_load_state("networkidle")

            # Type in search box
            search = page.locator('textarea[name="q"]')
            await search.hover()
            await search.click()
            await search.fill("camoufox browser automation")

            # Submit search
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            # Get results
            results = await page.locator("h3").all_text_contents()
            for i, r in enumerate(results[:5]):
                print(f"{i+1}. {r}")

            # Screenshot
            await page.screenshot(path="search_results.png")

            # Close this context (browser stays open)
            await context.close()

    asyncio.run(main())
    EOF

---

Tips
----
- Browser persists between HEREDOC scripts
- Use browser.contexts[0].pages[0] to reuse existing page
- Create new context/page for isolated sessions
- Call context.close() to clean up without closing browser
- Server outputs WebSocket URL on startup - save it
