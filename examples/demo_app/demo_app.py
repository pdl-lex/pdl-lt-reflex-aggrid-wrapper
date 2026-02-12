"""Demo app showcasing the AG Grid Community wrapper for Reflex.

Run with: reflex run
Requires: pip install pdl_lt_reflex_aggrid_wrapper
"""
import reflex as rx
from pdl_lt_reflex_aggrid_wrapper import ag_grid


# -- Sample data --

SAMPLE_DATA = [
    {"id": 1, "name": "Alice", "age": 28, "city": "Berlin", "salary": 65000},
    {"id": 2, "name": "Bob", "age": 34, "city": "Munich", "salary": 72000},
    {"id": 3, "name": "Carol", "age": 29, "city": "Hamburg", "salary": 58000},
    {"id": 4, "name": "David", "age": 42, "city": "Frankfurt", "salary": 85000},
    {"id": 5, "name": "Eva", "age": 31, "city": "Berlin", "salary": 70000},
    {"id": 6, "name": "Frank", "age": 26, "city": "Cologne", "salary": 52000},
    {"id": 7, "name": "Grace", "age": 38, "city": "Munich", "salary": 78000},
    {"id": 8, "name": "Henry", "age": 45, "city": "Hamburg", "salary": 92000},
]

# -- Column definitions --

COLUMN_DEFS = [
    ag_grid.column_def(
        field="id",
        header_name="ID",
        width=80,
        sortable=True,
    ),
    ag_grid.column_def(
        field="name",
        header_name="Name",
        filter=True,
        sortable=True,
        editable=True,
    ),
    ag_grid.column_def(
        field="age",
        header_name="Age",
        filter=ag_grid.filters.number,
        sortable=True,
        editable=True,
        cell_editor=ag_grid.editors.number,
    ),
    ag_grid.column_def(
        field="city",
        header_name="City",
        filter=True,
        sortable=True,
        editable=True,
        cell_editor=ag_grid.editors.select,
        cell_editor_params={
            "values": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"]
        },
    ),
    ag_grid.column_def(
        field="salary",
        header_name="Salary",
        filter=ag_grid.filters.number,
        sortable=True,
    ),
]


# -- State --

class State(rx.State):
    """App state managing grid data and selections."""

    row_data: list[dict] = SAMPLE_DATA
    selected_rows: list[dict] = []

    def on_selection_changed(self, rows: list[dict], source: str, type: str):
        """Handle row selection changes."""
        self.selected_rows = rows

    def on_cell_value_changed(self, row_index: int, field: str, new_value):
        """Handle inline cell edits."""
        if 0 <= row_index < len(self.row_data):
            self.row_data[row_index][field] = new_value


# -- Page --

def index() -> rx.Component:
    """Main page with AG Grid demo."""
    return rx.box(
        rx.heading("AG Grid Community Demo", size="7", margin_bottom="1em"),
        rx.text(
            f"Selected rows: {State.selected_rows}",
            margin_bottom="1em",
        ),
        ag_grid(
            id="demo-grid",
            row_data=State.row_data,
            column_defs=COLUMN_DEFS,
            row_selection={"mode": "multiRow", "enableClickSelection": True},
            on_selection_changed=State.on_selection_changed,
            on_cell_value_changed=State.on_cell_value_changed,
            default_col_def={"flex": 1, "minWidth": 100},
            pagination=True,
            pagination_page_size=5,
            pagination_page_size_selector=[5, 10, 25, 50],
            height="500px",
        ),
        padding="2em",
    )


app = rx.App()
app.add_page(index)
