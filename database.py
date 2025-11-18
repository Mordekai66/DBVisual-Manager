# database.py
import sqlite3
import mysql.connector
from mysql.connector import Error

def create_sqlite_database(file_path):
    """Create a new SQLite database"""
    conn = sqlite3.connect(file_path)
    conn.close()
    return file_path

def connect_sqlite(file_path):
    """Connect to an existing SQLite database"""
    return file_path

def connect_mysql(host, port, user, password, database):
    """Connect to a MySQL database"""
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            return {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database
            }
    except Error as e:
        raise Exception(f"Error connecting to MySQL: {e}")

def get_tables(db, db_type):
    """Get all tables in the database"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            return tables
        except Error as e:
            raise Exception(f"Error getting tables: {e}")

def get_table_columns(db, db_type, table_name):
    """Get column information for a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # Get foreign key info
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fk_info = cursor.fetchall()
        
        # Process columns
        columns = []
        for col in columns_info:
            col_dict = {
                "name": col["name"],
                "type": col["type"],
                "primary_key": bool(col["pk"]),
                "foreign_key": False,
                "reference": ""
            }
            
            # Check if it's a foreign key
            for fk in fk_info:
                if fk["from"] == col["name"]:
                    col_dict["foreign_key"] = True
                    col_dict["reference"] = f"{fk['table']}.{fk['to']}"
                    break
            
            columns.append(col_dict)
        
        conn.close()
        return columns
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor(dictionary=True)
            
            # Get column info
            cursor.execute(f"SHOW COLUMNS FROM {table_name};")
            columns_info = cursor.fetchall()
            
            # Get foreign key info
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME, 
                    REFERENCED_TABLE_NAME, 
                    REFERENCED_COLUMN_NAME 
                FROM 
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE 
                    TABLE_SCHEMA = '{db["database"]}' 
                    AND TABLE_NAME = '{table_name}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
            fk_info = cursor.fetchall()
            
            # Process columns
            columns = []
            for col in columns_info:
                col_dict = {
                    "name": col["Field"],
                    "type": col["Type"],
                    "primary_key": col["Key"] == "PRI",
                    "foreign_key": False,
                    "reference": ""
                }
                
                # Check if it's a foreign key
                for fk in fk_info:
                    if fk["COLUMN_NAME"] == col["Field"]:
                        col_dict["foreign_key"] = True
                        col_dict["reference"] = f"{fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}"
                        break
                
                columns.append(col_dict)
            
            conn.close()
            return columns
        except Error as e:
            raise Exception(f"Error getting table columns: {e}")

def get_table_data(db, db_type, table_name):
    """Get all data from a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in rows]
        
        conn.close()
        return data
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(f"SELECT * FROM {table_name};")
            data = cursor.fetchall()
            
            conn.close()
            return data
        except Error as e:
            raise Exception(f"Error getting table data: {e}")

def create_table(db, db_type, table_name):
    """Create a new table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY);")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            cursor.execute(f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY);")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error creating table: {e}")

def rename_table(db, db_type, old_name, new_name):
    """Rename a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            cursor.execute(f"RENAME TABLE {old_name} TO {new_name};")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error renaming table: {e}")

def drop_table(db, db_type, table_name):
    """Drop a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error dropping table: {e}")

