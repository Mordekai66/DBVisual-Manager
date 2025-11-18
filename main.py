# main.py
import tkinter as tk
from gui import create_main_window, setup_menu

def main():
    root = tk.Tk()
    root.title("Database Management Tool")
    root.geometry("1024x768")
    
    # Create the main window
    create_main_window(root)
    
    # Setup the menu
    setup_menu(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
