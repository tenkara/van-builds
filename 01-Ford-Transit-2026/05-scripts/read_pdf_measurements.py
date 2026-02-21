"""Extract text from the Ford Transit 148 Ext measurements PDF."""
import pymupdf

pdf_path = r"C:\Users\Raj\repos\van-builds\01-Ford-Transit-2026\03-inputs\Measurements-Ford-Transit-148-Ext.pdf"

doc = pymupdf.open(pdf_path)
print(f"Pages: {len(doc)}\n")

for i, page in enumerate(doc):
    print(f"{'='*70}")
    print(f"PAGE {i+1}")
    print(f"{'='*70}")
    text = page.get_text()
    print(text)
    print()

doc.close()
