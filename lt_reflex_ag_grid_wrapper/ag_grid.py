"""AG Grid Community component for Reflex.

Comprehensive wrapper covering all AG Grid Community (MIT) features for v35.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Literal

import reflex as rx
from reflex.components.el import Div
from reflex.components.props import PropsBase


# === Helper functions for event handling ===

def callback_content(iterable: list[str]) -> str:
    """Join callback expressions with semicolons."""
    return "; ".join(iterable)


def arrow_callback(js_expr: str | list[str]) -> rx.Var:
    """Create an arrow function callback from JS expression(s)."""
    if isinstance(js_expr, list):
        js_expr = callback_content(js_expr)
    return rx.Var(f"(() => {{{js_expr}}})()")


def exclude_non_serializable_keys(
    event: rx.Var,
    exclude_keys: list[str],
) -> list[str]:
    """Generate JS to exclude non-serializable keys from event object."""
    exclude_keys_str = ", ".join(exclude_keys)
    return [
        f"let {{{exclude_keys_str}, ...rest}} = {event}",
        "return rest",
    ]


# === Event spec functions ===

def _on_cell_event_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for cell events - excludes non-serializable keys."""
    exclude_keys = [
        "context", "api", "columnApi", "column",
        "node", "event", "eventPath",
    ]
    return [arrow_callback(exclude_non_serializable_keys(event, exclude_keys))]


def _on_row_event_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for row events."""
    exclude_keys = ["context", "api", "source", "node", "event", "eventPath"]
    return [arrow_callback(exclude_non_serializable_keys(event, exclude_keys))]


def _on_selection_change_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for selection change - returns selected rows."""
    return [
        rx.Var(f"{event}.api.getSelectedRows()"),
        rx.Var(f"{event}.source"),
        rx.Var(f"{event}.type"),
    ]


def _on_cell_value_changed_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for cell value change."""
    return [
        rx.Var(f"(() => {{let {{rowIndex, ...rest}} = {event}; return rowIndex}})()"),
        rx.Var(f"(() => {{let {{colDef, ...rest}} = {event}; return colDef.field}})()"),
        rx.Var(f"(() => {{let {{newValue, ...rest}} = {event}; return newValue}})()"),
    ]


def _on_cell_editing_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for cell editing started/stopped."""
    return [
        rx.Var(f"(() => {{let {{rowIndex, ...rest}} = {event}; return rowIndex}})()"),
        rx.Var(f"(() => {{let {{colDef, ...rest}} = {event}; return colDef.field}})()"),
        rx.Var(f"(() => {{let {{value, ...rest}} = {event}; return value}})()"),
    ]


def _on_row_editing_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for row editing started/stopped."""
    return [
        rx.Var(f"(() => {{let {{rowIndex, ...rest}} = {event}; return rowIndex}})()"),
        rx.Var(f"{event}.data"),
    ]


def _on_sort_changed_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for sort changed."""
    return [
        rx.Var(f"{event}.api.getColumnState().filter(c => c.sort).map(c => ({{colId: c.colId, sort: c.sort, sortIndex: c.sortIndex}}))"),
    ]


def _on_filter_changed_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for filter changed."""
    return [
        rx.Var(f"{event}.api.getFilterModel()"),
    ]


def _on_pagination_changed_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for pagination changed."""
    return [
        rx.Var(f"{event}.api.paginationGetCurrentPage()"),
        rx.Var(f"{event}.api.paginationGetTotalPages()"),
        rx.Var(f"{event}.api.paginationGetPageSize()"),
    ]


def _on_column_event_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for column events (resize, move, visible, pinned)."""
    exclude_keys = ["context", "api", "columnApi", "column", "columns", "source"]
    return [arrow_callback(exclude_non_serializable_keys(event, exclude_keys))]


def _on_row_selected_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for individual row selected."""
    return [
        rx.Var(f"{event}.data"),
        rx.Var(f"{event}.node.isSelected()"),
        rx.Var(f"(() => {{let {{rowIndex, ...rest}} = {event}; return rowIndex}})()"),
    ]


