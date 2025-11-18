# DBVisual-Manager
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%2C%20macOS%2C%20Linux-red)

A powerful desktop tool for visually managing SQLite and MySQL databases with ER diagram generation, data import/export, and intuitive table design.

## Features

### Database Management
- **Multi-Database Support**: Connect to both SQLite and MySQL databases
- **Table Operations**: Create, rename, and drop tables
- **Column Management**: Add, edit, and delete columns with full data type support
- **Data Manipulation**: Insert, update, and delete records with intuitive forms

### Visual Tools
- **ER Diagram Generator**: Automatically generate Entity-Relationship diagrams
- **Visual Export**: Export ERDs as PNG or PDF files
- **Real-time Preview**: See database structure changes instantly

### Import/Export Capabilities
- **Excel Integration**: Import data from Excel files directly into databases
- **Multiple Export Formats**:
  - SQL Schema and INSERT statements
  - JSON format
  - CSV files
  - Excel workbooks

### User Experience
- **Undo/Redo Support**: Complete history tracking for all operations
- **Foreign Key Support**: Visual representation of database relationships
- **Intuitive Forms**: Dynamic form generation based on table structure
- **Cross-Platform**: Built with Python and Tkinter for wide compatibility

## Requirements

```txt
pandas==2.0.3
Pillow==10.0.0
mysql-connector-python==8.1.0
openpyxl==3.1.2
```

## Getting Started
### Installation
1. **Clone the repository**

```bash
git clone https://github.com/Mordekai66/DBVisual-Manager.git
cd DBVisual-Manager
```
2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the application**

```bash
python main.py
```
### Usage
1. Create/Open Database
   - Use File menu to create new SQLite/MySQL database or open existing one

2. Manage Database Structure
   - Use "Database Structure" tab to manage tables and columns
   - Add primary keys and foreign key relationships

3. Data Entry
   - Use "Data Entry" tab to insert, update, and delete records
   - Dynamic forms adapt to table structure

4. Visualize Relationships
   - Generate ER diagrams in the "ER Diagram" tab
   - Export diagrams as PNG or PDF

5. Import/Export Data
   - Import Excel files directly into databases
   - Export data in multiple formats (SQL, JSON, CSV, Excel)
  
### Core Modules
1. database.py
   - Handles all database operations
   - Supports both SQLite and MySQL
   - Manages connections, queries, and transactions

2. gui.py
   - Main application window with tabbed interface
   - Real-time UI updates
   - Event handling and user interactions

3. import_export.py
   - Excel file processing with pandas
   - Multi-format export capabilities
   - Data validation and transformation

4. erd_generator.py
   - Visual ER diagram generation
   - PNG and PDF export functionality
   - Automatic relationship detection
   
### Key Features in Detail
1. Multi-Database Support
   - SQLite: Local file-based databases
   - MySQL: Remote database connections with authentication
   - Unified Interface: Same operations work across both database types

2. Smart Form Generation
   - Automatically creates appropriate input fields based on column data types
   - Foreign key fields show dropdowns with referenced table data
   - Date fields include calendar integration
3. History Management
   - Complete undo/redo functionality
   - Tracks all database modifications
   - Prevents data loss from accidental operations

4. ER Diagram Features
   - Automatic table positioning
   - Relationship lines with arrow indicators
   - Professional styling and formatting
   - High-resolution export options

   
## Technical Details
Built With:
- Python 3.8+: Core programming language
- Tkinter: GUI framework
- Pandas: Data manipulation and Excel handling
- Pillow: Image processing for ERD export
- MySQL Connector: MySQL database connectivity

Database Compatibility:
- SQLite 3.x
- MySQL 5.7+

Cross-platform compatibility (Windows, macOS, Linux)

## Future Enhancements
- PostgreSQL support
- Data validation rules
- Query builder interface
- Database comparison tools
- Backup and restore functionality
- Plugin system for extended functionality

## project structure
```bash
DBVisual-Manager/
├── main.py                 # Application entry point
├── gui.py                  # Main GUI implementation
├── database.py             # Database operations and connections
├── import_export.py        # Import/export functionality
├── erd_generator.py        # ER diagram generation
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
