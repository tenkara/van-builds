"""Read dimensions from the Ford Transit layout guide image using EasyOCR."""
import easyocr
import sys

img_path = r"C:\Users\Raj\repos\van-builds\01-Ford-Transit-2026\03-inputs\Ford_Transit-Ext_148WB_0a3d84d9-63eb-4e17-90cb-c18d63e6e0e4.webp"

print("Loading EasyOCR (first run downloads model ~100MB)...")
reader = easyocr.Reader(['en'], gpu=False)

print(f"\nReading image: {img_path}\n")
results = reader.readtext(img_path, detail=1)

print("=" * 70)
print("ALL DETECTED TEXT (sorted top-to-bottom, left-to-right):")
print("=" * 70)

# Sort by Y position (top of bounding box), then X
results_sorted = sorted(results, key=lambda r: (r[0][0][1], r[0][0][0]))

for bbox, text, conf in results_sorted:
    top_left = bbox[0]
    print(f"  [{top_left[0]:6.0f}, {top_left[1]:6.0f}]  conf={conf:.2f}  \"{text}\"")

print("\n" + "=" * 70)
print("NUMBERS ONLY (likely dimensions):")
print("=" * 70)

import re
for bbox, text, conf in results_sorted:
    # Look for text containing numbers (dimensions)
    if re.search(r'\d', text):
        top_left = bbox[0]
        print(f"  [{top_left[0]:6.0f}, {top_left[1]:6.0f}]  conf={conf:.2f}  \"{text}\"")
