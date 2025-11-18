# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import database as db
import import_export as ie
import erd_generator as erd
from datetime import datetime

# Global variables
current_db = None
current_db_type = None
table_list = None
record_tree = None
entry_form = None
history = []
history_index = -1

def create_main_window(root):
    """Create the main application window with all UI components"""
    # Create a notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Tab for database structure
    structure_tab = ttk.Frame(notebook)
    notebook.add(structure_tab, text="Database Structure")
    
    # Left panel for table list
    left_panel = ttk.Frame(structure_tab)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
    
    # Table list
    global table_list
    table_listbox = tk.Listbox(left_panel, width=30)
    table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    table_list = table_listbox
    
    # Buttons for table operations
    table_btn_frame = ttk.Frame(left_panel)
    table_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    ttk.Button(table_btn_frame, text="Add Table", command=add_table_dialog).pack(fill=tk.X, pady=2)
    ttk.Button(table_btn_frame, text="Edit Table", command=edit_table_dialog).pack(fill=tk.X, pady=2)
    ttk.Button(table_btn_frame, text="Drop Table", command=drop_table).pack(fill=tk.X, pady=2)
    
    # Right panel for table structure
    right_panel = ttk.Frame(structure_tab)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Table structure treeview
    columns = ("Column", "Type", "Primary Key", "Foreign Key", "Reference")
    structure_tree = ttk.Treeview(right_panel, columns=columns, show="headings")
    
    for col in columns:
        structure_tree.heading(col, text=col)
        structure_tree.column(col, width=150)
    
    structure_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Buttons for column operations
    col_btn_frame = ttk.Frame(right_panel)
    col_btn_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(col_btn_frame, text="Add Column", command=add_column_dialog).pack(side=tk.LEFT, padx=5)
    ttk.Button(col_btn_frame, text="Edit Column", command=edit_column_dialog).pack(side=tk.LEFT, padx=5)
    ttk.Button(col_btn_frame, text="Drop Column", command=drop_column).pack(side=tk.LEFT, padx=5)
    
    # Tab for data entry
    data_tab = ttk.Frame(notebook)
    notebook.add(data_tab, text="Data Entry")
    
    # Left panel for table selection
    data_left_panel = ttk.Frame(data_tab)
    data_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
    
    # Table list for data entry
    data_table_listbox = tk.Listbox(data_left_panel, width=30)
    data_table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Bind selection event
    data_table_listbox.bind('<<ListboxSelect>>', on_table_select)
    
    # Right panel for data entry
    data_right_panel = ttk.Frame(data_tab)
    data_right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Record treeview
    global record_tree
    record_tree = ttk.Treeview(data_right_panel)
    record_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Entry form
    global entry_form
    entry_form = ttk.Frame(data_right_panel)
    entry_form.pack(fill=tk.X, padx=5, pady=5)
    
    # Buttons for record operations
    record_btn_frame = ttk.Frame(data_right_panel)
    record_btn_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(record_btn_frame, text="Add Record", command=add_record).pack(side=tk.LEFT, padx=5)
    ttk.Button(record_btn_frame, text="Edit Record", command=edit_record).pack(side=tk.LEFT, padx=5)
    ttk.Button(record_btn_frame, text="Delete Record", command=delete_record).pack(side=tk.LEFT, padx=5)
    
    # Tab for ERD
    erd_tab = ttk.Frame(notebook)
    notebook.add(erd_tab, text="ER Diagram")
    
    # ERD canvas
    erd_canvas = tk.Canvas(erd_tab, bg="white")
    erd_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # ERD buttons
    erd_btn_frame = ttk.Frame(erd_tab)
    erd_btn_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(erd_btn_frame, text="Generate ERD", command=lambda: generate_erd(erd_canvas)).pack(side=tk.LEFT, padx=5)
    ttk.Button(erd_btn_frame, text="Export as PNG", command=lambda: export_erd(erd_canvas, "png")).pack(side=tk.LEFT, padx=5)
    ttk.Button(erd_btn_frame, text="Export as PDF", command=lambda: export_erd(erd_canvas, "pdf")).pack(side=tk.LEFT, padx=5)
    
    # Status bar
    status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Store references to UI elements
    root.structure_tree = structure_tree
    root.data_table_listbox = data_table_listbox
    root.erd_canvas = erd_canvas
    root.status_bar = status_bar

