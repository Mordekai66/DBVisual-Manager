
# ============================
# FLET VERSION OF YOUR GUI
# Converted from Tkinter → Flet
# ============================

import flet as ft
import database as db
import import_export as ie
import erd_generator as erd
from datetime import datetime
import os


# -----------------------------
# MAIN APP
# -----------------------------
def main(page: ft.Page):
    page.title = "Database Manager (Flet Version)"
    page.window_width = 1200
    page.window_height = 750
    page.padding = 10
    page.scroll = "auto"

    # GLOBAL STATE
    current_db_path = ft.Text("")
    selected_table = ft.Text("")
    table_list = ft.Column(scroll="auto", spacing=5)
    data_table = ft.DataTable(columns=[], rows=[], expand=True)

    # -----------------------------
    # Load Tables
    # -----------------------------
    def load_tables():
        table_list.controls.clear()
        if not current_db_path.value:
            table_list.controls.append(ft.Text("No database selected"))
            page.update()
            return

        try:
            if hasattr(db, "get_tables"):
                tables = db.get_tables(current_db_path.value)
            elif hasattr(db, "list_tables"):
                tables = db.list_tables(current_db_path.value)
            else:
                tables = []

            if not tables:
                table_list.controls.append(ft.Text("No Tables Found"))
            else:
                for t in tables:
                    table_list.controls.append(
                        ft.ElevatedButton(t, on_click=lambda e, t=t: load_table_records(t))
                    )

        except Exception as ex:
            table_list.controls.append(ft.Text(f"Error loading tables: {ex}"))

        page.update()

    # -----------------------------
    # Load Records
    # -----------------------------
    def load_table_records(table_name):
        selected_table.value = table_name

        try:
            if hasattr(db, "fetch_records"):
                recs, cols = db.fetch_records(current_db_path.value, table_name)
            else:
                recs = []
                cols = []

            # Build table
            data_table.columns = [ft.DataColumn(ft.Text(c)) for c in cols]
            rows = []

            for item in recs:
                if isinstance(item, dict):
                    vals = [str(item[c]) for c in cols]
                else:
                    vals = [str(x) for x in item]

                rows.append(
                    ft.DataRow(
                        cells=[ft.DataCell(ft.Text(v)) for v in vals]
                    )
                )

            data_table.rows = rows

        except Exception as ex:
            data_table.columns = []
            data_table.rows = []
            page.snack_bar = ft.SnackBar(ft.Text(f"Error loading records: {ex}"))
            page.snack_bar.open = True

        page.update()

    # -----------------------------
    # Add Record
    # -----------------------------
    def add_record_dialog(e):
        if not selected_table.value:
            return

        # Fetch schema
        try:
            schema = db.get_table_schema(current_db_path.value, selected_table.value)
            inputs = {}

            fields = []
            for col in schema:
                name = col["name"]
                tf = ft.TextField(label=name)
                inputs[name] = tf
                fields.append(tf)

            def submit_record(ev):
                data = {k: v.value for k, v in inputs.items()}
                db.insert_record(current_db_path.value, selected_table.value, data)
                dlg.open = False
                load_table_records(selected_table.value)
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(f"Add Record to {selected_table.value}"),
                content=ft.Column(fields, scroll="auto", height=300),
                actions=[
                    ft.ElevatedButton("Add", on_click=submit_record),
                    ft.ElevatedButton("Cancel", on_click=lambda ev: close_dialog())
                ],
            )

            def close_dialog():
                dlg.open = False
                page.update()

            page.dialog = dlg
            dlg.open = True
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
            page.snack_bar.open = True
            page.update()

    # -----------------------------
    # Delete Record
    # -----------------------------
    def delete_record_dialog(e):
        if not selected_table.value:
            return

        pk_field = ft.TextField(label="Primary Key Column")
        pk_value = ft.TextField(label="Value")

        def confirm(ev):
            try:
                db.delete_record(current_db_path.value, selected_table.value, pk_field.value, pk_value.value)
                dlg.open = False
                load_table_records(selected_table.value)
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
                page.snack_bar.open = True
                page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Delete Record"),
            content=ft.Column([pk_field, pk_value]),
            actions=[
                ft.ElevatedButton("Delete", on_click=confirm),
                ft.ElevatedButton("Cancel", on_click=lambda ev: close())
            ],
        )

        def close():
            dlg.open = False
            page.update()

        page.dialog = dlg
        dlg.open = True
        page.update()

    # -----------------------------
    # Open DB File
    # -----------------------------
    file_picker = ft.FilePicker()

    def pick_file(e: ft.FilePickerResultEvent):
        if e.files:
            current_db_path.value = e.files[0].path
            load_tables()
            page.update()

    file_picker.on_result = pick_file
    page.overlay.append(file_picker)

    # -----------------------------
    # Layout
    # -----------------------------
    left_panel = ft.Container(
        width=350,
        padding=10,
        content=ft.Column(
            [
                ft.Text("Database Path:"),
                ft.Text(current_db_path.value),
                ft.ElevatedButton("Open Database", on_click=lambda e: file_picker.pick_files(allow_multiple=False)),
                ft.Divider(),
                ft.Text("Tables:", size=20),
                table_list,
                ft.ElevatedButton("Refresh Tables", on_click=lambda e: load_tables()),
                ft.ElevatedButton("Import DB", on_click=lambda e: ie.import_db(current_db_path.value)),
                ft.ElevatedButton("Export DB", on_click=lambda e: ie.export_db(current_db_path.value)),
            ],
            expand=True
        ),
        border=ft.border.all(1),
    )

    right_panel = ft.Container(
        expand=True,
        padding=10,
        content=ft.Column(
            [
                ft.Text("Selected Table:"),
                selected_table,
                ft.Row([
                    ft.ElevatedButton("Add Record", on_click=add_record_dialog),
                    ft.ElevatedButton("Delete Record", on_click=delete_record_dialog),
                ]),
                ft.Container(
                    content=data_table,
                    expand=True
                )
            ],
            expand=True
        ),
        border=ft.border.all(1),
    )

    page.add(
        ft.Row([left_panel, right_panel], expand=True)
    )


# RUN
ft.app(target=main)
