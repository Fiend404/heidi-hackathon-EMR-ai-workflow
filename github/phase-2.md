category_for_analysis: profile management
external_data_file: sample-profile-data.json

GOAL: Reverse engineer {{category_for_analysis}} to create and execute production-ready Camoufox E2E functions for the EMR system.

OUTPUT STRUCTURE: {{category}}/{{function_name}}.py

RULES:
  - Do NOT assume field names, selectors, or operations
  - Extract ALL information from live page analysis
  - Verify every selector exists before using
  - Document only what is discovered, not what is expected

PROGRESS TRACKING:
  - Use TodoWrite to track each function
  - SEQUENTIAL EXECUTION: Create and run ONE function at a time
  - Do NOT proceed to next function until current function runs successfully
  - Mark in_progress before creation
  - Mark completed ONLY after successful execution test
  - If execution fails: fix issues and re-run until passing

SEQUENTIAL WORKFLOW PER FUNCTION:
  1. Create function file
  2. Run with test data: `uv run python {{category}}/{{function}}.py`
  3. If error: fix and re-run
  4. If success: mark completed, move to next
  5. Repeat until all functions pass

Phase 0: Prerequisites Check
  - Verify Phase 1 outputs exist:
    - analysis/menu_items.json
    - analysis/emr_classification.json
    - html/02_dashboard_*.html (dashboard HTML from Phase 1)
    - screenshot/02_dashboard_*.png (dashboard screenshot from Phase 1)
  - If missing: STOP and notify user to run Phase 1 first
  - Parse emr_classification.json to identify pages in {{category_for_analysis}}
  - Report: Number of pages found in category

Phase 1: Page Discovery
  - Parse menu_items.json to identify pages related to {{category_for_analysis}}
  - Use Camoufox to navigate to each identified page
  - Export Screenshot, HTML for each page
  - CRITICAL: For iframe-based content, extract iframe HTML separately:
    ```python
    for frame in page.frames:
        content = await frame.content()
        if 'target_keyword' in content:
            with open(f"html/{page_name}_iframe.html", "w") as f:
                f.write(content)
    ```
  - Identify all distinct view states (list, add, edit, delete, search)
  - Document navigation path to each view

Phase 1.5: Additional Form Discovery
  - CRITICAL: Before extracting fields, trigger ALL form modals/views
  - For each page identified in Phase 1:
    - Click "Add" buttons to capture add forms
    - Click table entries to capture edit forms
    - Click "Search" buttons to capture search forms
    - Export screenshot + HTML for each modal/form state
    - Extract iframe HTML if forms load in iframes
  - This ensures complete field coverage before function creation
  - Save all form HTML to {{category}}/html/ for parsing

Phase 2: Field Extraction
  - Parse ALL exported HTML (including iframe content) with BS4
  - Extract from BOTH list pages AND form modals captured in Phase 1.5
  - For each element capture exact attributes:
    - tag name, name, id, type, class, required, maxlength, pattern, value
  - CRITICAL Button Element Detection:
    - Check if <button>, <a>, or <input type="button/submit">
    - WRONG: button:has-text('Add New') when element is <input>
    - RIGHT: input[value='Add New'] for <input type="button" value="Add New">
  - For select elements: extract all option values
  - For buttons: extract text, type, onclick actions
  - Watch for obfuscated field names (e.g. "rumple" for username)
  - Identify form groupings and sections
  - Output: {{category}}/selectors.json
    ```json
    {
      "page_url": "discovered_url",
      "iframe_selector": "discovered_or_null",
      "forms": {
        "form_id_or_index": {
          "action": "form_action",
          "method": "form_method",
          "fields": [
            {"name": "x", "id": "y", "type": "z", "selector": "[name='x']", ...}
          ],
          "buttons": [
            {"text": "x", "type": "y", "selector": "button:has-text('x')"}
          ]
        }
      }
    }
    ```

Phase 3: External Data Analysis (if applicable)
  - Check for external data file: {{external_data_file}}
  - If {{external_data_file}} exists:
    - Read and analyze data structure
    - Identify fields that need mapping to EMR fields
    - Document mapping requirements:
      - Which external fields map to which EMR fields
      - Any transformations needed (e.g. phone format, concatenation)
      - Fields to combine (e.g. medical info → notes field)
    - Save mapping plan to {{category}}/data_mapping_plan.json
  - If no external data: Skip to Phase 4