def _on_cell_focused_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for cell focused."""
    return [
        rx.Var(f"{event}.rowIndex"),
        rx.Var(f"(() => {{let {{column, ...rest}} = {event}; return column?.colId}})()"),
    ]


def _on_body_scroll_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for body scroll."""
    return [
        rx.Var(f"{event}.direction"),
        rx.Var(f"{event}.left"),
        rx.Var(f"{event}.top"),
    ]


def _on_grid_size_changed_spec(event: rx.Var) -> list[rx.Var]:
    """Event spec for grid size changed."""
    return [
        rx.Var(f"{event}.clientWidth"),
        rx.Var(f"{event}.clientHeight"),
    ]


# === Auto-size columns event chain ===

size_columns_to_fit = rx.Var(
    "(event) => event.api.sizeColumnsToFit()",
    _var_type=rx.EventChain
)


# === Filter and Editor type namespaces ===

class AGFilters(SimpleNamespace):
    """AG Grid Community filter types."""
    text = "agTextColumnFilter"
    number = "agNumberColumnFilter"
    date = "agDateColumnFilter"


class AGEditors(SimpleNamespace):
    """AG Grid Community editor types."""
    text = "agTextCellEditor"
    large_text = "agLargeTextCellEditor"
    select = "agSelectCellEditor"
    number = "agNumberCellEditor"
    date = "agDateCellEditor"
    checkbox = "agCheckboxCellEditor"


# === Column Definition ===

class ColumnDef(PropsBase):
    """Column definition for AG Grid.

    Covers all Community-level colDef properties.
    """
    # Core
    field: str | rx.Var[str]
    col_id: str | rx.Var[str] | None = None
    type: str | list[str] | rx.Var[str] | rx.Var[list[str]] | None = None
    cell_data_type: bool | str | rx.Var[bool] | rx.Var[str] | None = None

    # Header
    header_name: str | rx.Var[str] | None = None
    header_tooltip: str | rx.Var[str] | None = None
    header_class: str | list[str] | rx.Var[str] | rx.Var[list[str]] | None = None
    header_component: rx.Var | None = None
    header_component_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    wrap_header_text: bool | rx.Var[bool] | None = None
    auto_header_height: bool | rx.Var[bool] | None = None
    suppress_header_menu_button: bool | rx.Var[bool] | None = None
    suppress_header_filter_button: bool | rx.Var[bool] | None = None
    suppress_header_context_menu: bool | rx.Var[bool] | None = None
    suppress_floating_filter_button: bool | rx.Var[bool] | None = None

    # Display & Visibility
    hide: bool | rx.Var[bool] | None = None
    initial_hide: bool | rx.Var[bool] | None = None
    lock_visible: bool | rx.Var[bool] | None = None
    lock_position: bool | str | rx.Var[bool] | rx.Var[str] | None = None
    suppress_movable: bool | rx.Var[bool] | None = None

    # Width & Sizing
    width: int | rx.Var[int] | None = None
    initial_width: int | rx.Var[int] | None = None
    min_width: int | rx.Var[int] | None = None
    max_width: int | rx.Var[int] | None = None
    flex: int | rx.Var[int] | None = None
    initial_flex: int | rx.Var[int] | None = None
    resizable: bool | rx.Var[bool] | None = None
    suppress_size_to_fit: bool | rx.Var[bool] | None = None
    suppress_auto_size: bool | rx.Var[bool] | None = None

    # Sorting
    sortable: bool | rx.Var[bool] | None = None
    sort: str | rx.Var[str] | None = None
    initial_sort: str | rx.Var[str] | None = None
    sort_index: int | rx.Var[int] | None = None
    initial_sort_index: int | rx.Var[int] | None = None
    sorting_order: list[str] | rx.Var[list[str]] | None = None
    comparator: rx.Var | None = None
    un_sort_icon: bool | rx.Var[bool] | None = None

    # Filtering
    filter: str | bool | rx.Var[str] | rx.Var[bool] | None = None
    filter_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    filter_value_getter: rx.Var | None = None
    get_quick_filter_text: rx.Var | None = None
    floating_filter: bool | rx.Var[bool] | None = None
    floating_filter_component: rx.Var | None = None
    floating_filter_component_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None

    # Editing
    editable: bool | rx.Var[bool] | None = None
    cell_editor: str | rx.Var[str] | None = None
    cell_editor_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    cell_editor_selector: rx.Var | None = None
    cell_editor_popup: bool | rx.Var[bool] | None = None
    cell_editor_popup_position: str | rx.Var[str] | None = None
    single_click_edit: bool | rx.Var[bool] | None = None
    value_setter: rx.Var | None = None
    value_parser: rx.Var | None = None
    use_value_parser_for_import: bool | rx.Var[bool] | None = None

    # Data & Value
    value_getter: rx.Var | None = None
    value_formatter: rx.Var | None = None
    ref_data: dict[str, str] | rx.Var[dict[str, str]] | None = None

    # Rendering & Styling
    cell_renderer: rx.Var | None = None
    cell_renderer_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    cell_renderer_selector: rx.Var | None = None
    cell_style: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    cell_class: str | list[str] | rx.Var[str] | rx.Var[list[str]] | None = None
    cell_class_rules: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    enable_cell_change_flash: bool | rx.Var[bool] | None = None

    # Text display
    wrap_text: bool | rx.Var[bool] | None = None
    auto_height: bool | rx.Var[bool] | None = None

    # Tooltips
    tooltip_field: str | rx.Var[str] | None = None
    tooltip_value_getter: rx.Var | None = None
    tooltip_component: rx.Var | None = None
    tooltip_component_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None

    # Pinning
    pinned: bool | str | rx.Var[bool] | rx.Var[str] | None = None
    initial_pinned: bool | str | rx.Var[bool] | rx.Var[str] | None = None
    lock_pinned: bool | rx.Var[bool] | None = None

    # Spanning
    col_span: rx.Var | None = None

    # Row Drag
    row_drag: bool | rx.Var[bool] | None = None
    row_drag_text: rx.Var | None = None

    # Keyboard & Navigation
    suppress_navigable: bool | rx.Var[bool] | None = None
    suppress_keyboard_event: rx.Var | None = None
    suppress_paste: bool | rx.Var[bool] | None = None
    suppress_fill_handle: bool | rx.Var[bool] | None = None

    # Export
    use_value_formatter_for_export: bool | rx.Var[bool] | None = None

    # Misc
    cell_aria_role: str | rx.Var[str] | None = None
    context: dict[str, Any] | rx.Var[dict[str, Any]] | None = None


