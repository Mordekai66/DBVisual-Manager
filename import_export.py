# import_export.py
import pandas as pd
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import database as db
import erd_generator as erd

def import_excel_to_db(database, db_type, file_path):
    """Import data from an Excel file to the database"""
    # Read Excel file
    xls = pd.ExcelFile(file_path)
    
    # Process each sheet
    for sheet_name in xls.sheet_names:
        # Read sheet data
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Clean column names (remove spaces and special characters)
        df.columns = [str(col).replace(' ', '_').replace('-', '_').replace('.', '_') for col in df.columns]
        
        # Create table if it doesn't exist
        tables = db.get_tables(database, db_type)
        if sheet_name not in tables:
            db.create_table(database, db_type, sheet_name)
        
        # Get existing columns
        existing_columns = db.get_table_columns(database, db_type, sheet_name)
        existing_col_names = [col["name"] for col in existing_columns]
        
        # Add new columns if needed
        for col in df.columns:
            if col not in existing_col_names:
                # Determine column type
                col_type = "TEXT"
                if pd.api.types.is_numeric_dtype(df[col]):
                    if pd.api.types.is_integer_dtype(df[col]):
                        col_type = "INTEGER"
                    else:
                        col_type = "REAL"
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_type = "DATE"
                
                # Add column
                db.add_column(database, db_type, sheet_name, col, col_type, False, False, "")
        
        # Insert data
        for _, row in df.iterrows():
            # Convert NaN to None
            values = {}
            for col in df.columns:
                if pd.isna(row[col]):
                    values[col] = None
                else:
                    values[col] = row[col]
            
            # Insert record
            db.insert_record(database, db_type, sheet_name, values)

def export_sql_schema(database, db_type):
    """Export the database schema as SQL"""
    if not database:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".sql",
        filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            with open(file_path, 'w') as f:
                # Get tables
                tables = db.get_tables(database, db_type)
                
                for table in tables:
                    # Get columns
                    columns = db.get_table_columns(database, db_type, table)
                    
                    # Build CREATE TABLE statement
                    col_defs = []
                    
                    for col in columns:
                        col_def = f"{col['name']} {col['type']}"
                        
                        if col['primary_key']:
                            col_def += " PRIMARY KEY"
                        
                        col_defs.append(col_def)
                    
                    # Add foreign key constraints
                    fk_defs = []
                    
                    for col in columns:
                        if col['foreign_key']:
                            ref_table, ref_col = col['reference'].split('.')
                            fk_defs.append(f"FOREIGN KEY ({col['name']}) REFERENCES {ref_table}({ref_col})")
                    
                    # Write CREATE TABLE statement
                    f.write(f"CREATE TABLE {table} (")
                    f.write("    " + ", ".join(col_defs + fk_defs))
                    f.write(");")
            
            messagebox.showinfo("Success", "SQL schema exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export SQL schema: {str(e)}")

def export_sql_inserts(database, db_type):
    """Export the database data as SQL INSERT statements"""
    if not database:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".sql",
        filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            with open(file_path, 'w') as f:
                # Get tables
                tables = db.get_tables(database, db_type)
                
                for table in tables:
                    # Get data
                    data = db.get_table_data(database, db_type, table)
                    
                    if not data:
                        continue
                    
                    # Get columns
                    columns = db.get_table_columns(database, db_type, table)
                    col_names = [col['name'] for col in columns]
                    
                    # Write INSERT statements
                    for row in data:
                        values = []
                        
                        for col in col_names:
                            if row[col] is None:
                                values.append("NULL")
                            elif isinstance(row[col], str):
                                values.append(f"'{row[col].replace("'", "''")}'")
                            else:
                                values.append(str(row[col]))
                        
                        f.write(f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({', '.join(values)});")
                    
                    f.write("")
            
            messagebox.showinfo("Success", "SQL INSERT statements exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export SQL INSERT statements: {str(e)}")

def export_json(database, db_type):
    """Export the database as JSON"""
    if not database:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            # Get tables
            tables = db.get_tables(database, db_type)
            
            # Build JSON structure
            json_data = {}
            
            for table in tables:
                # Get data
                data = db.get_table_data(database, db_type, table)
                json_data[table] = data
            
            # Write JSON file
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=4, default=str)
            
            messagebox.showinfo("Success", "Database exported as JSON successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")

def export_csv(database, db_type):
    """Export each table as a CSV file"""
    if not database:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    # Ask for directory
    dir_path = filedialog.askdirectory()
    
    if dir_path:
        try:
            # Get tables
            tables = db.get_tables(database, db_type)
            
            for table in tables:
                # Get data
                data = db.get_table_data(database, db_type, table)
                
                if not data:
                    continue
                
                # Create DataFrame
                df = pd.DataFrame(data)
                
                # Write CSV file
                file_path = f"{dir_path}/{table}.csv"
                df.to_csv(file_path, index=False)
            
            messagebox.showinfo("Success", "Tables exported as CSV files successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")

def export_excel(database, db_type):
    """Export the database as an Excel file"""
    if not database:
        messagebox.showwarning("Warning", "Please open or create a database first!")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            # Get tables
            tables = db.get_tables(database, db_type)
            
            # Create Excel writer
            with pd.ExcelWriter(file_path) as writer:
                for table in tables:
                    # Get data
                    data = db.get_table_data(database, db_type, table)
                    
                    if not data:
                        continue
                    
                    # Create DataFrame
                    df = pd.DataFrame(data)
                    
                    # Write to Excel
                    df.to_excel(writer, sheet_name=table, index=False)
            
            messagebox.showinfo("Success", "Database exported as Excel file successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")