Phase 4: Operation Discovery
  - From page analysis, identify available operations
  - Do NOT assume CRUD - only document what exists
  - For EACH discovered operation:
    - Operation name (from button/link text)
    - Trigger selector
    - Required fields (marked required or validated)
    - Optional fields
    - Submit selector
    - Success indicator (what changes on success)
    - Error indicator (what appears on failure)
  - Output: {{category}}/operations.json
    ```json
    {
      "operations": [
        {
          "name": "discovered_operation_name",
          "trigger": "selector_to_start",
          "form_fields": ["field1", "field2"],
          "required_fields": ["field1"],
          "submit": "selector_to_submit",
          "success_indicator": {"selector": "x", "condition": "visible|text_contains|etc"},
          "error_indicator": {"selector": "x", "condition": "visible|text_contains|etc"}
        }
      ]
    }
    ```

Phase 5: Function Creation and Execution
  - Create {{category}}/ directory
  - Create __init__.py with shared helpers:
    ```python
    async def login(page, username, password):
        # Implementation based on discovered login selectors

    async def navigate_to(page, menu_path: list, timeout=15000):
        # Click through menu items
        # CRITICAL: Wrap wait_for_load_state in try/except with timeout

    async def find_content_frame(page, keyword):
        # Return frame containing keyword in URL

    async def type_human(page, text, delay_range=(30, 80)):
        # Type with human delays using page.keyboard (NOT frame.keyboard)

    async def fill_form(frame, field_data: dict, selectors: dict):
        # Fill form fields based on selector mapping
        # Use frame.fill() method, not click + type

    async def wait_for_success(frame, indicator: dict):
        # Wait for success condition

    async def capture_error(frame, indicator: dict):
        # Capture error message if present

    async def extract_table_data(frame, table_selector="table"):
        # Extract table rows as list of dicts
    ```

  - For EACH discovered operation, create function file:
    - Filename: {{category}}/{{operation_name}}.py
    - Use selectors.json for all element references
    - Use operations.json for flow logic
    - CRITICAL: Follow <automation_function_template> directive from CLAUDE.md
    - Include test execution in __main__ that loads {{external_data_file}}
    - Map external data fields to function parameters
    - Use frame.fill() for text inputs, NOT click + type

  - SEQUENTIAL: Create one file, run it, fix until passing, then next

Phase 5: Validation
  - SCOPE: Do NOT stop until EVERY function passes with {{external_data_file}}
  - For each function:
    1. Verify __main__ loads {{external_data_file}} (not hardcoded test data)
    2. Run: `uv run python {{category}}/{{function}}.py`
    3. If error: fix and re-run
    4. If success: verify data from {{external_data_file}} appears in EMR
    5. Move to next function
  - All functions MUST validate with real external data
  - Repeat until ALL functions execute without error
  - Do NOT mark complete until 100% pass

Phase 6: Documentation Generation
  - Create {{category}}/documentation.md after ALL functions validated
  - Document structure:
    - Module overview with target URL and credentials
    - Shared helpers section with function signatures and parameter descriptions
    - Each operation class with:
      - Class name and purpose
      - __init__ parameters
      - execute() method signature with all supported data fields
      - Parameter descriptions with types and requirements
      - Return value structure
      - Usage example with sample data
    - Complete end-to-end example showing all functions
    - Standalone run commands for testing
  - Use inline code blocks for parameters
  - Keep descriptions concise and practical
  - Format example:
    ```
    async def login(page, username="admin", password="pass") -> bool
    Logs into OpenEMR and returns success status.
    - page: Playwright page object
    - username: Login username (default: "admin")
    - password: Login password (default: "pass")
    - Returns: True if login successful, False otherwise
    ```

Phase 7: External Data Import (if applicable)
  - Check for external data file (e.g. sample-profile-data.json)
  - If exists:
    - Analyze data structure
    - Create map_*_to_*() function to transform external format to EMR format
    - Create import_*.py with ImportClass containing:
      - import_single(data) method
      - import_all(data_list) method with success/failure tracking
    - Run bulk import to validate
    - Report: Total imported, success count, failure count
  - If no external data: Skip this phase
