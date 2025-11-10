#!/usr/bin/env python3
"""
Create app icon for Reminders to Google Calendar sync app.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple icon
size = 1024
img = Image.new('RGB', (size, size), color='#4285F4')  # Google blue

# Draw
draw = ImageDraw.Draw(img)

# Draw a calendar-like icon
margin = size // 8
calendar_rect = [margin, margin, size - margin, size - margin]
draw.rounded_rectangle(calendar_rect, radius=size//10, fill='white')

# Draw calendar header
header_height = size // 4
draw.rectangle([margin, margin, size - margin, margin + header_height], fill='#EA4335')  # Google red

# Draw some calendar grid
grid_margin = margin + size // 16
grid_start_y = margin + header_height + size // 16
cell_size = (size - 2 * grid_margin - margin) // 3

for row in range(2):
    for col in range(3):
        x = grid_margin + col * (cell_size + size // 32)
        y = grid_start_y + row * (cell_size + size // 32)
        draw.rectangle([x, y, x + cell_size, y + cell_size], fill='#FBBC04', outline='#4285F4', width=10)

# Save icon
icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
img.save(icon_path)
print(f"Icon created: {icon_path}")

# Create .icns file for Mac (requires iconutil)
# First create iconset directory structure
iconset_path = icon_path.replace('.png', '.iconset')
os.makedirs(iconset_path, exist_ok=True)

# Generate different sizes
sizes = [16, 32, 64, 128, 256, 512, 1024]
for icon_size in sizes:
    resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(iconset_path, f'icon_{icon_size}x{icon_size}.png'))
    if icon_size <= 512:
        # Also create @2x versions
        resized_2x = img.resize((icon_size * 2, icon_size * 2), Image.Resampling.LANCZOS)
        resized_2x.save(os.path.join(iconset_path, f'icon_{icon_size}x{icon_size}@2x.png'))

print(f"Iconset created: {iconset_path}")
print("To create .icns file, run:")
print(f"iconutil -c icns {iconset_path}")
