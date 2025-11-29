Trigger: After completing Phase 3 (Form Interaction), ask user for summary name based on context

Output: analysis/{{summary_name}}_summary.md

Template:

```markdown
{{summary_name}} Summary

Overview
  - Pages discovered: {{count}}
  - Total fields extracted: {{count}}
  - Validation rules identified: {{count}}

Selectors by Action

  Inputs:
    | Field | Selector | Type |
    |-------|----------|------|
    | {{field_name}} | {{css_selector}} | {{input_type}} |

  Buttons:
    | Action | Selector |
    |--------|----------|
    | {{action_name}} | {{css_selector}} |

  Dropdowns:
    | Field | Selector | Options Count |
    |-------|----------|---------------|
    | {{field_name}} | {{css_selector}} | {{count}} |

Navigation Workflow
  1. {{menu_item}} -> {{selector}}
  2. {{menu_item}} -> {{selector}}
  3. {{page_action}} -> {{selector}}

Class Template
  ```python
  class {{ClassName}}Page:
      URL = "{{url_pattern}}"

      SELECTORS = {
          "inputs": { ... },
          "buttons": { ... },
          "dropdowns": { ... }
      }

      async def navigate(self, page):
          pass

      async def fill(self, page, data: dict):
          pass

      async def submit(self, page):
          pass
  ```

Validation Notes
  - {{field_name}}: {{validation_rule}}
  - {{field_name}}: {{validation_rule}}
```
