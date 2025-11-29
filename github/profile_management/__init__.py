"""
Profile Management Module for OpenEMR Address Book
Auto-generated from EMR analysis
"""
import asyncio
import random
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
SELECTORS = json.loads((BASE_DIR / "selectors.json").read_text())
OPERATIONS = json.loads((BASE_DIR / "operations.json").read_text())

# Login credentials
LOGIN_URL = "https://demo.openemr.io/openemr/interface/login/login.php?site=default"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "pass"


async def login(page, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """
    Login to OpenEMR

    Args:
        page: Playwright page object
        username: Login username
        password: Login password

    Returns:
        bool: True if login successful
    """
    await page.goto(LOGIN_URL, wait_until="networkidle")
    await page.fill("[name='authUser']", username)
    await page.fill("[name='clearPass']", password)
    await page.click("#login-button")

    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    await asyncio.sleep(2)

    title = await page.title()
    return "OpenEMR" in title and "Login" not in title


async def navigate_to(page, menu_path: list, timeout=15000):
    """
    Navigate through menu items

    Args:
        page: Playwright page object
        menu_path: List of menu items to click, e.g. ["Admin", "Address Book"]
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if navigation successful
    """
    for i, item in enumerate(menu_path):
        try:
            # Use JavaScript to click menu items for reliability
            clicked = await page.evaluate(f"""
                () => {{
                    const items = document.querySelectorAll('.menuLabel');
                    for (const el of items) {{
                        if (el.textContent.trim() === '{item}') {{
                            el.click();
                            return true;
                        }}
                    }}
                    // Try dropdown toggles
                    const dropdowns = document.querySelectorAll('.dropdown-toggle');
                    for (const el of dropdowns) {{
                        if (el.textContent.trim() === '{item}') {{
                            el.click();
                            return true;
                        }}
                    }}
                    return false;
                }}
            """)

            if clicked:
                await asyncio.sleep(0.5)
            else:
                print(f"Menu item not found: {item}")
                return False

        except Exception as e:
            print(f"Navigation error at '{item}': {e}")
            return False

    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass
    await asyncio.sleep(2)

    return True


async def find_content_frame(page, keyword):
    """
    Find iframe containing keyword in URL

    Args:
        page: Playwright page object
        keyword: String to match in frame URL

    Returns:
        Frame object or None
    """
    for frame in page.frames:
        if keyword in frame.url:
            return frame
    return None


async def type_human(page, text, delay_range=(30, 80)):
    """
    Type text with human-like delays using page.keyboard

    Args:
        page: Playwright page object (NOT frame - frames don't have keyboard)
        text: Text to type
        delay_range: Tuple of (min_ms, max_ms) delay between keystrokes
    """
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(delay_range[0], delay_range[1]) / 1000)


async def fill_form(frame, field_data: dict, selectors: dict = None):
    """
    Fill form fields in an iframe

    Args:
        frame: Playwright frame object
        field_data: Dict of field_name -> value
        selectors: Optional dict of field_name -> selector (defaults to [name='field_name'])
    """
    for field_name, value in field_data.items():
        if value is None or value == "":
            continue

        selector = f"[name='{field_name}']"
        if selectors and field_name in selectors:
            selector = selectors[field_name]

        try:
            element = await frame.query_selector(selector)
            if element:
                tag = await element.evaluate("el => el.tagName.toLowerCase()")

                if tag == "select":
                    await frame.select_option(selector, value)
                elif tag == "textarea":
                    await frame.fill(selector, str(value))
                else:
                    input_type = await element.get_attribute("type")
                    if input_type == "checkbox":
                        if value:
                            await element.check()
                    else:
                        await frame.fill(selector, str(value))
        except Exception as e:
            print(f"Error filling {field_name}: {e}")


async def wait_for_success(frame, indicator: dict, timeout=10000):
    """
    Wait for success indicator

    Args:
        frame: Playwright frame object
        indicator: Dict with 'selector' and 'condition' keys
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if success indicator found
    """
    try:
        if indicator.get("type") == "frame_url_change":
            await asyncio.sleep(2)
            return indicator.get("value", "") in frame.url
        else:
            await frame.wait_for_selector(
                indicator["selector"],
                state="visible",
                timeout=timeout
            )
            return True
    except Exception:
        return False


async def capture_error(frame, indicator: dict):
    """
    Capture error message if present

    Args:
        frame: Playwright frame object
        indicator: Dict with 'selector' key

    Returns:
        str or None: Error message if found
    """
    try:
        error_el = await frame.query_selector(indicator["selector"])
        if error_el:
            return await error_el.text_content()
    except Exception:
        pass
    return None


async def extract_table_data(frame, table_selector="table"):
    """
    Extract table rows as list of dicts

    Args:
        frame: Playwright frame object
        table_selector: CSS selector for the table

    Returns:
        list: List of dicts with column headers as keys
    """
    try:
        data = await frame.evaluate(f"""
            () => {{
                const table = document.querySelector('{table_selector}');
                if (!table) return [];

                const headers = Array.from(table.querySelectorAll('th'))
                    .map(th => th.textContent.trim());

                const rows = [];
                table.querySelectorAll('tbody tr').forEach(tr => {{
                    const row = {{}};
                    tr.querySelectorAll('td').forEach((td, i) => {{
                        row[headers[i] || `col_${{i}}`] = td.textContent.trim();
                    }});
                    rows.push(row);
                }});
                return rows;
            }}
        """)
        return data
    except Exception as e:
        print(f"Error extracting table: {e}")
        return []


def map_profile_to_address(profile: dict) -> dict:
    """
    Map external profile data to Address Book fields

    Args:
        profile: Dict with external profile data

    Returns:
        dict: Mapped data for Address Book form
    """
    # Gender to title mapping
    title_map = {
        "male": "Mr.",
        "female": "Ms.",
        "other": ""
    }

    # Combine medical info for notes
    notes_parts = []
    if profile.get("additional_context"):
        notes_parts.append(f"Context: {profile['additional_context']}")
    if profile.get("current_medications"):
        notes_parts.append(f"Medications: {profile['current_medications']}")
    if profile.get("allergies"):
        notes_parts.append(f"Allergies: {profile['allergies']}")
    if profile.get("past_medical_history"):
        notes_parts.append(f"History: {profile['past_medical_history']}")
    if profile.get("birth_date"):
        notes_parts.append(f"DOB: {profile['birth_date']}")

    notes = "\n".join(notes_parts)

    # Normalize phone - remove country code
    phone = profile.get("phone", "")
    if phone.startswith("+61"):
        phone = phone.replace("+61", "0").replace(" ", "")

    return {
        "form_abook_type": "oth",  # Other
        "form_title": title_map.get(profile.get("gender", ""), ""),
        "form_fname": profile.get("first_name", ""),
        "form_lname": profile.get("last_name", ""),
        "form_phonecell": phone,
        "form_email": profile.get("email", ""),
        "form_specialty": "Patient Contact",
        "form_notes": notes
    }
