# erd_generator.py
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import os

def export_erd(canvas, file_path, format_type):
    """Export ERD as PNG or PDF"""
    # Get canvas dimensions
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    # Create image
    img = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Get canvas items
    items = canvas.find_all()
    
    # Draw items
    for item in items:
        item_type = canvas.type(item)
        
        if item_type == "rectangle":
            coords = canvas.coords(item)
            fill = canvas.itemcget(item, "fill")
            outline = canvas.itemcget(item, "outline")
            width = int(canvas.itemcget(item, "width"))
            
            draw.rectangle(coords, fill=fill, outline=outline, width=width)
        
        elif item_type == "line":
            coords = canvas.coords(item)
            fill = canvas.itemcget(item, "fill")
            width = int(canvas.itemcget(item, "width"))
            
            # Check if it has an arrow
            arrow = canvas.itemcget(item, "arrow")
            
            if arrow:
                # Draw line with arrow
                draw.line(coords, fill=fill, width=width)
                
                # Draw arrowhead
                x1, y1, x2, y2 = coords
                
                # Calculate arrowhead points
                angle = 3.14159 / 6  # 30 degrees
                length = 10
                
                # Calculate the angle of the line
                line_angle = tk.math.atan2(y2 - y1, x2 - x1)
                
                # Calculate arrowhead points
                ax1 = x2 - length * tk.math.cos(line_angle - angle)
                ay1 = y2 - length * tk.math.sin(line_angle - angle)
                ax2 = x2 - length * tk.math.cos(line_angle + angle)
                ay2 = y2 - length * tk.math.sin(line_angle + angle)
                
                # Draw arrowhead
                draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=fill)
            else:
                draw.line(coords, fill=fill, width=width)
        
        elif item_type == "text":
            coords = canvas.coords(item)
            text = canvas.itemcget(item, "text")
            fill = canvas.itemcget(item, "fill")
            font = canvas.itemcget(item, "font")
            
            # Parse font
            font_parts = font.split()
            font_family = font_parts[0]
            font_size = int(font_parts[1])
            
            # Check if bold
            font_weight = "normal"
            if "bold" in font_parts:
                font_weight = "bold"
            
            # Create font
            try:
                pil_font = ImageFont.truetype(font_family, font_size)
            except:
                pil_font = ImageFont.load_default()
            
            # Draw text
            draw.text((coords[0], coords[1]), text, fill=fill, font=pil_font)
    
    # Save image
    if format_type == "png":
        img.save(file_path)
    elif format_type == "pdf":
        img.save(file_path, "PDF", resolution=100.0)
