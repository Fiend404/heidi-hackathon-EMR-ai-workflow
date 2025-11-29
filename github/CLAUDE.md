<granular_task_tracking>
When executing multi-phase pipelines, use TodoWrite with GRANULAR STEPS from each phase.

Example for phase-1.md:
```
[
  {"content": "1.1 Analyze login page with curl_cffi", "status": "in_progress", "activeForm": "Analyzing login page"},
  {"content": "1.2 Extract form selectors", "status": "pending", "activeForm": "Extracting selectors"},
  {"content": "2.1 Navigate to login URL", "status": "pending", "activeForm": "Navigating to login"},
  {"content": "2.2 Fill credentials and submit", "status": "pending", "activeForm": "Filling credentials"},
  {"content": "2.3 Capture dashboard HTML/screenshot", "status": "pending", "activeForm": "Capturing dashboard"},
  {"content": "3.1 Parse menu with BS4", "status": "pending", "activeForm": "Parsing menu"},
  {"content": "3.2 Build selector tree", "status": "pending", "activeForm": "Building selector tree"},
  {"content": "4.1 Classify into EMR categories", "status": "pending", "activeForm": "Classifying categories"},
  {"content": "4.2 Export emr_classification.json", "status": "pending", "activeForm": "Exporting classification"}
]
```

Rules:
  - Extract steps from phase prompt sections
  - Mark step in_progress BEFORE starting
  - Mark step completed IMMEDIATELY after success
  - Continue to next step without stopping
</granular_task_tracking>

<playwright_form_filling_learnings>
CRITICAL LEARNINGS from Profile Management implementation:

1. Frame Objects and Keyboard Access
   - Frame objects do NOT have .keyboard attribute
   - Always use page.keyboard when typing in frames
   - WRONG: await frame.keyboard.type(char)
   - RIGHT: await page.keyboard.type(char)

2. Form Filling Methods
   - Use frame.fill() instead of frame.click() + keyboard.type()
   - fill() is more reliable and handles focus automatically
   - WRONG: await frame.click(selector); await type_human(frame, text, page)
   - RIGHT: await frame.fill(selector, text)

3. Button Element Detection
   - Buttons can be <button>, <a>, or <input type="button/submit">
   - Always check actual HTML element type before creating selector
   - WRONG: button:has-text('Add New') when element is <input>
   - RIGHT: input[value='Add New'] for <input type="button" value="Add New">

4. Obfuscated Field Names
   - Form field names may be obfuscated for security
   - Example: username field = "rumple", password field = "stiltskin"
   - Always extract actual field names from live HTML, never assume
   - Use BS4 to capture exact name attributes from iframe HTML

5. Modal and Iframe Handling
   - After modal closes, refresh frame references
   - Frames change when navigating between pages
   - WRONG: Reuse same frame variable after modal action
   - RIGHT: Re-find frame after modal closes:
     ```python
     await add_frame.click(save_button)
     await asyncio.sleep(2)

     # Refresh frame reference
     list_frame = None
     for f in page.frames:
         if keyword in f.url:
             list_frame = f
             break
     ```

6. Wait States and Timeouts
   - page.wait_for_load_state("networkidle") often times out with iframes
   - Wrap in try/except and continue with sleep fallback
   - RIGHT:
     ```python
     try:
         await page.wait_for_load_state("networkidle", timeout=10000)
     except Exception:
         pass
     await asyncio.sleep(2)
     ```

7. Success Verification
   - After form submission, verify success by checking if entity appears in list
   - Query the list frame for newly created item
   - Use table selectors: table a:has-text('username')

8. Field Selector Discovery
   - Parse iframe HTML with BS4 to extract ALL fields
   - Export to JSON for reference: {name, id, type, selector, options}
   - For selects: capture all option values for validation

9. Error Handling in Forms
   - Check for error elements: .alert-danger, .text-danger, .error
   - Error messages may appear in the form iframe, not main page
   - Screenshot before/after save for debugging

10. Bulk Import Pattern
    - Create mapping function to transform external format to EMR format
    - Example: map_profile_to_address() transforms patient data to address book format
    - Process sequentially with frame refresh between each import
    - Track success/failure counts for reporting
</playwright_form_filling_learnings>

<camoufox_usage>
uv run python3 << 'EOF'
import asyncio
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=False) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        print(await page.title())

asyncio.run(main())
EOF
</camoufox_usage>