# === Column Group Definition ===

class ColGroupDef(PropsBase):
    """Column group definition for grouped column headers."""
    header_name: str | rx.Var[str]
    group_id: str | rx.Var[str] | None = None
    children: list[dict[str, Any]] | rx.Var[list[dict[str, Any]]] = []
    marry_children: bool | rx.Var[bool] | None = None
    open_by_default: bool | rx.Var[bool] | None = None
    header_class: str | list[str] | rx.Var[str] | rx.Var[list[str]] | None = None
    header_group_component: rx.Var | None = None
    header_group_component_params: dict[str, Any] | rx.Var[dict[str, Any]] | None = None
    suppress_sticky_label: bool | rx.Var[bool] | None = None


# === Grid API class for imperative operations ===

class AgGridAPI:
    """API class for imperative AG Grid operations.

    Uses dynamic __getattr__ so any AG Grid API method can be called.
    Common convenience methods are provided explicitly.
    """

    def __init__(self, ref: str):
        self.ref = ref

    @classmethod
    def create(cls, id: str) -> "AgGridAPI":
        """Create API instance for a grid with given ID."""
        return cls(ref=rx.utils.format.format_ref(id))

    @property
    def _api(self) -> str:
        """Get the JavaScript API reference string."""
        return f"refs['{self.ref}']?.current?.api"

    def __getattr__(self, name: str) -> Callable[..., rx.event.EventSpec]:
        """Allow calling any AG Grid API method dynamically."""
        def _call_api(*args, **kwargs) -> rx.event.EventSpec:
            var_args = [str(rx.Var.create(arg)) for arg in args]
            return rx.call_script(
                f"{self._api}.{rx.utils.format.to_camel_case(name)}({', '.join(var_args)})",
                **kwargs,
            )
        return _call_api


