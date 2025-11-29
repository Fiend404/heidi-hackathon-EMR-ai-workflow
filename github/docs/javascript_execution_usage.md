Camoufox JavaScript Execution Functions

These functions allow executing JavaScript code in the browser context.

---

Page-Level JavaScript Execution
-------------------------------

page.evaluate(expression, arg)
    Executes JavaScript and returns the result.

    Parameters:
        expression (str): JavaScript code to execute
        arg (any, optional): Arguments to pass to the function

    Returns:
        The result of the JavaScript expression (serialized to Python types)

<js_evaluate_title_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        title = await page.evaluate("document.title")
        print(f"Title: {title}")

asyncio.run(main())
EOF
</js_evaluate_title_example>
```

<js_evaluate_with_args_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        result = await page.evaluate("([a, b]) => a + b", [5, 3])
        print(f"Result: {result}")

asyncio.run(main())
EOF
</js_evaluate_with_args_example>
```

<js_evaluate_modify_dom_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.evaluate("""
            () => {
                const el = document.querySelector('h1');
                el.style.color = 'red';
                el.textContent = 'Modified!';
            }
        """)

asyncio.run(main())
EOF
</js_evaluate_modify_dom_example>
```

<js_evaluate_get_data_example>
```bash
uv run python3 << 'EOF'
import asyncio
import json
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        data = await page.evaluate("""
            () => JSON.stringify({
                url: window.location.href,
                title: document.title,
                height: document.body.scrollHeight
            })
        """)
        parsed = json.loads(data)
        print(parsed)

asyncio.run(main())
EOF
</js_evaluate_get_data_example>
```


page.evaluate_handle(expression, arg)
    Executes JavaScript and returns a handle to the result object.
    Use this for complex objects that cannot be serialized.

    Parameters:
        expression (str): JavaScript code to execute
        arg (any, optional): Arguments to pass

    Returns:
        JSHandle: A handle to the JavaScript object

<js_evaluate_handle_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        handle = await page.evaluate_handle("window")
        properties = await handle.get_properties()
        print(f"Window properties: {len(properties)}")

asyncio.run(main())
EOF
</js_evaluate_handle_example>
```

---

Element-Level JavaScript Execution
----------------------------------

locator.evaluate(expression, arg, timeout)
    Executes JavaScript on the matched element.
    The element is passed as the first argument to the function.

    Parameters:
        expression (str): JavaScript code (receives element as first arg)
        arg (any, optional): Additional arguments
        timeout (float, optional): Maximum wait time

    Returns:
        The result of the JavaScript expression

<js_locator_evaluate_text_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        text = await page.locator("h1").evaluate("el => el.textContent")
        print(f"H1 text: {text}")

asyncio.run(main())
EOF
</js_locator_evaluate_text_example>
```

<js_locator_evaluate_modify_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.locator("div.box").evaluate("el => el.classList.add('active')")

asyncio.run(main())
EOF
</js_locator_evaluate_modify_example>
```

<js_locator_evaluate_styles_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        styles = await page.locator("h1").evaluate("""
            el => ({
                color: getComputedStyle(el).color,
                fontSize: getComputedStyle(el).fontSize
            })
        """)
        print(f"Styles: {styles}")

asyncio.run(main())
EOF
</js_locator_evaluate_styles_example>
```


locator.evaluate_all(expression, arg)
    Executes JavaScript on all matched elements.

    Parameters:
        expression (str): JavaScript code (receives array of elements)
        arg (any, optional): Additional arguments

<js_locator_evaluate_all_example>
```bash
uv run python3 << 'EOF'
import asyncio
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        texts = await page.locator("p").evaluate_all("els => els.map(e => e.textContent)")
        for i, text in enumerate(texts):
            print(f"{i+1}. {text}")

asyncio.run(main())
EOF
</js_locator_evaluate_all_example>
```

---

Complete Workflow Example
-------------------------

<js_complete_workflow_example>
```bash
uv run python3 << 'EOF'
import asyncio
import json
from playwright.async_api import async_playwright

WS_URL = "ws://localhost:XXXXX/token"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.connect(WS_URL)
        page = browser.contexts[0].pages[0]

        await page.goto("https://example.com")

        title = await page.evaluate("document.title")
        print(f"Title: {title}")

        result = await page.evaluate("([x, y]) => x * y", [7, 6])
        print(f"7 * 6 = {result}")

        await page.evaluate("""
            () => {
                const div = document.createElement('div');
                div.id = 'injected';
                div.textContent = 'Created by JS!';
                document.body.appendChild(div);
            }
        """)

        font = await page.locator("h1").evaluate("el => getComputedStyle(el).fontSize")
        print(f"H1 font size: {font}")

asyncio.run(main())
EOF
</js_complete_workflow_example>
```