<realistic_mouse_navigation>
uv run python3 << 'EOF'
import asyncio
from camoufox.async_api import AsyncCamoufox

async def main():
    # humanize=0.5 enables built-in bezier curve movements
    async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        await page.click('button')

asyncio.run(main())
EOF
</realistic_mouse_navigation>

<execute_js>
uv run python3 << 'EOF'
import asyncio
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=False) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.evaluate("document.title")
        print(f"Title: {title}")

asyncio.run(main())
EOF
</execute_js>

<page_screenshot>
uv run python3 << 'EOF'
import asyncio
from camoufox.async_api import AsyncCamoufox

async def main():
    async with AsyncCamoufox(headless=False) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        await page.screenshot(path="screenshot.png")

asyncio.run(main())
EOF
</page_screenshot>

<realistic_typing>
uv run python3 << 'EOF'
import asyncio
import random
from camoufox.async_api import AsyncCamoufox

async def realistic_type(page, text, delay_range=(50, 150)):
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(delay_range[0], delay_range[1]) / 1000)

async def main():
    async with AsyncCamoufox(headless=False) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        await page.click('input[name="username"]')
        await realistic_type(page, "myusername")

asyncio.run(main())
EOF
</realistic_typing>

<form_interaction>
uv run python3 << 'EOF'
import asyncio
import random
from camoufox.async_api import AsyncCamoufox

async def type_human(page, text):
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(0.03, 0.08))

async def main():
    # humanize=0.5 enables built-in bezier curve movements
    async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com/login")
        await page.click('input[name="username"]')
        await type_human(page, "myuser")
        await page.click('input[name="password"]')
        await type_human(page, "mypass")
        await page.click('button[type="submit"]')

asyncio.run(main())
EOF
</form_interaction>

<camoufox_report_format>
All camoufox browser automation scripts must use this console report format:

File output paths:
  HAR:         ./har/{{task_name}}_{{timestamp}}.har
  Screenshots: ./screenshot/{{step}}_{{context_name}}_{{timestamp}}.png
  HTML pages:  ./html/{{step}}_{{context_name}}_{{timestamp}}.html

Filename patterns:
  With timestamp: 01_login_20251129_083037.png
  Context only:   login.png, dashboard.html

Report structure:
  - Steps show key details (title, URL, status) without file paths
  - EXPORTED FILES section shows only final step files
  - All intermediate files saved to disk but not listed in summary
  - Full traceback on errors

uv run python3 << 'EOF'
import asyncio
import os
import traceback
from datetime import datetime
from camoufox.async_api import AsyncCamoufox