def setup_menu(root):
    """Setup the application menu"""
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New SQLite Database", command=lambda: new_database("sqlite"))
    file_menu.add_command(label="New MySQL Database", command=lambda: new_database("mysql"))
    file_menu.add_command(label="Open Database", command=open_database)
    file_menu.add_separator()
    file_menu.add_command(label="Import Excel", command=import_excel)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Export menu
    export_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Export", menu=export_menu)
    export_menu.add_command(label="SQL Schema", command=lambda: ie.export_sql_schema(current_db, current_db_type))
    export_menu.add_command(label="SQL Insert Statements", command=lambda: ie.export_sql_inserts(current_db, current_db_type))
    export_menu.add_command(label="JSON", command=lambda: ie.export_json(current_db, current_db_type))
    export_menu.add_command(label="CSV", command=lambda: ie.export_csv(current_db, current_db_type))
    export_menu.add_command(label="Excel", command=lambda: ie.export_excel(current_db, current_db_type))
    
    # Edit menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=undo_action)
    edit_menu.add_command(label="Redo", command=redo_action)

def new_database(db_type):
    """Create a new database"""
    global current_db, current_db_type
    
    if db_type == "sqlite":
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            current_db = db.create_sqlite_database(file_path)
            current_db_type = "sqlite"
            update_ui()
            messagebox.showinfo("Success", "SQLite database created successfully!")
    elif db_type == "mysql":
        # Get MySQL connection details
        dialog = tk.Toplevel()
        dialog.title("MySQL Connection Details")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        host_entry = ttk.Entry(dialog)
        host_entry.grid(row=0, column=1, padx=5, pady=5)
        host_entry.insert(0, "localhost")
        
        ttk.Label(dialog, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        port_entry = ttk.Entry(dialog)
        port_entry.grid(row=1, column=1, padx=5, pady=5)
        port_entry.insert(0, "3306")
        
        ttk.Label(dialog, text="Username:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        user_entry = ttk.Entry(dialog)
        user_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Password:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        pass_entry = ttk.Entry(dialog, show="*")
        pass_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Database:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        db_entry = ttk.Entry(dialog)
        db_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def connect():
            host = host_entry.get()
            port = port_entry.get()
            user = user_entry.get()
            password = pass_entry.get()
            database = db_entry.get()
            
            try:
                current_db = db.connect_mysql(host, port, user, password, database)
                current_db_type = "mysql"
                update_ui()
                dialog.destroy()
                messagebox.showinfo("Success", "Connected to MySQL database successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect to MySQL: {str(e)}")
        
        ttk.Button(dialog, text="Connect", command=connect).grid(row=5, column=0, columnspan=2, pady=10)

def open_database():
    """Open an existing database"""
    global current_db, current_db_type
    
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("SQLite Database", "*.db"),
            ("All Files", "*.*")
        ]
    )
    
    if file_path:
        try:
            current_db = db.connect_sqlite(file_path)
            current_db_type = "sqlite"
            update_ui()
            messagebox.showinfo("Success", "Database opened successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database: {str(e)}")