# === Main AG Grid Component ===

class AgGrid(rx.Component):
    """AG Grid Community component for Reflex.

    Comprehensive wrapper covering all Community (MIT) grid options.
    """

    # React library configuration
    library: str = "ag-grid-react@35.0.0"
    tag: str = "AgGridReact"

    # Dependencies - Community only (no enterprise)
    lib_dependencies: list[str] = ["ag-grid-community@35.0.0"]

    # === Grid Data Props ===
    column_defs: rx.Var[list[dict[str, Any] | ColumnDef]]
    row_data: rx.Var[list[dict[str, Any]]]
    pinned_top_row_data: rx.Var[list[dict[str, Any]]] | None = None
    pinned_bottom_row_data: rx.Var[list[dict[str, Any]]] | None = None
    default_col_def: rx.Var[dict[str, Any]] = rx.Var.create({})
    default_col_group_def: rx.Var[dict[str, Any]] | None = None
    column_types: rx.Var[dict[str, Any]] | None = None
    data_type_definitions: rx.Var[dict[str, Any]] | None = None
    maintain_column_order: rx.Var[bool] | None = None
    suppress_field_dot_notation: rx.Var[bool] | None = None

    # === Selection Props ===
    # AG Grid 35: rowSelection is an object with mode "singleRow" or "multiRow"
    row_selection: rx.Var[dict[str, Any]] = rx.Var.create({"mode": "singleRow"})
    cell_selection: rx.Var[bool | dict[str, Any]] | None = None

    # === Display & Rendering Props ===
    animate_rows: rx.Var[bool] | None = None
    dom_layout: rx.Var[str] | None = None  # "normal" | "autoHeight" | "print"
    enable_rtl: rx.Var[bool] | None = None
    ensure_dom_order: rx.Var[bool] | None = None
    get_row_id: rx.Var | None = None
    get_row_class: rx.Var | None = None
    get_row_style: rx.Var | None = None
    row_class: rx.Var[str | list[str]] | None = None
    row_class_rules: rx.Var[dict[str, Any]] | None = None
    row_height: rx.Var[int] | None = None
    get_row_height: rx.Var | None = None
    row_buffer: rx.Var[int] | None = None
    suppress_column_virtualisation: rx.Var[bool] | None = None
    suppress_row_virtualisation: rx.Var[bool] | None = None
    cell_flash_duration: rx.Var[int] | None = None
    cell_fade_duration: rx.Var[int] | None = None
    allow_show_change_after_filter: rx.Var[bool] | None = None
    grid_id: rx.Var[str] | None = None
    debug: rx.Var[bool] | None = None

    # === Column Header Props ===
    header_height: rx.Var[int] | None = None
    group_header_height: rx.Var[int] | None = None
    floating_filters_height: rx.Var[int] | None = None

    # === Column Moving Props ===
    suppress_movable_columns: rx.Var[bool] | None = None
    suppress_move_when_column_dragging: rx.Var[bool] | None = None
    suppress_column_move_animation: rx.Var[bool] | None = None
    suppress_drag_leave_hides_columns: rx.Var[bool] | None = None

    # === Column Sizing Props ===
    auto_size_strategy: rx.Var[dict] | None = None
    col_resize_default: rx.Var[str] | None = None
    suppress_auto_size: rx.Var[bool] | None = None
    auto_size_padding: rx.Var[int] | None = None
    skip_header_on_auto_size: rx.Var[bool] | None = None

    # === Column Pinning Props ===
    process_unpinned_columns: rx.Var | None = None

    # === Editing Props ===
    edit_type: rx.Var[str] | None = None  # "fullRow"
    single_click_edit: rx.Var[bool] | None = None
    suppress_click_edit: rx.Var[bool] | None = None
    stop_editing_when_cells_lose_focus: rx.Var[bool] | None = None
    enter_navigates_vertically: rx.Var[bool] | None = None
    enter_navigates_vertically_after_edit: rx.Var[bool] | None = None
    enable_cell_editing_on_backspace: rx.Var[bool] | None = None
    undo_redo_cell_editing: rx.Var[bool] | None = None
    undo_redo_cell_editing_limit: rx.Var[int] | None = None
    read_only_edit: rx.Var[bool] | None = None

    # === Pagination Props ===
    pagination: rx.Var[bool] = False
    pagination_page_size: rx.Var[int] | None = None
    pagination_page_size_selector: rx.Var[list[int] | bool] | None = None
    pagination_auto_page_size: rx.Var[bool] | None = None
    paginate_child_rows: rx.Var[bool] | None = None
    suppress_pagination_panel: rx.Var[bool] | None = None

    # === Filtering Props ===
    quick_filter_text: rx.Var[str] | None = None
    cache_quick_filter: rx.Var[bool] | None = None
    include_hidden_columns_in_quick_filter: rx.Var[bool] | None = None
    is_external_filter_present: rx.Var | None = None
    does_external_filter_pass: rx.Var | None = None
    enable_advanced_filter: rx.Var[bool] | None = None

    # === Sorting Props ===
    multi_sort_key: rx.Var[str] | None = None  # "ctrl"
    accented_sort: rx.Var[bool] | None = None
    post_sort_rows: rx.Var | None = None
    delta_sort: rx.Var[bool] | None = None

    # === Overlays Props ===
    loading: rx.Var[bool] | None = None
    overlay_loading_template: rx.Var[str] | None = None
    loading_overlay_component: rx.Var | None = None
    loading_overlay_component_params: rx.Var[dict[str, Any]] | None = None
    overlay_no_rows_template: rx.Var[str] | None = None
    no_rows_overlay_component: rx.Var | None = None
    no_rows_overlay_component_params: rx.Var[dict[str, Any]] | None = None
    suppress_no_rows_overlay: rx.Var[bool] | None = None

    # === CSV Export Props ===
    default_csv_export_params: rx.Var[dict[str, Any]] | None = None
    suppress_csv_export: rx.Var[bool] | None = None

    # === Localisation Props ===
    locale_text: rx.Var[dict[str, str]] | None = None

    # === Tooltip Props ===
    tooltip_show_delay: rx.Var[int] | None = None
    tooltip_hide_delay: rx.Var[int] | None = None
    tooltip_mouse_track: rx.Var[bool] | None = None
    tooltip_interaction: rx.Var[bool] | None = None

    # === Keyboard Navigation Props ===
    tab_index: rx.Var[int] | None = None
    navigate_to_next_cell: rx.Var | None = None
    tab_to_next_cell: rx.Var | None = None
    navigate_to_next_header: rx.Var | None = None
    tab_to_next_header: rx.Var | None = None

    # === Row Drag & Drop Props ===
    row_drag_managed: rx.Var[bool] | None = None
    row_drag_entire_row: rx.Var[bool] | None = None
    row_drag_multi_row: rx.Var[bool] | None = None
    suppress_row_drag: rx.Var[bool] | None = None
    suppress_move_when_row_dragging: rx.Var[bool] | None = None

    # === Miscellaneous Props ===
    popup_parent: rx.Var | None = None
    context: rx.Var[dict[str, Any]] | None = None
    value_cache: rx.Var[bool] | None = None
    value_cache_never_expires: rx.Var[bool] | None = None
    suppress_touch: rx.Var[bool] | None = None
    suppress_focus_after_refresh: rx.Var[bool] | None = None
    suppress_change_detection: rx.Var[bool] | None = None
    suppress_browser_resize_observer: rx.Var[bool] | None = None
    suppress_row_click_selection: rx.Var[bool] | None = None
    initial_state: rx.Var[dict[str, Any]] | None = None
    aligned_grids: rx.Var[list[Any]] | None = None

    # === Theme ===
    # AG Grid 35: use "legacy" to enable CSS class-based theming
    theme: rx.Var[str] = "legacy"

    # === Event Handlers ===
    # Core
    on_grid_ready: rx.EventHandler[lambda e0: [e0]]
    on_grid_pre_destroyed: rx.EventHandler[lambda e0: [e0]]
    on_first_data_rendered: rx.EventHandler[lambda e0: [e0]]
    on_grid_size_changed: rx.EventHandler[_on_grid_size_changed_spec]
    # Cell
    on_cell_clicked: rx.EventHandler[_on_cell_event_spec]
    on_cell_double_clicked: rx.EventHandler[_on_cell_event_spec]
    on_cell_focused: rx.EventHandler[_on_cell_focused_spec]
    on_cell_value_changed: rx.EventHandler[_on_cell_value_changed_spec]
    # Editing
    on_cell_editing_started: rx.EventHandler[_on_cell_editing_spec]
    on_cell_editing_stopped: rx.EventHandler[_on_cell_editing_spec]
    on_row_editing_started: rx.EventHandler[_on_row_editing_spec]
    on_row_editing_stopped: rx.EventHandler[_on_row_editing_spec]
    # Row
    on_row_clicked: rx.EventHandler[_on_row_event_spec]
    on_row_double_clicked: rx.EventHandler[_on_row_event_spec]
    on_row_selected: rx.EventHandler[_on_row_selected_spec]
    on_selection_changed: rx.EventHandler[_on_selection_change_spec]
    on_row_data_updated: rx.EventHandler[lambda e0: [e0]]
    # Column
    on_column_resized: rx.EventHandler[_on_column_event_spec]
    on_column_moved: rx.EventHandler[_on_column_event_spec]
    on_column_visible: rx.EventHandler[_on_column_event_spec]
    on_column_pinned: rx.EventHandler[_on_column_event_spec]
    on_new_columns_loaded: rx.EventHandler[lambda e0: [e0]]
    on_displayed_columns_changed: rx.EventHandler[lambda e0: [e0]]
    # Sorting & Filtering
    on_sort_changed: rx.EventHandler[_on_sort_changed_spec]
    on_filter_changed: rx.EventHandler[_on_filter_changed_spec]
    # Pagination
    on_pagination_changed: rx.EventHandler[_on_pagination_changed_spec]
    # Scroll & Layout
    on_body_scroll: rx.EventHandler[_on_body_scroll_spec]
    on_body_scroll_end: rx.EventHandler[_on_body_scroll_spec]
    on_model_updated: rx.EventHandler[lambda e0: [e0]]
    on_viewport_changed: rx.EventHandler[lambda e0: [e0]]

    @classmethod
    def create(cls, *children, id: str, **props) -> rx.Component:
        """Create an AG Grid component.

        Args:
            id: Required unique identifier for the grid
            **props: Grid properties
        """
        # Use id only for React ref, not as AG Grid gridOption
        props["id"] = id

        # Set up theme CSS class based on color mode
        theme = props.pop("theme", "quartz")
        props["class_name"] = rx.match(
            theme,
            ("quartz", rx.color_mode_cond("ag-theme-quartz", "ag-theme-quartz-dark")),
            ("balham", rx.color_mode_cond("ag-theme-balham", "ag-theme-balham-dark")),
            ("alpine", rx.color_mode_cond("ag-theme-alpine", "ag-theme-alpine-dark")),
            ("material", rx.color_mode_cond("ag-theme-material", "ag-theme-material-dark")),
            "",
        )

        # Auto-size columns on grid ready if strategy is set
        if "auto_size_strategy" in props:
            props["on_grid_ready"] = size_columns_to_fit

        return super().create(*children, **props)

    def _exclude_props(self) -> list[str]:
        """Exclude id from being passed as an AG Grid gridOption."""
        return ["id"]

    def add_imports(self) -> dict:
        """Add required imports for AG Grid modules and themes."""
        return {
            "ag-grid-community": ["ModuleRegistry", "AllCommunityModule"],
            "": [
                "ag-grid-community/styles/ag-grid.css",
                "ag-grid-community/styles/ag-theme-quartz.css",
                "ag-grid-community/styles/ag-theme-balham.css",
                "ag-grid-community/styles/ag-theme-material.css",
                "ag-grid-community/styles/ag-theme-alpine.css",
            ],
        }

    def add_custom_code(self) -> list[str]:
        """Register AG Grid community modules at initialization."""
        return [
            "ModuleRegistry.registerModules([AllCommunityModule]);",
        ]

    @property
    def api(self) -> AgGridAPI:
        """Get the grid API for imperative operations."""
        return AgGridAPI(ref=self.get_ref())

    # === Convenience API methods ===

    def get_selected_rows(self, callback: rx.EventHandler) -> rx.event.EventSpec:
        """Get selected rows via callback."""
        return self.api.getSelectedRows(callback=callback)

    def select_all(self) -> rx.event.EventSpec:
        """Select all rows."""
        return self.api.selectAll()

    def deselect_all(self) -> rx.event.EventSpec:
        """Deselect all rows."""
        return self.api.deselectAll()

    def export_data_as_csv(self) -> rx.event.EventSpec:
        """Export grid data as CSV."""
        return self.api.exportDataAsCsv()

    def redraw_rows(self) -> rx.event.EventSpec:
        """Force redraw of all rows."""
        return self.api.redrawRows()

    def size_columns_to_fit(self) -> rx.event.EventSpec:
        """Size all columns to fit the grid width."""
        return self.api.sizeColumnsToFit()

    def auto_size_all_columns(self) -> rx.event.EventSpec:
        """Auto-size all columns based on content."""
        return self.api.autoSizeAllColumns()

    def set_quick_filter(self, text: str) -> rx.event.EventSpec:
        """Set quick filter text."""
        return self.api.setGridOption("quickFilterText", text)

    def set_filter_model(self, model: dict) -> rx.event.EventSpec:
        """Set the filter model."""
        return self.api.setFilterModel(model)

    def get_filter_model(self, callback: rx.EventHandler) -> rx.event.EventSpec:
        """Get current filter model via callback."""
        return self.api.getFilterModel(callback=callback)

    def pagination_go_to_page(self, page: int) -> rx.event.EventSpec:
        """Go to specific pagination page."""
        return self.api.paginationGoToPage(page)

    def pagination_go_to_first_page(self) -> rx.event.EventSpec:
        """Go to first page."""
        return self.api.paginationGoToFirstPage()

    def pagination_go_to_last_page(self) -> rx.event.EventSpec:
        """Go to last page."""
        return self.api.paginationGoToLastPage()

    def pagination_go_to_next_page(self) -> rx.event.EventSpec:
        """Go to next page."""
        return self.api.paginationGoToNextPage()

    def pagination_go_to_previous_page(self) -> rx.event.EventSpec:
        """Go to previous page."""
        return self.api.paginationGoToPreviousPage()

    def start_editing_cell(self, row_index: int, col_key: str) -> rx.event.EventSpec:
        """Start editing a specific cell."""
        return rx.call_script(
            f"{self.api._api}.startEditingCell({{rowIndex: {row_index}, colKey: '{col_key}'}})"
        )

    def stop_editing(self) -> rx.event.EventSpec:
        """Stop editing."""
        return self.api.stopEditing()

    def flash_cells(self) -> rx.event.EventSpec:
        """Flash all cells."""
        return self.api.flashCells()

    def refresh_cells(self) -> rx.event.EventSpec:
        """Refresh all cells."""
        return self.api.refreshCells()

    def set_row_data(self, data: list[dict]) -> rx.event.EventSpec:
        """Set new row data."""
        return self.api.setGridOption("rowData", data)


# === Wrapped version with default sizing ===

class WrappedAgGrid(AgGrid):
    """AG Grid with default container sizing."""

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        width = props.pop("width", "100%")
        height = props.pop("height", "400px")

        return Div.create(
            super().create(*children, **props),
            width=width,
            height=height,
        )


# === Namespace for convenient access ===

class AgGridNamespace(rx.ComponentNamespace):
    """Namespace providing convenient access to AG Grid components."""
    api = AgGridAPI.create
    column_def = ColumnDef
    col_group_def = ColGroupDef
    filters = AGFilters
    editors = AGEditors
    size_columns_to_fit = size_columns_to_fit
    root = AgGrid.create
    __call__ = WrappedAgGrid.create


# Export the namespace
ag_grid = AgGridNamespace()