os.makedirs("har", exist_ok=True)
os.makedirs("screenshot", exist_ok=True)
os.makedirs("html", exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

async def main():
    print("=" * 70)
    print("TASK NAME HERE")
    print("=" * 70)

    har_path = f"har/taskname_{timestamp}.har"
    errors = []

    async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
        context = await browser.new_context(
            record_har_path=har_path,
            record_har_content="embed"
        )
        page = await context.new_page()

        try:
            print(f"\n[1] Step description...")
            await page.goto("https://example.com", wait_until="networkidle")
            print(f"    Title: {await page.title()}")
            # Save intermediate files (not shown in summary)
            await page.screenshot(path=f"screenshot/01_context_{timestamp}.png")
            with open(f"html/01_context_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
        except Exception as e:
            errors.append(f"Step 1:\n{traceback.format_exc()}")

        try:
            print(f"\n[2] Final step...")
            print(f"    Status: SUCCESS")
            # Save final files (shown in summary)
            await page.screenshot(path=f"screenshot/02_final_{timestamp}.png", full_page=True)
            with open(f"html/02_final_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
        except Exception as e:
            errors.append(f"Step 2:\n{traceback.format_exc()}")

        print(f"\n[3] Finalizing HAR...")
        await context.close()
        print(f"    Complete")

    # EXPORTED FILES - Only final step files
    print("\n" + "=" * 70)
    print("EXPORTED FILES")
    print("=" * 70)
    print(f"  har/taskname_{timestamp}.har")
    print(f"  screenshot/02_final_{timestamp}.png")
    print(f"  html/02_final_{timestamp}.html")

    if errors:
        print("\n" + "=" * 70)
        print("ERRORS")
        print("=" * 70)
        for err in errors:
            print(f"\n{err}")

asyncio.run(main())
EOF
</camoufox_report_format>

<har_analysis>
Trigger: Fallback analysis when BS4/screenshot miss navigation data

Modes:
  - api: Discover API endpoints (JSON/XML responses, POST/PUT/PATCH/DELETE)
  - pages: Identify HTML pages and their resources
  - navigation: Extract page titles and categorize by EMR function

Usage: Set mode variable in script below

uv run python3 << 'EOF'
import json
import re
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

har_file = "har/example.har"  # Replace with actual HAR file
mode = "api"  # Options: api, pages, navigation

with open(har_file, 'r') as f:
    entries = json.load(f).get('log', {}).get('entries', [])

print("=" * 70)
print(f"HAR ANALYSIS - {mode.upper()}")
print("=" * 70)

if mode == "api":
    data_types = ['application/json', 'application/xml', 'text/xml']
    for entry in entries:
        req, resp = entry.get('request', {}), entry.get('response', {})
        url, method = req.get('url', ''), req.get('method', '')
        content_type = next((h['value'] for h in resp.get('headers', [])
                            if h['name'].lower() == 'content-type'), '').lower()
        if any(ct in content_type for ct in data_types) or method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            path = re.sub(r'/\d+', '/{id}', urlparse(url).path)
            print(f"  {method} {path} [{resp.get('status')}]")

elif mode == "pages":
    for entry in entries:
        req, resp = entry.get('request', {}), entry.get('response', {})
        content_type = next((h['value'] for h in resp.get('headers', [])
                            if h['name'].lower() == 'content-type'), '').lower()
        if 'text/html' in content_type and req.get('method') == 'GET':
            print(f"  {urlparse(req['url']).path}")

elif mode == "navigation":
    categories = defaultdict(list)
    for entry in entries:
        req, resp = entry.get('request', {}), entry.get('response', {})
        content_type = next((h['value'] for h in resp.get('headers', [])
                            if h['name'].lower() == 'content-type'), '').lower()
        if 'text/html' in content_type:
            body = resp.get('content', {}).get('text', '')
            title = re.search(r'<title>([^<]+)</title>', body, re.I)
            title = title.group(1).strip() if title else 'Untitled'
            path = urlparse(req['url']).path.lower()
            cat = 'calendar' if 'calendar' in path else 'patient' if 'patient' in path else \
                  'billing' if 'fee' in path or 'billing' in path else 'reports' if 'report' in path else 'other'
            categories[cat].append(f"{title}: {path}")
    for cat, pages in categories.items():
        if pages:
            print(f"\n[{cat.upper()}]")
            for p in pages[:10]:
                print(f"  {p}")

print("\n" + "=" * 70)
EOF
</har_analysis>

<bs4_form_discovery>
Trigger: When user requests "analyze forms" or needs to identify login/input selectors

uv run python3 << 'EOF'
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url, impersonate="chrome")
soup = BeautifulSoup(response.text, 'html.parser')

print("=" * 60)
print("FORM DISCOVERY ANALYSIS")
print("=" * 60)

forms = soup.find_all('form')
if not forms:
    print("\n  No forms found - page may use JavaScript submissions")
    print("    Recommendation: Use Playwright to inspect dynamic forms")

for i, form in enumerate(forms, 1):
    print(f"\n[Form {i}]")
    print(f"  id: {form.get('id')}")
    print(f"  action: {form.get('action')}")
    print(f"  method: {form.get('method', 'GET')}")

    print("\n  Inputs:")
    for inp in form.find_all(['input', 'select', 'textarea']):
        inp_id = inp.get('id')
        inp_name = inp.get('name')
        inp_type = inp.get('type', 'text')

        if inp_id:
            selector = f"#{inp_id}"
        elif inp_name:
            selector = f"[name='{inp_name}']"
        else:
            selector = f"{inp.name}[type='{inp_type}']"

        print(f"    {inp.name} ({inp_type}): {inp.attrs}")
        print(f"      Selector: {selector}")

    print("\n  Buttons:")
    for btn in form.find_all(['button', 'input[type="submit"]']):
        btn_id = btn.get('id')
        btn_text = btn.get_text(strip=True) or btn.get('value', '')

        if btn_id:
            selector = f"#{btn_id}"
        else:
            selector = f"button:has-text('{btn_text}')" if btn_text else "button[type='submit']"

        print(f"    {btn.name}: id={btn_id} text='{btn_text}'")
        print(f"      Selector: {selector}")

    hidden = form.find_all('input', type='hidden')
    if hidden:
        print(f"\n  Hidden fields: {len(hidden)}")
        for h in hidden:
            print(f"    {h.get('name')}: {h.get('value', '')[:50]}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
inputs_no_id = [i for i in soup.find_all('input') if not i.get('id') and i.get('type') != 'hidden']
if inputs_no_id:
    print(f"  {len(inputs_no_id)} inputs lack IDs - use [name='...'] selectors")
csrf = soup.find('input', attrs={'name': lambda x: x and 'csrf' in x.lower()})
if csrf:
    print(f"  CSRF token found: {csrf.get('name')}")
EOF
</bs4_form_discovery>

<bs4_navigation_mapping>
Trigger: When user requests "map navigation" or needs to understand site structure/pagination

uv run python3 << 'EOF'
from curl_cffi import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://example.com"
response = requests.get(url, impersonate="chrome")
soup = BeautifulSoup(response.text, 'html.parser')

print("=" * 60)
print("NAVIGATION MAPPING ANALYSIS")
print("=" * 60)

print("\n[Navigation Menus]")
navs = soup.find_all('nav')
if not navs:
    navs = soup.select('[role="navigation"], [class*="nav"], header ul')

for i, nav in enumerate(navs, 1):
    nav_id = nav.get('id') or nav.get('class', ['unnamed'])[0]
    print(f"\n  Nav {i} ({nav_id}):")
    for a in nav.find_all('a', limit=10):
        href = a.get('href', '')
        text = a.get_text(strip=True)[:40]
        print(f"    '{text}' -> {href}")

print("\n[Pagination]")
pag_selectors = [
    '[class*="pagination"]', '[class*="pager"]',
    '[aria-label*="pagination"]', '.page-numbers',
    '[class*="paginate"]'
]
pagination = None
for sel in pag_selectors:
    pagination = soup.select_one(sel)
    if pagination:
        print(f"  Found: {sel}")
        break

if pagination:
    pages = pagination.find_all('a')
    print(f"  Page links: {len(pages)}")
    for p in pages[:5]:
        print(f"    '{p.get_text(strip=True)}' -> {p.get('href', '')}")

    next_btn = pagination.find('a', string=lambda x: x and 'next' in x.lower()) or \
               pagination.select_one('[class*="next"], [rel="next"]')
    if next_btn:
        print(f"  Next button: {next_btn.get('href')}")
        print(f"    Selector: a[rel='next'] or [class*='next']")
else:
    print("  No pagination found")
    print("    Check for: infinite scroll, load more button, or URL params (?page=2)")

print("\n[Breadcrumbs]")
breadcrumb = soup.select_one('[class*="breadcrumb"], [aria-label="breadcrumb"]')
if breadcrumb:
    crumbs = [a.get_text(strip=True) for a in breadcrumb.find_all('a')]
    print(f"  Path: {' > '.join(crumbs)}")
else:
    print("  No breadcrumbs found")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
all_links = soup.find_all('a', href=True)
internal = [a for a in all_links if a['href'].startswith('/') or url in a['href']]
external = [a for a in all_links if a['href'].startswith('http') and url not in a['href']]
print(f"Total links: {len(all_links)} (internal: {len(internal)}, external: {len(external)})")
EOF
</bs4_navigation_mapping>

<bs4_general_analysis>
Trigger: When user requests "analyze page" for comprehensive structure overview

uv run python3 << 'EOF'
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url, impersonate="chrome")
soup = BeautifulSoup(response.text, 'html.parser')

print("=" * 60)
print("GENERAL PAGE ANALYSIS")
print("=" * 60)

print(f"\nTitle: {soup.title.string if soup.title else 'None'}")
print(f"Status: {response.status_code}")

print("\n[Meta Information]")
for meta in soup.find_all('meta', attrs={'name': True})[:5]:
    print(f"  {meta.get('name')}: {meta.get('content', '')[:60]}")

print("\n[Main Content Areas]")
main = soup.find('main') or soup.find(id='content') or soup.find(class_='content')
if main:
    print(f"  Main container: <{main.name}> id={main.get('id')} class={main.get('class')}")

print("\n[Content Containers]")
containers = soup.select('article, [class*="card"], [class*="item"], [class*="listing"], [class*="product"]')[:8]
for c in containers:
    classes = ' '.join(c.get('class', []))[:40]
    print(f"  <{c.name}> .{classes}")

print("\n[Data Tables]")
tables = soup.find_all('table')
print(f"  Found: {len(tables)} tables")
for t in tables[:3]:
    headers = [th.get_text(strip=True) for th in t.find_all('th')[:5]]
    print(f"    Headers: {headers}")

print("\n[Lists]")
lists = soup.find_all(['ul', 'ol'], class_=True)[:5]
for lst in lists:
    classes = ' '.join(lst.get('class', []))
    items = len(lst.find_all('li'))
    print(f"  <{lst.name}> .{classes} ({items} items)")

print("\n[Interactive Elements]")
buttons = soup.find_all('button')
selects = soup.find_all('select')
print(f"  Buttons: {len(buttons)}")
print(f"  Dropdowns: {len(selects)}")
for s in selects[:3]:
    options = [o.get_text(strip=True) for o in s.find_all('option')[:4]]
    print(f"    {s.get('name')}: {options}")

print("\n[Scripts & Data]")
json_ld = soup.find('script', type='application/ld+json')
if json_ld:
    print("  JSON-LD structured data found")
data_attrs = soup.find_all(attrs={'data-api': True})[:3]
if data_attrs:
    print(f"  Elements with data-api: {len(data_attrs)}")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
if not containers:
    print("  No obvious content containers - may need custom selectors")
if soup.find_all('script', src=lambda x: x and 'react' in x.lower()):
    print("  React detected - content may be dynamically rendered")
if soup.find_all('script', src=lambda x: x and 'vue' in x.lower()):
    print("  Vue detected - content may be dynamically rendered")
print("  Use discovered selectors with Playwright for interaction")
EOF
</bs4_general_analysis>

<screenshot_analysis>
Trigger: Read exported screenshot to identify visible UI elements

Steps:
1. Read screenshot with Read tool
2. List all visible navigation items, menus, buttons
3. Note any expanded dropdowns or active states

Output: Bulleted list of identified elements by region (top nav, sidebar, main content, user menu)
</screenshot_analysis>

<menu_bs4_analysis>
Trigger: When user requests "analyze menu" or needs to extract navigation menu selectors from HTML

Report format:
==========================================================================================
MENU BS4 ANALYSIS - TREE WITH SELECTORS
==========================================================================================

[MENU TREE]
📦 Menu
├── 📄 Calendar → .menuLabel.px-1:has-text('Calendar')
├── 📁 Patient → .dropdown-toggle:has-text('Patient')
│   ├── 📄 New/Search → .menuEntries .menuLabel:has-text('New/Search')
│   ├── 📄 Dashboard (disabled) → .menuEntries .menuLabel:has-text('Dashboard')
│   ├── 📁 Visits → .dropdown-toggle:has-text('Visits')
│   │   ├── 📄 Create Visit (disabled) → .menuEntries .menuLabel:has-text('Create Visit')
│   │   ├── 📄 Current (disabled) → .menuEntries .menuLabel:has-text('Current')

==========================================================================================
SUMMARY
==========================================================================================
  Total menu items: 136
  Enabled items: 118
  Disabled items: 18
==========================================================================================

uv run python3 << 'EOF'
from bs4 import BeautifulSoup
import json
import os

os.makedirs("analysis", exist_ok=True)

html_file = "html/dashboard.html"  # Replace with actual HTML file

with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=" * 90)
print("MENU BS4 ANALYSIS - TREE WITH SELECTORS")
print("=" * 90)

# Find the nav collapse div
nav = soup.find('nav')
collapse_div = nav.find('div', class_='navbar-collapse') if nav else None

if not collapse_div:
    print("ERROR: Could not find navbar-collapse")
    exit(1)

# Find ALL menuLabel elements within navbar
all_labels = collapse_div.find_all(class_='menuLabel')
print(f"\nFound {len(all_labels)} menuLabel elements")

menu_items = []
seen = set()

def get_depth(elem):
    """Calculate depth by counting ancestor menuEntries"""
    depth = 0
    parent = elem.parent
    while parent and parent != collapse_div:
        if parent.get('class') and 'menuEntries' in parent.get('class'):
            depth += 1
        parent = parent.parent
    return depth

def get_selector(text, classes, depth):
    """Generate appropriate selector"""
    text_clean = text.replace("'", "\\'")
    if 'dropdown-toggle' in classes:
        return f".dropdown-toggle:has-text('{text_clean}')"
    elif depth == 0:
        return f".menuLabel.px-1:has-text('{text_clean}')"
    else:
        return f".menuEntries .menuLabel:has-text('{text_clean}')"

for label in all_labels:
    text = label.get_text(strip=True)

    # Skip empty or too long (concatenated)
    if not text or len(text) > 50:
        continue

    # Skip duplicates
    if text in seen:
        continue
    seen.add(text)

    classes = label.get('class', [])
    is_dropdown = 'dropdown-toggle' in classes
    is_disabled = 'menuDisabled' in classes
    depth = get_depth(label)

    item = {
        'name': text,
        'selector': get_selector(text, classes, depth),
        'depth': depth,
        'is_dropdown': is_dropdown,
        'disabled': is_disabled
    }
    menu_items.append(item)

# Display tree
print("\n[MENU TREE]")
print("📦 Menu")

enabled_count = 0
disabled_count = 0

for item in menu_items:
    if item['disabled']:
        disabled_count += 1
    else:
        enabled_count += 1

    status = " (disabled)" if item['disabled'] else ""
    icon = "📁" if item['is_dropdown'] else "📄"

    depth = item['depth']
    if depth == 0:
        prefix = "├── "
    else:
        prefix = "│   " * depth + "├── "

    print(f"{prefix}{icon} {item['name']}{status} → {item['selector']}")

print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)
print(f"  Total menu items: {len(menu_items)}")
print(f"  Enabled items: {enabled_count}")
print(f"  Disabled items: {disabled_count}")
print("=" * 90)

# Save to JSON
with open("analysis/menu_items.json", "w") as f:
    json.dump(menu_items, f, indent=2)
print(f"\nSaved to: analysis/menu_items.json")
EOF
</menu_bs4_analysis>

<emr_classification>
Trigger: For final summary after menu analysis complete

Analyze menu tree and classify into EMR categories with NESTED TREE STRUCTURE.

Expected output format:

[SCHEDULING] - X items (Enabled: X, Disabled: X)
├── 📄 Calendar → .menuLabel.px-1:has-text('Calendar')
└── 📄 Appointments → .menuEntries .menuLabel:has-text('Appointments')

[PATIENT] - X items (Enabled: X, Disabled: X)
├── 📁 Patient → .dropdown-toggle:has-text('Patient')
│   ├── 📄 New/Search → .menuEntries .menuLabel:has-text('New/Search')
│   └── 📁 Visits → .dropdown-toggle:has-text('Visits')
│       ├── 📄 Create Visit (disabled) → .menuEntries .menuLabel:has-text('Create Visit')
│       └── 📄 Current (disabled) → .menuEntries .menuLabel:has-text('Current')

Total: XXX items | Enabled: XXX | Disabled: XX

uv run python3 << 'EOF'
import json

with open("analysis/menu_items.json", "r") as f:
    menu_items = json.load(f)

print("=" * 90)
print("EMR CLASSIFICATION - NESTED TREE STRUCTURE")
print("=" * 90)

# Build hierarchical structure
def build_tree(items):
    """Build nested tree from flat list with depth info"""
    tree = []
    stack = [{'children': tree, 'depth': -1}]

    for item in items:
        depth = item['depth']

        # Pop stack until we find the parent level
        while len(stack) > 1 and stack[-1]['depth'] >= depth:
            stack.pop()

        # Add item to current parent
        node = {
            'name': item['name'],
            'selector': item['selector'],
            'disabled': item['disabled'],
            'is_dropdown': item['is_dropdown'],
            'depth': depth,
            'children': []
        }
        stack[-1]['children'].append(node)

        # If dropdown, push to stack as potential parent
        if item['is_dropdown']:
            stack.append(node)

    return tree

# Classify menu items by category
categories = {
    'SCHEDULING': [],
    'PATIENT': [],
    'CLINICAL': [],
    'BILLING': [],
    'PROCEDURES': [],
    'REPORTS': [],
    'MESSAGING': [],
    'ADMIN': [],
    'MISCELLANEOUS': []
}

def classify_item(name):
    """Return category for an item"""
    name_lower = name.lower()

    if any(k in name_lower for k in ['calendar', 'appt', 'appointment', 'recall']):
        return 'SCHEDULING'
    elif any(k in name_lower for k in ['patient', 'visit', 'record', 'merge', 'duplicate', 'chart out', 'chart track', 'flow board']):
        return 'PATIENT'
    elif any(k in name_lower for k in ['clinical', 'issue', 'encounter', 'superbill', 'measure', 'alert', 'immunization', 'syndromic', 'referral', 'letter', 'label', 'rx', 'medication']):
        return 'CLINICAL'
    elif any(k in name_lower for k in ['fee', 'bill', 'payment', 'checkout', 'batch payment', 'posting', 'edi', 'sales', 'cash', 'collection', 'ledger', 'financial', 'pending res', 'insurance', 'indigent', 'eligibility', 'pmt method']):
        return 'BILLING'
    elif any(k in name_lower for k in ['procedure', 'lab', 'compendium', 'batch result', 'electronic report', 'lab document']):
        return 'PROCEDURES'
    elif any(k in name_lower for k in ['report', 'list', 'statistic', 'distribution']):
        return 'REPORTS'
    elif any(k in name_lower for k in ['message', 'direct message']):
        return 'MESSAGING'
    elif any(k in name_lower for k in ['admin', 'config', 'clinic', 'facility', 'holiday', 'practice', 'setting', 'rule', 'coding', 'code', 'native data', 'external data', 'form admin', 'layout', 'document template', 'system', 'backup', 'file', 'language', 'certificate', 'log', 'diagnostic', 'api client', 'user', 'address book', 'acl']):
        return 'ADMIN'
    else:
        return 'MISCELLANEOUS'

# Build tree structure
tree = build_tree(menu_items)

def add_to_category(node, parent_category=None):
    """Recursively add nodes to categories, inheriting parent's category if needed"""
    category = classify_item(node['name'])

    # For child items, inherit parent category if current item would be MISCELLANEOUS
    if parent_category and category == 'MISCELLANEOUS':
        category = parent_category

    categories[category].append(node)

    # Recursively process children
    for child in node['children']:
        add_to_category(child, category)

for node in tree:
    add_to_category(node)

def print_tree(node, prefix="", is_last=True):
    """Print tree with proper indentation"""
    icon = "📁" if node['is_dropdown'] else "📄"
    status = " (disabled)" if node['disabled'] else ""
    connector = "└── " if is_last else "├── "

    print(f"{prefix}{connector}{icon} {node['name']}{status} → {node['selector']}")

    # Prepare prefix for children
    if node['children']:
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension

        for i, child in enumerate(node['children']):
            is_last_child = (i == len(node['children']) - 1)
            print_tree(child, new_prefix, is_last_child)

# Display categorized tree
total_items = 0
enabled_items = 0
disabled_items = 0

def count_nodes(nodes):
    """Count all nodes recursively"""
    total = len(nodes)
    for node in nodes:
        total += count_nodes(node['children'])
    return total

def count_disabled(nodes):
    """Count disabled nodes recursively"""
    disabled = sum(1 for n in nodes if n['disabled'])
    for node in nodes:
        disabled += count_disabled(node['children'])
    return disabled

for category, nodes in categories.items():
    if nodes:
        cat_total = count_nodes(nodes)
        cat_disabled = count_disabled(nodes)
        cat_enabled = cat_total - cat_disabled

        print(f"\n[{category}] - {cat_total} items (Enabled: {cat_enabled}, Disabled: {cat_disabled})")

        for i, node in enumerate(nodes):
            is_last = (i == len(nodes) - 1)
            print_tree(node, "", is_last)

        total_items += cat_total
        enabled_items += cat_enabled
        disabled_items += cat_disabled

print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)
for category, nodes in categories.items():
    if nodes:
        cat_total = count_nodes(nodes)
        cat_disabled = count_disabled(nodes)
        cat_enabled = cat_total - cat_disabled
        print(f"  {category}: {cat_total} items (Enabled: {cat_enabled}, Disabled: {cat_disabled})")

