"""Extract drawing elements (lines) from the PDF to understand dimension placement."""
import pymupdf

pdf_path = r"C:\Users\Raj\repos\van-builds\01-Ford-Transit-2026\03-inputs\Measurements-Ford-Transit-148-Ext.pdf"

doc = pymupdf.open(pdf_path)
page = doc[0]

# Get all drawings (lines, rects, paths)
drawings = page.get_drawings()

print(f"Total drawing elements: {len(drawings)}\n")

# Also check for images
images = page.get_images()
print(f"Images on page: {len(images)}\n")

# Let's also get the text with more context - words with positions
words = page.get_text("words")  # (x0, y0, x1, y1, "word", block_no, line_no, word_no)
print("ALL WORDS with positions:")
print("="*70)
words_sorted = sorted(words, key=lambda w: (w[1], w[0]))
for w in words_sorted:
    print(f"  ({w[0]:6.1f}, {w[1]:6.1f}) - ({w[2]:6.1f}, {w[3]:6.1f})  \"{w[4]}\"")

doc.close()
