"""Read dimensions from the second Ford Transit layout guide image."""
import easyocr, re

img_path = r"C:\Users\Raj\repos\van-builds\01-Ford-Transit-2026\03-inputs\Layout_Guide_Transit_148_EX_WB.jpg"

reader = easyocr.Reader(['en'], gpu=False)
results = reader.readtext(img_path, detail=1)
results_sorted = sorted(results, key=lambda r: (r[0][0][1], r[0][0][0]))

print("ALL TEXT:")
for bbox, text, conf in results_sorted:
    tl = bbox[0]
    print(f'  [{tl[0]:6.0f},{tl[1]:6.0f}] conf={conf:.2f}  "{text}"')

print("\nNUMBERS:")
for bbox, text, conf in results_sorted:
    if re.search(r'\d', text):
        tl = bbox[0]
        print(f'  [{tl[0]:6.0f},{tl[1]:6.0f}] conf={conf:.2f}  "{text}"')
