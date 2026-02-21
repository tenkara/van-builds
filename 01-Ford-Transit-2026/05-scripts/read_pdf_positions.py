"""Extract text with positions from the Ford Transit 148 Ext measurements PDF."""
import pymupdf
from pathlib import Path

# Build path relative to this script's location
script_dir = Path(__file__).parent
pdf_path = script_dir.parent / "03-inputs" / "Measurements-Ford-Transit-148-Ext.pdf"

doc = pymupdf.open(pdf_path)
page = doc[0]  # First page has the layout diagram

# Get text blocks with positions
blocks = page.get_text("dict")["blocks"]

print("TEXT BLOCKS (sorted by position):")
print("="*70)

items = []
for block in blocks:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    bbox = span["bbox"]  # (x0, y0, x1, y1)
                    items.append((bbox[1], bbox[0], text, bbox))

# Sort by Y (top-to-bottom), then X (left-to-right)
items.sort()

for y, x, text, bbox in items:
    print(f"  x={bbox[0]:6.1f}  y={bbox[1]:6.1f}  →  \"{text}\"")

print(f"\nPage size: {page.rect.width:.0f} x {page.rect.height:.0f}")

doc.close()