print(f"\n  TOTAL: {total_items} items | Enabled: {enabled_items} | Disabled: {disabled_items}")
print("=" * 90)

# Save categorized tree structure
categorized_data = {
    'metadata': {
        'total_items': total_items,
        'enabled_items': enabled_items,
        'disabled_items': disabled_items
    },
    'categories': {}
}

for category, nodes in categories.items():
    if nodes:
        categorized_data['categories'][category] = nodes

with open("analysis/emr_classification.json", "w") as f:
    json.dump(categorized_data, f, indent=2)

print(f"\nSaved to: analysis/emr_classification.json")
EOF
</emr_classification>

<automation_function_template>
Template for creating EMR automation functions with external data validation.

All automation functions must follow this structure:

```python
"""
{{category}} - {{operation_name}}
Auto-generated from EMR analysis
"""
import asyncio
import json
from pathlib import Path
from camoufox.async_api import AsyncCamoufox

BASE_DIR = Path(__file__).parent
SELECTORS = json.loads((BASE_DIR / "selectors.json").read_text())
OPERATIONS = json.loads((BASE_DIR / "operations.json").read_text())

from . import login, navigate_to, find_content_frame, fill_form, wait_for_success, capture_error


class {{OperationName}}:
    """{{Description of what this operation does}}"""

    def __init__(self, page, frame=None):
        self.page = page
        self.frame = frame or page
        self.operation = next(
            o for o in OPERATIONS["operations"] if o["name"] == "{{operation_name}}"
        )

    async def execute(self, data: dict) -> dict:
        """Execute {{operation_name}} operation

        Args:
            data: Dict containing fields:
                - field1 (required): Description
                - field2 (optional): Description

        Returns:
            dict with success status and result data
        """
        try:
            # 1. Click trigger if needed
            # 2. Find form frame if modal
            # 3. Fill form fields using frame.fill()
            # 4. Submit
            # 5. Check success/error
            return {"success": True, "message": "...", "data": {...}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}


async def main():
    """Test execution with external data"""
    # Load external data for validation
    external_file = Path(__file__).parent.parent / "sample-profile-data.json"

    if external_file.exists():
        with open(external_file) as f:
            external_data = json.load(f)

        # Use first record for testing
        sample = external_data[0]

        # Map external fields to function parameters
        test_data = {
            "first_name": sample.get("first_name"),
            "last_name": sample.get("last_name"),
            "email": sample.get("email"),
            "phone": sample.get("phone"),
            # Add all required field mappings
        }

        print(f"Testing with external data: {sample.get('first_name')} {sample.get('last_name')}")
    else:
        # Fallback to generated test data
        import time
        suffix = int(time.time()) % 10000
        test_data = {
            "first_name": f"Test{suffix}",
            "last_name": f"User{suffix}",
        }
        print("Testing with generated data")

    async with AsyncCamoufox(headless=False, humanize=0.5) as browser:
        ctx = await browser.new_context()
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        # Login
        await login(page)

        # Navigate to target page
        await navigate_to(page, ["Menu", "Submenu"])

        # Find content frame
        frame = await find_content_frame(page, "iframe_keyword")

        # Execute operation
        op = {{OperationName}}(page, frame)
        result = await op.execute(test_data)

        # Print result
        print(json.dumps(result, indent=2))

        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Key Requirements:
- Load external_data_file from frontmatter if it exists
- Map external fields to function parameters in test_data
- Print which data source is being used (external vs generated)
- Set page.set_default_timeout(30000) for iframe-heavy apps
- Use frame.fill() for all text inputs
- Validate with actual sample data before marking function complete
</automation_function_template>

<analysis_json_export>
Trigger: "export analysis" or "save json" after menu/page discovery complete

File output path: ./analysis/{{domain}}_{{type}}.json

Types:
  - menu_selectors: All menu items with CSS selectors
  - emr_classification: Categorized EMR pages
  - form_selectors: Form inputs and button selectors
  - api_endpoints: Discovered API endpoints from HAR

uv run python3 << 'EOF'
import json
import os

os.makedirs("analysis", exist_ok=True)

domain = "example_domain"  # Replace with actual domain
export_type = "menu_selectors"  # Or: emr_classification, form_selectors, api_endpoints

# Load source data
with open("openemr_menu_complete.json", "r") as f:
    menu_items = json.load(f)

# Build export structure
export_data = {
    "metadata": {
        "domain": domain,
        "export_type": export_type,
        "total_items": len(menu_items)
    },
    "selectors": []
}

for item in menu_items:
    export_data["selectors"].append({
        "name": item["name"],
        "selector": item["selector"],
        "disabled": item.get("disabled", False),
        "depth": item.get("depth", 0),
        "is_dropdown": item.get("is_dropdown", False)
    })

# Save to analysis folder
output_path = f"analysis/{domain}_{export_type}.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(export_data, f, indent=2, ensure_ascii=False)

print("=" * 70)
print("ANALYSIS JSON EXPORT")
print("=" * 70)
print(f"\n  Domain: {domain}")
print(f"  Type: {export_type}")
print(f"  Items: {len(menu_items)}")
print(f"\n  Exported to: {output_path}")
print("=" * 70)
EOF
</analysis_json_export>