def add_column(db, db_type, table_name, column_name, data_type, is_pk, is_fk, reference):
    """Add a column to a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # SQLite doesn't support adding primary keys or foreign keys directly
        # We'll just add the column
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type};")
        
        # If it's a primary key, we need to recreate the table
        if is_pk:
            # Get current table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Create new table
            new_table_name = f"{table_name}_new"
            col_defs = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                col_pk = col[5]
                
                if col_name == column_name:
                    col_defs.append(f"{col_name} {data_type} PRIMARY KEY")
                else:
                    pk_str = "PRIMARY KEY" if col_pk else ""
                    col_defs.append(f"{col_name} {col_type} {pk_str}")
            
            cursor.execute(f"CREATE TABLE {new_table_name} ({', '.join(col_defs)});")
            
            # Copy data
            cursor.execute(f"INSERT INTO {new_table_name} SELECT * FROM {table_name};")
            
            # Drop old table and rename new table
            cursor.execute(f"DROP TABLE {table_name};")
            cursor.execute(f"ALTER TABLE {new_table_name} RENAME TO {table_name};")
        
        # If it's a foreign key, we need to recreate the table
        if is_fk:
            # Get current table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get foreign key info
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            fk_list = cursor.fetchall()
            
            # Create new table
            new_table_name = f"{table_name}_new"
            col_defs = []
            fk_defs = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                col_pk = col[5]
                
                if col_name == column_name:
                    col_defs.append(f"{col_name} {data_type}")
                    ref_table, ref_col = reference.split(".")
                    fk_defs.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table}({ref_col})")
                else:
                    pk_str = "PRIMARY KEY" if col_pk else ""
                    col_defs.append(f"{col_name} {col_type} {pk_str}")
            
            # Add existing foreign keys
            for fk in fk_list:
                fk_defs.append(f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})")
            
            # Create table with foreign keys
            cursor.execute(f"CREATE TABLE {new_table_name} ({', '.join(col_defs + fk_defs)});")
            
            # Copy data
            cursor.execute(f"INSERT INTO {new_table_name} SELECT * FROM {table_name};")
            
            # Drop old table and rename new table
            cursor.execute(f"DROP TABLE {table_name};")
            cursor.execute(f"ALTER TABLE {new_table_name} RENAME TO {table_name};")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Build column definition
            col_def = f"{column_name} {data_type}"
            
            if is_pk:
                col_def += " PRIMARY KEY"
            
            if is_fk:
                ref_table, ref_col = reference.split(".")
                col_def += f", ADD FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_col})"
            
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_def};")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error adding column: {e}")

def edit_column(db, db_type, table_name, old_name, new_name, data_type, is_pk, is_fk, reference):
    """Edit a column in a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Get current table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Get foreign key info
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fk_list = cursor.fetchall()
        
        # Create new table
        new_table_name = f"{table_name}_new"
        col_defs = []
        fk_defs = []
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_pk = col[5]
            
            if col_name == old_name:
                col_defs.append(f"{new_name} {data_type}")
                
                if is_pk:
                    col_defs[-1] += " PRIMARY KEY"
                
                if is_fk:
                    ref_table, ref_col = reference.split(".")
                    fk_defs.append(f"FOREIGN KEY ({new_name}) REFERENCES {ref_table}({ref_col})")
            else:
                pk_str = "PRIMARY KEY" if col_pk else ""
                col_defs.append(f"{col_name} {col_type} {pk_str}")
        
        # Add existing foreign keys
        for fk in fk_list:
            if fk[3] != old_name:  # Skip the FK we're editing
                fk_defs.append(f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})")
        
        # Create table with new structure
        cursor.execute(f"CREATE TABLE {new_table_name} ({', '.join(col_defs + fk_defs)});")
        
        # Copy data
        old_cols = [col[1] for col in columns]
        new_cols = []
        
        for col in old_cols:
            if col == old_name:
                new_cols.append(new_name)
            else:
                new_cols.append(col)
        
        cursor.execute(f"INSERT INTO {new_table_name} ({', '.join(new_cols)}) SELECT {', '.join(old_cols)} FROM {table_name};")
        
        # Drop old table and rename new table
        cursor.execute(f"DROP TABLE {table_name};")
        cursor.execute(f"ALTER TABLE {new_table_name} RENAME TO {table_name};")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Build column definition
            col_def = f"{old_name} {new_name} {data_type}"
            
            if is_pk:
                col_def += " PRIMARY KEY"
            
            # Drop existing foreign key if any
            cursor.execute(f"""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = '{db["database"]}' 
                AND TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME = '{old_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
            
            fk_result = cursor.fetchone()
            if fk_result:
                cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_result[0]};")
            
            # Modify column
            cursor.execute(f"ALTER TABLE {table_name} CHANGE COLUMN {old_name} {col_def};")
            
            # Add foreign key if needed
            if is_fk:
                ref_table, ref_col = reference.split(".")
                cursor.execute(f"ALTER TABLE {table_name} ADD FOREIGN KEY ({new_name}) REFERENCES {ref_table}({ref_col});")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error editing column: {e}")

def drop_column(db, db_type, table_name, column_name):
    """Drop a column from a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Get current table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Get foreign key info
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fk_list = cursor.fetchall()
        
        # Create new table
        new_table_name = f"{table_name}_new"
        col_defs = []
        fk_defs = []
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_pk = col[5]
            
            if col_name != column_name:
                pk_str = "PRIMARY KEY" if col_pk else ""
                col_defs.append(f"{col_name} {col_type} {pk_str}")
        
        # Add existing foreign keys (except those referencing the dropped column)
        for fk in fk_list:
            if fk[3] != column_name:  # Skip FKs referencing the dropped column
                fk_defs.append(f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})")
        
        # Create table without the column
        cursor.execute(f"CREATE TABLE {new_table_name} ({', '.join(col_defs + fk_defs)});")
        
        # Copy data (excluding the dropped column)
        old_cols = [col[1] for col in columns if col[1] != column_name]
        
        cursor.execute(f"INSERT INTO {new_table_name} ({', '.join(old_cols)}) SELECT {', '.join(old_cols)} FROM {table_name};")
        
        # Drop old table and rename new table
        cursor.execute(f"DROP TABLE {table_name};")
        cursor.execute(f"ALTER TABLE {new_table_name} RENAME TO {table_name};")
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Drop foreign key if any
            cursor.execute(f"""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = '{db["database"]}' 
                AND TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME = '{column_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
            
            fk_result = cursor.fetchone()
            if fk_result:
                cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_result[0]};")
            
            # Drop column
            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name};")
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error dropping column: {e}")

def insert_record(db, db_type, table_name, values):
    """Insert a new record into a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Build SQL statement
        columns = list(values.keys())
        placeholders = ["?" for _ in columns]
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"
        
        # Execute
        cursor.execute(sql, list(values.values()))
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Build SQL statement
            columns = list(values.keys())
            placeholders = ["%s" for _ in columns]
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"
            
            # Execute
            cursor.execute(sql, list(values.values()))
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error inserting record: {e}")

def update_record(db, db_type, table_name, pk_values, new_values):
    """Update a record in a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        where_values = []
        
        for col, val in pk_values.items():
            where_clauses.append(f"{col} = ?")
            where_values.append(val)
        
        where_clause = " AND ".join(where_clauses)
        
        # Build SET clause
        set_clauses = []
        set_values = []
        
        for col, val in new_values.items():
            set_clauses.append(f"{col} = ?")
            set_values.append(val)
        
        set_clause = ", ".join(set_clauses)
        
        # Build SQL statement
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
        
        # Execute
        cursor.execute(sql, set_values + where_values)
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_clauses = []
            where_values = []
            
            for col, val in pk_values.items():
                where_clauses.append(f"{col} = %s")
                where_values.append(val)
            
            where_clause = " AND ".join(where_clauses)
            
            # Build SET clause
            set_clauses = []
            set_values = []
            
            for col, val in new_values.items():
                set_clauses.append(f"{col} = %s")
                set_values.append(val)
            
            set_clause = ", ".join(set_clauses)
            
            # Build SQL statement
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
            
            # Execute
            cursor.execute(sql, set_values + where_values)
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error updating record: {e}")

def delete_record(db, db_type, table_name, pk_values):
    """Delete a record from a table"""
    if db_type == "sqlite":
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        where_values = []
        
        for col, val in pk_values.items():
            where_clauses.append(f"{col} = ?")
            where_values.append(val)
        
        where_clause = " AND ".join(where_clauses)
        
        # Build SQL statement
        sql = f"DELETE FROM {table_name} WHERE {where_clause};"
        
        # Execute
        cursor.execute(sql, where_values)
        
        conn.commit()
        conn.close()
    elif db_type == "mysql":
        try:
            conn = mysql.connector.connect(
                host=db["host"],
                port=db["port"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
            )
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_clauses = []
            where_values = []
            
            for col, val in pk_values.items():
                where_clauses.append(f"{col} = %s")
                where_values.append(val)
            
            where_clause = " AND ".join(where_clauses)
            
            # Build SQL statement
            sql = f"DELETE FROM {table_name} WHERE {where_clause};"
            
            # Execute
            cursor.execute(sql, where_values)
            
            conn.commit()
            conn.close()
        except Error as e:
            raise Exception(f"Error deleting record: {e}")