def import_excel():
    """Import data from Excel file"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Excel Files", "*.xlsx *.xls"),
            ("All Files", "*.*")
        ]
    )
    
    if file_path:
        try:
            ie.import_excel_to_db(current_db, current_db_type, file_path)
            update_ui()
            messagebox.showinfo("Success", "Excel data imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import Excel data: {str(e)}")

def update_ui():
    """Update the UI with current database information"""
    if not current_db:
        return
    
    # Update table lists
    tables = db.get_tables(current_db, current_db_type)
    
    table_list.delete(0, tk.END)
    for table in tables:
        table_list.insert(tk.END, table)
    
    # Bind selection event
    table_list.bind('<<ListboxSelect>>', on_table_structure_select)
    
    # Update data table list
    root = table_list.master
    while root.master:
        root = root.master
    
    root.data_table_listbox.delete(0, tk.END)
    for table in tables:
        root.data_table_listbox.insert(tk.END, table)

def on_table_structure_select(event):
    """Handle table selection in structure tab"""
    if not current_db:
        return
    
    selection = table_list.curselection()
    if not selection:
        return
    
    table_name = table_list.get(selection[0])
    
    # Get table structure
    columns = db.get_table_columns(current_db, current_db_type, table_name)
    
    # Update structure tree
    root = table_list.master
    while root.master:
        root = root.master
    
    structure_tree = root.structure_tree
    for item in structure_tree.get_children():
        structure_tree.delete(item)
    
    for col in columns:
        structure_tree.insert("", tk.END, values=(
            col["name"],
            col["type"],
            "Yes" if col["primary_key"] else "No",
            "Yes" if col["foreign_key"] else "No",
            col["reference"] if col["foreign_key"] else ""
        ))

def on_table_select(event):
    """Handle table selection in data entry tab"""
    if not current_db:
        return
    
    root = event.widget.master
    while root.master:
        root = root.master
    
    selection = root.data_table_listbox.curselection()
    if not selection:
        return
    
    table_name = root.data_table_listbox.get(selection[0])
    
    # Get table data
    columns = db.get_table_columns(current_db, current_db_type, table_name)
    data = db.get_table_data(current_db, current_db_type, table_name)
    
    # Update record tree
    global record_tree
    record_tree.delete(*record_tree.get_children())
    
    # Set columns
    col_names = [col["name"] for col in columns]
    record_tree["columns"] = col_names
    record_tree["show"] = "headings"
    
    for col in col_names:
        record_tree.heading(col, text=col)
        record_tree.column(col, width=100)
    
    # Add data
    for row in data:
        record_tree.insert("", tk.END, values=row)
    
    # Update entry form
    update_entry_form(columns)

def update_entry_form(columns):
    """Update the entry form based on table columns"""
    global entry_form
    
    # Clear existing form
    for widget in entry_form.winfo_children():
        widget.destroy()
    
    # Create form fields
    entry_widgets = {}
    
    for i, col in enumerate(columns):
        ttk.Label(entry_form, text=col["name"] + ":").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        
        if col["foreign_key"]:
            # Create combobox for foreign key
            ref_table = col["reference"].split(".")[0]
            ref_column = col["reference"].split(".")[1]
            
            ref_data = db.get_table_data(current_db, current_db_type, ref_table)
            ref_values = [str(row[ref_column]) for row in ref_data]
            
            combobox = ttk.Combobox(entry_form, values=ref_values)
            combobox.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            entry_widgets[col["name"]] = combobox
        elif col["type"].lower() in ["date", "datetime"]:
            # Create date entry
            date_entry = ttk.Entry(entry_form)
            date_entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            entry_widgets[col["name"]] = date_entry
        elif col["type"].lower() in ["int", "integer", "decimal", "numeric", "float", "real"]:
            # Create number entry
            num_entry = ttk.Entry(entry_form)
            num_entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            entry_widgets[col["name"]] = num_entry
        else:
            # Create text entry
            text_entry = ttk.Entry(entry_form)
            text_entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            entry_widgets[col["name"]] = text_entry
    
    # Store entry widgets for later use
    entry_form.entry_widgets = entry_widgets

def add_table_dialog():
    """Show dialog to add a new table"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    dialog = tk.Toplevel()
    dialog.title("Add Table")
    dialog.geometry("300x100")
    
    ttk.Label(dialog, text="Table Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(dialog)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    def add_table():
        table_name = name_entry.get()
        if not table_name:
            messagebox.showwarning("Warning", "Please enter a table name!")
            return
        
        try:
            db.create_table(current_db, current_db_type, table_name)
            update_ui()
            dialog.destroy()
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully!")
            
            # Add to history
            add_to_history({
                "action": "create_table",
                "table_name": table_name
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create table: {str(e)}")
    
    ttk.Button(dialog, text="Add", command=add_table).grid(row=1, column=0, columnspan=2, pady=10)

def edit_table_dialog():
    """Show dialog to edit a table"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    selection = table_list.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table to edit!")
        return
    
    old_name = table_list.get(selection[0])
    
    dialog = tk.Toplevel()
    dialog.title("Edit Table")
    dialog.geometry("300x100")
    
    ttk.Label(dialog, text="New Table Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(dialog)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    name_entry.insert(0, old_name)
    
    def rename_table():
        new_name = name_entry.get()
        if not new_name:
            messagebox.showwarning("Warning", "Please enter a table name!")
            return
        
        try:
            db.rename_table(current_db, current_db_type, old_name, new_name)
            update_ui()
            dialog.destroy()
            messagebox.showinfo("Success", f"Table renamed from '{old_name}' to '{new_name}' successfully!")
            
            # Add to history
            add_to_history({
                "action": "rename_table",
                "old_name": old_name,
                "new_name": new_name
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename table: {str(e)}")
    
    ttk.Button(dialog, text="Rename", command=rename_table).grid(row=1, column=0, columnspan=2, pady=10)

def drop_table():
    """Drop the selected table"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    selection = table_list.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table to drop!")
        return
    
    table_name = table_list.get(selection[0])
    
    if messagebox.askyesno("Confirm", f"Are you sure you want to drop the table '{table_name}'?"):
        try:
            db.drop_table(current_db, current_db_type, table_name)
            update_ui()
            messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully!")
            
            # Add to history
            add_to_history({
                "action": "drop_table",
                "table_name": table_name
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to drop table: {str(e)}")

def add_column_dialog():
    """Show dialog to add a new column"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    selection = table_list.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = table_list.get(selection[0])
    
    dialog = tk.Toplevel()
    dialog.title("Add Column")
    dialog.geometry("400x300")
    
    ttk.Label(dialog, text="Column Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(dialog)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(dialog, text="Data Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    type_var = tk.StringVar(value="TEXT")
    type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["TEXT", "INTEGER", "REAL", "DATE"])
    type_combo.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(dialog, text="Primary Key:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    pk_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(dialog, variable=pk_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(dialog, text="Foreign Key:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    fk_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(dialog, variable=fk_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(dialog, text="Reference (table.column):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    ref_entry = ttk.Entry(dialog)
    ref_entry.grid(row=4, column=1, padx=5, pady=5)
    
    def add_column():
        column_name = name_entry.get()
        data_type = type_var.get()
        is_pk = pk_var.get()
        is_fk = fk_var.get()
        reference = ref_entry.get()
        
        if not column_name:
            messagebox.showwarning("Warning", "Please enter a column name!")
            return
        
        if is_fk and not reference:
            messagebox.showwarning("Warning", "Please enter a reference for the foreign key!")
            return
        
        try:
            db.add_column(current_db, current_db_type, table_name, column_name, data_type, is_pk, is_fk, reference)
            on_table_structure_select(None)
            messagebox.showinfo("Success", f"Column '{column_name}' added successfully!")
            
            # Add to history
            add_to_history({
                "action": "add_column",
                "table_name": table_name,
                "column_name": column_name,
                "data_type": data_type,
                "is_pk": is_pk,
                "is_fk": is_fk,
                "reference": reference
            })
            
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add column: {str(e)}")
    
    ttk.Button(dialog, text="Add", command=add_column).grid(row=5, column=0, columnspan=2, pady=10)

def edit_column_dialog():
    """Show dialog to edit a column"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    selection = table_list.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = table_list.get(selection[0])
    
    root = table_list.master
    while root.master:
        root = root.master
    
    structure_tree = root.structure_tree
    selected_item = structure_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a column to edit!")
        return
    
    column_values = structure_tree.item(selected_item, "values")
    old_name = column_values[0]
    old_type = column_values[1]
    old_pk = column_values[2] == "Yes"
    old_fk = column_values[3] == "Yes"
    old_ref = column_values[4]
    
    dialog = tk.Toplevel()
    dialog.title("Edit Column")
    dialog.geometry("400x300")
    
    ttk.Label(dialog, text="Column Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(dialog)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    name_entry.insert(0, old_name)
    
    ttk.Label(dialog, text="Data Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    type_var = tk.StringVar(value=old_type)
    type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["TEXT", "INTEGER", "REAL", "DATE"])
    type_combo.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(dialog, text="Primary Key:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    pk_var = tk.BooleanVar(value=old_pk)
    ttk.Checkbutton(dialog, variable=pk_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(dialog, text="Foreign Key:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    fk_var = tk.BooleanVar(value=old_fk)
    ttk.Checkbutton(dialog, variable=fk_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(dialog, text="Reference (table.column):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    ref_entry = ttk.Entry(dialog)
    ref_entry.grid(row=4, column=1, padx=5, pady=5)
    ref_entry.insert(0, old_ref)
    
    def edit_column():
        new_name = name_entry.get()
        data_type = type_var.get()
        is_pk = pk_var.get()
        is_fk = fk_var.get()
        reference = ref_entry.get()
        
        if not new_name:
            messagebox.showwarning("Warning", "Please enter a column name!")
            return
        
        if is_fk and not reference:
            messagebox.showwarning("Warning", "Please enter a reference for the foreign key!")
            return
        
        try:
            db.edit_column(current_db, current_db_type, table_name, old_name, new_name, data_type, is_pk, is_fk, reference)
            on_table_structure_select(None)
            messagebox.showinfo("Success", f"Column '{old_name}' edited successfully!")
            
            # Add to history
            add_to_history({
                "action": "edit_column",
                "table_name": table_name,
                "old_name": old_name,
                "new_name": new_name,
                "data_type": data_type,
                "is_pk": is_pk,
                "is_fk": is_fk,
                "reference": reference
            })
            
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit column: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=edit_column).grid(row=5, column=0, columnspan=2, pady=10)

def drop_column():
    """Drop the selected column"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    selection = table_list.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = table_list.get(selection[0])
    
    root = table_list.master
    while root.master:
        root = root.master
    
    structure_tree = root.structure_tree
    selected_item = structure_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a column to drop!")
        return
    
    column_values = structure_tree.item(selected_item, "values")
    column_name = column_values[0]
    
    if messagebox.askyesno("Confirm", f"Are you sure you want to drop the column '{column_name}' from table '{table_name}'?"):
        try:
            db.drop_column(current_db, current_db_type, table_name, column_name)
            on_table_structure_select(None)
            messagebox.showinfo("Success", f"Column '{column_name}' dropped successfully!")
            
            # Add to history
            add_to_history({
                "action": "drop_column",
                "table_name": table_name,
                "column_name": column_name
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to drop column: {str(e)}")

def add_record():
    """Add a new record to the selected table"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    root = entry_form.master
    while root.master:
        root = root.master
    
    selection = root.data_table_listbox.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = root.data_table_listbox.get(selection[0])
    
    # Get values from entry form
    values = {}
    for col_name, widget in entry_form.entry_widgets.items():
        values[col_name] = widget.get()
    
    try:
        db.insert_record(current_db, current_db_type, table_name, values)
        on_table_select(None)
        messagebox.showinfo("Success", "Record added successfully!")
        
        # Add to history
        add_to_history({
            "action": "insert_record",
            "table_name": table_name,
            "values": values
        })
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add record: {str(e)}")

def edit_record():
    """Edit the selected record"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    root = entry_form.master
    while root.master:
        root = root.master
    
    selection = root.data_table_listbox.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = root.data_table_listbox.get(selection[0])
    
    # Get selected record
    selected_item = record_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to edit!")
        return
    
    record_values = record_tree.item(selected_item, "values")
    
    # Get primary key column
    columns = db.get_table_columns(current_db, current_db_type, table_name)
    pk_columns = [col["name"] for col in columns if col["primary_key"]]
    
    if not pk_columns:
        messagebox.showwarning("Warning", "Table has no primary key. Cannot edit record.")
        return
    
    # Get primary key values
    pk_values = {}
    for i, col in enumerate(columns):
        if col["primary_key"]:
            pk_values[col["name"]] = record_values[i]
    
    # Get new values from entry form
    new_values = {}
    for col_name, widget in entry_form.entry_widgets.items():
        new_values[col_name] = widget.get()
    
    try:
        db.update_record(current_db, current_db_type, table_name, pk_values, new_values)
        on_table_select(None)
        messagebox.showinfo("Success", "Record updated successfully!")
        
        # Add to history
        add_to_history({
            "action": "update_record",
            "table_name": table_name,
            "pk_values": pk_values,
            "new_values": new_values
        })
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update record: {str(e)}")

def delete_record():
    """Delete the selected record"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    root = entry_form.master
    while root.master:
        root = root.master
    
    selection = root.data_table_listbox.curselection()
    if not selection:
        messagebox.showwarning("Warning", "Please select a table first!")
        return
    
    table_name = root.data_table_listbox.get(selection[0])
    
    # Get selected record
    selected_item = record_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete!")
        return
    
    record_values = record_tree.item(selected_item, "values")
    
    # Get primary key column
    columns = db.get_table_columns(current_db, current_db_type, table_name)
    pk_columns = [col["name"] for col in columns if col["primary_key"]]
    
    if not pk_columns:
        messagebox.showwarning("Warning", "Table has no primary key. Cannot delete record.")
        return
    
    # Get primary key values
    pk_values = {}
    for i, col in enumerate(columns):
        if col["primary_key"]:
            pk_values[col["name"]] = record_values[i]
    
    if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
        try:
            db.delete_record(current_db, current_db_type, table_name, pk_values)
            on_table_select(None)
            messagebox.showinfo("Success", "Record deleted successfully!")
            
            # Add to history
            add_to_history({
                "action": "delete_record",
                "table_name": table_name,
                "pk_values": pk_values
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

def generate_erd(canvas):
    """Generate ERD on the canvas"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    # Clear canvas
    canvas.delete("all")
    
    # Get tables and relationships
    tables = db.get_tables(current_db, current_db_type)
    table_info = {}
    
    # Get table columns
    for table in tables:
        columns = db.get_table_columns(current_db, current_db_type, table)
        table_info[table] = columns
    
    # Draw tables
    table_positions = {}
    x = 50
    y = 50
    
    for table, columns in table_info.items():
        # Calculate table dimensions
        col_width = 150
        row_height = 25
        header_height = 30
        
        # Table width
        max_col_width = max([len(col["name"]) * 8 for col in columns] + [len(table) * 8])
        table_width = max(col_width, max_col_width)
        
        # Table height
        table_height = header_height + len(columns) * row_height
        
        # Draw table rectangle
        canvas.create_rectangle(x, y, x + table_width, y + table_height, fill="lightgray", outline="black", width=2)
        
        # Draw table header
        canvas.create_rectangle(x, y, x + table_width, y + header_height, fill="gray", outline="black", width=2)
        canvas.create_text(x + table_width/2, y + header_height/2, text=table, font=("Arial", 12, "bold"))
        
        # Draw columns
        for i, col in enumerate(columns):
            col_y = y + header_height + i * row_height
            
            # Draw column rectangle
            canvas.create_line(x, col_y, x + table_width, col_y, fill="black")
            
            # Draw column name
            col_text = col["name"]
            if col["primary_key"]:
                col_text += " (PK)"
            if col["foreign_key"]:
                col_text += " (FK)"
            
            canvas.create_text(x + 10, col_y + row_height/2, text=col_text, anchor=tk.W, font=("Arial", 10))
        
        # Store table position
        table_positions[table] = {
            "x": x,
            "y": y,
            "width": table_width,
            "height": table_height
        }
        
        # Move to next position
        x += table_width + 50
        if x > 800:
            x = 50
            y += 200
    
    # Draw relationships
    for table, columns in table_info.items():
        for col in columns:
            if col["foreign_key"]:
                ref_table = col["reference"].split(".")[0]
                ref_col = col["reference"].split(".")[1]
                
                if table in table_positions and ref_table in table_positions:
                    # Get source and destination positions
                    src_table = table_positions[table]
                    dst_table = table_positions[ref_table]
                    
                    # Find column position in source table
                    col_index = next((i for i, c in enumerate(columns) if c["name"] == col["name"]), 0)
                    src_x = src_table["x"] + src_table["width"]
                    src_y = src_table["y"] + 30 + col_index * 25 + 12
                    
                    # Find column position in destination table
                    ref_columns = table_info[ref_table]
                    ref_col_index = next((i for i, c in enumerate(ref_columns) if c["name"] == ref_col), 0)
                    dst_x = dst_table["x"]
                    dst_y = dst_table["y"] + 30 + ref_col_index * 25 + 12
                    
                    # Draw relationship line
                    canvas.create_line(src_x, src_y, dst_x, dst_y, fill="blue", width=2, arrow=tk.LAST)
    
    # Update status
    root = canvas.master
    while root.master:
        root = root.master
    
    root.status_bar.config(text="ERD generated successfully!")

def export_erd(canvas, format_type):
    """Export ERD as PNG or PDF"""
    if not current_db:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=f".{format_type}",
        filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            erd.export_erd(canvas, file_path, format_type)
            messagebox.showinfo("Success", f"ERD exported as {format_type.upper()} successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export ERD: {str(e)}")

def add_to_history(action):
    """Add an action to the history"""
    global history, history_index
    
    # Remove any actions after the current index
    history = history[:history_index + 1]
    
    # Add the new action
    history.append(action)
    history_index += 1

def undo_action():
    """Undo the last action"""
    global history_index
    
    if history_index < 0:
        messagebox.showinfo("Info", "Nothing to undo!")
        return
    
    action = history[history_index]
    
    try:
        if action["action"] == "create_table":
            db.drop_table(current_db, current_db_type, action["table_name"])
        elif action["action"] == "drop_table":
            # This is complex to implement without storing the full table structure
            messagebox.showinfo("Info", "Cannot undo table drop operation!")
            return
        elif action["action"] == "rename_table":
            db.rename_table(current_db, current_db_type, action["new_name"], action["old_name"])
        elif action["action"] == "add_column":
            db.drop_column(current_db, current_db_type, action["table_name"], action["column_name"])
        elif action["action"] == "drop_column":
            # This is complex to implement without storing the full column definition
            messagebox.showinfo("Info", "Cannot undo column drop operation!")
            return
        elif action["action"] == "edit_column":
            db.edit_column(
                current_db, current_db_type,
                action["table_name"],
                action["new_name"],
                action["old_name"],
                action["data_type"],
                action["is_pk"],
                action["is_fk"],
                action["reference"]
            )
        elif action["action"] == "insert_record":
            # This is complex to implement without storing the primary key
            messagebox.showinfo("Info", "Cannot undo record insert operation!")
            return
        elif action["action"] == "update_record":
            db.update_record(current_db, current_db_type, action["table_name"], action["pk_values"], action["old_values"])
        elif action["action"] == "delete_record":
            # This is complex to implement without storing the full record
            messagebox.showinfo("Info", "Cannot undo record delete operation!")
            return
        
        history_index -= 1
        update_ui()
        messagebox.showinfo("Success", "Action undone successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to undo action: {str(e)}")

def redo_action():
    """Redo the last undone action"""
    global history_index
    
    if history_index >= len(history) - 1:
        messagebox.showinfo("Info", "Nothing to redo!")
        return
    
    history_index += 1
    action = history[history_index]
    
    try:
        if action["action"] == "create_table":
            db.create_table(current_db, current_db_type, action["table_name"])
        elif action["action"] == "drop_table":
            db.drop_table(current_db, current_db_type, action["table_name"])
        elif action["action"] == "rename_table":
            db.rename_table(current_db, current_db_type, action["old_name"], action["new_name"])
        elif action["action"] == "add_column":
            db.add_column(
                current_db, current_db_type,
                action["table_name"],
                action["column_name"],
                action["data_type"],
                action["is_pk"],
                action["is_fk"],
                action["reference"]
            )
        elif action["action"] == "drop_column":
            db.drop_column(current_db, current_db_type, action["table_name"], action["column_name"])
        elif action["action"] == "edit_column":
            db.edit_column(
                current_db, current_db_type,
                action["table_name"],
                action["old_name"],
                action["new_name"],
                action["data_type"],
                action["is_pk"],
                action["is_fk"],
                action["reference"]
            )
        elif action["action"] == "insert_record":
            db.insert_record(current_db, current_db_type, action["table_name"], action["values"])
        elif action["action"] == "update_record":
            db.update_record(current_db, current_db_type, action["table_name"], action["pk_values"], action["new_values"])
        elif action["action"] == "delete_record":
            db.delete_record(current_db, current_db_type, action["table_name"], action["pk_values"])
        
        update_ui()
        messagebox.showinfo("Success", "Action redone successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to redo action: {str(e)}")
