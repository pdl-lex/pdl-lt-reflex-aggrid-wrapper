# pdl_lt_reflex_aggrid_wrapper

A comprehensive [AG Grid](https://www.ag-grid.com/) Community (v35) wrapper for the [Reflex](https://reflex.dev/) framework. Provides full access to all AG Grid Community (MIT-licensed) features through a Pythonic API, including sorting, filtering, editing, pagination, row selection, CSV export, drag & drop, theming with dark mode support, and more.

## Installation

```bash
pip install pdl_lt_reflex_aggrid_wrapper
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/lexoterm/pdl_lt_reflex_aggrid_wrapper.git
```

## Quick Start

```python
import reflex as rx
from pdl_lt_reflex_aggrid_wrapper import ag_grid

COLUMN_DEFS = [
    ag_grid.column_def(field="name", header_name="Name", sortable=True, filter=True),
    ag_grid.column_def(field="age", header_name="Age", sortable=True, editable=True),
]

class State(rx.State):
    row_data: list[dict] = [
        {"name": "Alice", "age": 28},
        {"name": "Bob", "age": 34},
    ]

def index() -> rx.Component:
    return ag_grid(
        id="my-grid",
        row_data=State.row_data,
        column_defs=COLUMN_DEFS,
        height="400px",
    )

app = rx.App()
app.add_page(index)
```

## Features

### Column Definitions

Use `ag_grid.column_def()` to define columns. All AG Grid Community colDef properties are supported:

```python
ag_grid.column_def(
    field="name",
    header_name="Full Name",
    sortable=True,
    filter=True,                    # or ag_grid.filters.text / .number / .date
    editable=True,
    cell_editor=ag_grid.editors.text,  # .text / .number / .select / .date / .checkbox / .large_text
    cell_editor_params={"values": ["A", "B", "C"]},  # for select editor
    pinned="left",                  # "left" | "right"
    width=150,
    min_width=100,
    max_width=300,
    flex=1,
    hide=False,
    resizable=True,
    floating_filter=True,
    wrap_text=True,
    auto_height=True,
    tooltip_field="name",
    cell_style={"color": "red"},
    cell_class="my-class",
)
```

### Column Groups

Group related columns under a shared header:

```python
from pdl_lt_reflex_aggrid_wrapper import ag_grid

column_defs = [
    ag_grid.col_group_def(
        header_name="Personal Info",
        children=[
            ag_grid.column_def(field="name", header_name="Name"),
            ag_grid.column_def(field="age", header_name="Age"),
        ],
    ),
    ag_grid.col_group_def(
        header_name="Work",
        children=[
            ag_grid.column_def(field="company", header_name="Company"),
            ag_grid.column_def(field="salary", header_name="Salary"),
        ],
    ),
]
```

### Row Selection

AG Grid v35 uses an object-based `rowSelection` configuration:

```python
# Single row selection
ag_grid(
    id="grid",
    row_selection={"mode": "singleRow"},
    ...
)

# Multi-row selection with click
ag_grid(
    id="grid",
    row_selection={"mode": "multiRow", "enableClickSelection": True},
    on_selection_changed=State.on_selection_changed,
    ...
)
```

The `on_selection_changed` handler receives three arguments:

```python
def on_selection_changed(self, rows: list[dict], source: str, type: str):
    self.selected_rows = rows
```

### Pagination

```python
ag_grid(
    id="grid",
    pagination=True,
    pagination_page_size=10,
    pagination_page_size_selector=[5, 10, 25, 50, 100],
    ...
)
```

### Editing

Enable inline cell editing with built-in editors:

```python
# Per-column editing
ag_grid.column_def(field="name", editable=True, cell_editor=ag_grid.editors.text)
ag_grid.column_def(field="age", editable=True, cell_editor=ag_grid.editors.number)
ag_grid.column_def(field="city", editable=True, cell_editor=ag_grid.editors.select,
                   cell_editor_params={"values": ["Berlin", "Munich"]})

# Grid-level editing options
ag_grid(
    id="grid",
    single_click_edit=True,                     # edit on single click
    stop_editing_when_cells_lose_focus=True,     # auto-stop on blur
    undo_redo_cell_editing=True,                 # Ctrl+Z / Ctrl+Y
    undo_redo_cell_editing_limit=20,
    edit_type="fullRow",                         # edit entire row at once
    on_cell_value_changed=State.on_cell_value_changed,
    ...
)

def on_cell_value_changed(self, row_index: int, field: str, new_value):
    self.row_data[row_index][field] = new_value
```

### Filtering

```python
# Column-level filters
ag_grid.column_def(field="name", filter=True)                        # default text filter
ag_grid.column_def(field="age", filter=ag_grid.filters.number)       # number filter
ag_grid.column_def(field="date", filter=ag_grid.filters.date)        # date filter
ag_grid.column_def(field="name", floating_filter=True)               # show filter below header

# Grid-level quick filter (searches all columns)
ag_grid(
    id="grid",
    quick_filter_text=State.search_text,
    ...
)
```

### Theming

Four built-in themes with automatic dark mode support:

```python
ag_grid(id="grid", theme="quartz", ...)    # default
ag_grid(id="grid", theme="alpine", ...)
ag_grid(id="grid", theme="balham", ...)
ag_grid(id="grid", theme="material", ...)
```

The wrapper automatically switches between light and dark variants based on the Reflex color mode.

### CSV Export

```python
ag_grid(
    id="grid",
    default_csv_export_params={
        "fileName": "export.csv",
        "columnSeparator": ";",
    },
    ...
)
```

Trigger export programmatically via the API (see below).

### Localisation

Translate AG Grid UI strings:

```python
ag_grid(
    id="grid",
    locale_text={
        "page": "Seite",
        "of": "von",
        "to": "bis",
        "next": "Weiter",
        "last": "Letzte",
        "first": "Erste",
        "previous": "Zurueck",
        "noRowsToShow": "Keine Daten vorhanden",
    },
    ...
)
```

### Overlays

Show loading or empty-state overlays:

```python
ag_grid(
    id="grid",
    loading=State.is_loading,
    overlay_loading_template="<span>Loading data...</span>",
    overlay_no_rows_template="<span>No records found</span>",
    ...
)
```

### Row Drag & Drop

```python
ag_grid.column_def(field="name", row_drag=True)

ag_grid(
    id="grid",
    row_drag_managed=True,        # let AG Grid handle reordering
    row_drag_entire_row=True,     # drag by clicking anywhere on the row
    ...
)
```

### Pinned Rows

```python
ag_grid(
    id="grid",
    pinned_top_row_data=[{"name": "TOTAL", "salary": 570000}],
    pinned_bottom_row_data=[{"name": "AVERAGE", "salary": 71250}],
    ...
)
```

## Event Handlers

All event handlers receive serializable data (non-serializable JS objects like `api`, `node`, `column` are excluded).

| Event | Handler Signature |
|-------|-------------------|
| `on_selection_changed` | `(rows: list[dict], source: str, type: str)` |
| `on_cell_value_changed` | `(row_index: int, field: str, new_value)` |
| `on_cell_clicked` | `(event_data: dict)` |
| `on_cell_double_clicked` | `(event_data: dict)` |
| `on_cell_focused` | `(row_index: int, col_id: str)` |
| `on_cell_editing_started` | `(row_index: int, field: str, value)` |
| `on_cell_editing_stopped` | `(row_index: int, field: str, value)` |
| `on_row_clicked` | `(event_data: dict)` |
| `on_row_double_clicked` | `(event_data: dict)` |
| `on_row_selected` | `(data: dict, is_selected: bool, row_index: int)` |
| `on_row_editing_started` | `(row_index: int, data: dict)` |
| `on_row_editing_stopped` | `(row_index: int, data: dict)` |
| `on_sort_changed` | `(sort_state: list[dict])` |
| `on_filter_changed` | `(filter_model: dict)` |
| `on_pagination_changed` | `(current_page: int, total_pages: int, page_size: int)` |
| `on_column_resized` | `(event_data: dict)` |
| `on_column_moved` | `(event_data: dict)` |
| `on_column_visible` | `(event_data: dict)` |
| `on_column_pinned` | `(event_data: dict)` |
| `on_grid_ready` | `(event)` |
| `on_first_data_rendered` | `(event)` |
| `on_grid_size_changed` | `(width: int, height: int)` |
| `on_body_scroll` | `(direction: str, left: float, top: float)` |
| `on_model_updated` | `(event)` |

## Grid API

Access the AG Grid API for imperative operations. The API uses dynamic method dispatch, so any AG Grid API method can be called:

```python
# Create an API instance
grid_api = ag_grid.api("my-grid")

# Use in event handlers
class State(rx.State):
    def select_all_rows(self):
        return grid_api.selectAll()

    def deselect_all_rows(self):
        return grid_api.deselectAll()

    def export_csv(self):
        return grid_api.exportDataAsCsv()

    def go_to_page(self, page: int):
        return grid_api.paginationGoToPage(page)
```

## All Supported Grid Options

The wrapper exposes all AG Grid Community grid options as Python properties. Properties use `snake_case` and are automatically converted to `camelCase` for JavaScript. A value of `None` means the property is not sent to AG Grid (using its default).

<details>
<summary>Click to expand full list</summary>

**Data:**
`column_defs`, `row_data`, `pinned_top_row_data`, `pinned_bottom_row_data`, `default_col_def`, `default_col_group_def`, `column_types`, `data_type_definitions`, `maintain_column_order`, `suppress_field_dot_notation`

**Selection:**
`row_selection`, `cell_selection`

**Display & Rendering:**
`animate_rows`, `dom_layout`, `enable_rtl`, `ensure_dom_order`, `get_row_id`, `get_row_class`, `get_row_style`, `row_class`, `row_class_rules`, `row_height`, `get_row_height`, `row_buffer`, `suppress_column_virtualisation`, `suppress_row_virtualisation`, `cell_flash_duration`, `cell_fade_duration`, `allow_show_change_after_filter`, `grid_id`, `debug`

**Column Headers:**
`header_height`, `group_header_height`, `floating_filters_height`

**Column Moving:**
`suppress_movable_columns`, `suppress_move_when_column_dragging`, `suppress_column_move_animation`, `suppress_drag_leave_hides_columns`

**Column Sizing:**
`auto_size_strategy`, `col_resize_default`, `suppress_auto_size`, `auto_size_padding`, `skip_header_on_auto_size`

**Editing:**
`edit_type`, `single_click_edit`, `suppress_click_edit`, `stop_editing_when_cells_lose_focus`, `enter_navigates_vertically`, `enter_navigates_vertically_after_edit`, `enable_cell_editing_on_backspace`, `undo_redo_cell_editing`, `undo_redo_cell_editing_limit`, `read_only_edit`

**Pagination:**
`pagination`, `pagination_page_size`, `pagination_page_size_selector`, `pagination_auto_page_size`, `paginate_child_rows`, `suppress_pagination_panel`

**Filtering:**
`quick_filter_text`, `cache_quick_filter`, `include_hidden_columns_in_quick_filter`, `is_external_filter_present`, `does_external_filter_pass`, `enable_advanced_filter`

**Sorting:**
`multi_sort_key`, `accented_sort`, `post_sort_rows`, `delta_sort`

**Overlays:**
`loading`, `overlay_loading_template`, `loading_overlay_component`, `loading_overlay_component_params`, `overlay_no_rows_template`, `no_rows_overlay_component`, `no_rows_overlay_component_params`, `suppress_no_rows_overlay`

**CSV Export:**
`default_csv_export_params`, `suppress_csv_export`

**Localisation:**
`locale_text`

**Tooltips:**
`tooltip_show_delay`, `tooltip_hide_delay`, `tooltip_mouse_track`, `tooltip_interaction`

**Keyboard Navigation:**
`tab_index`, `navigate_to_next_cell`, `tab_to_next_cell`, `navigate_to_next_header`, `tab_to_next_header`

**Row Drag & Drop:**
`row_drag_managed`, `row_drag_entire_row`, `row_drag_multi_row`, `suppress_row_drag`, `suppress_move_when_row_dragging`

**Miscellaneous:**
`popup_parent`, `context`, `value_cache`, `value_cache_never_expires`, `suppress_touch`, `suppress_focus_after_refresh`, `suppress_change_detection`, `suppress_browser_resize_observer`, `suppress_row_click_selection`, `initial_state`, `aligned_grids`

</details>

## All Supported Column Properties

<details>
<summary>Click to expand full list</summary>

**Core:** `field`, `col_id`, `type`, `cell_data_type`

**Header:** `header_name`, `header_tooltip`, `header_class`, `header_component`, `header_component_params`, `wrap_header_text`, `auto_header_height`, `suppress_header_menu_button`, `suppress_header_filter_button`, `suppress_header_context_menu`, `suppress_floating_filter_button`

**Visibility:** `hide`, `initial_hide`, `lock_visible`, `lock_position`, `suppress_movable`

**Width:** `width`, `initial_width`, `min_width`, `max_width`, `flex`, `initial_flex`, `resizable`, `suppress_size_to_fit`, `suppress_auto_size`

**Sorting:** `sortable`, `sort`, `initial_sort`, `sort_index`, `initial_sort_index`, `sorting_order`, `comparator`, `un_sort_icon`

**Filtering:** `filter`, `filter_params`, `filter_value_getter`, `get_quick_filter_text`, `floating_filter`, `floating_filter_component`, `floating_filter_component_params`

**Editing:** `editable`, `cell_editor`, `cell_editor_params`, `cell_editor_selector`, `cell_editor_popup`, `cell_editor_popup_position`, `single_click_edit`, `value_setter`, `value_parser`, `use_value_parser_for_import`

**Data:** `value_getter`, `value_formatter`, `ref_data`

**Rendering:** `cell_renderer`, `cell_renderer_params`, `cell_renderer_selector`, `cell_style`, `cell_class`, `cell_class_rules`, `enable_cell_change_flash`

**Text:** `wrap_text`, `auto_height`

**Tooltips:** `tooltip_field`, `tooltip_value_getter`, `tooltip_component`, `tooltip_component_params`

**Pinning:** `pinned`, `initial_pinned`, `lock_pinned`

**Spanning:** `col_span`

**Row Drag:** `row_drag`, `row_drag_text`

**Keyboard:** `suppress_navigable`, `suppress_keyboard_event`, `suppress_paste`, `suppress_fill_handle`

**Export:** `use_value_formatter_for_export`

**Misc:** `cell_aria_role`, `context`

</details>

## Compatibility

| Dependency | Version |
|------------|---------|
| AG Grid | 35.0.0 (Community / MIT) |
| Reflex | >= 0.6.0 |
| Python | >= 3.10 |
| React | 18+ / 19+ |

## License

MIT -- same as AG Grid Community.
