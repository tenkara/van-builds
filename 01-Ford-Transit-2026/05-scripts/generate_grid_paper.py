#!../../.venv/Scripts/python.exe
"""
Ford Transit Cargo Area Grid Paper Generator
==============================================
Generates a 1-inch grid pattern representing the Ford Transit cargo area
(160" length × 75" width) scaled to fit on A4 paper for hand-drawing layouts.

Each grid square represents 1 square inch of actual cargo space.
Output is optimized for A4 paper (210mm × 297mm or 8.27" × 11.69").
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

# ── Output paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "04-outputs"))
os.makedirs(OUT_DIR, exist_ok=True)
DPI = 300  # High resolution for printing

# ═════════════════════════════════════════════════════════════════════════════
# DIMENSIONS
# ═════════════════════════════════════════════════════════════════════════════

# Ford Transit cargo area (in inches)
CARGO_LENGTH = 168.0  # Length (north-south, front to rear)
CARGO_WIDTH = 84.0    # Width (east-west, driver to passenger)

# A4 paper dimensions (in inches)
A4_WIDTH_IN = 8.27    # 210mm
A4_HEIGHT_IN = 11.69  # 297mm

# Grid settings
GRID_SIZE = 1.0       # 1 inch per grid square
MARGIN = 0.5          # Margin around the grid in inches

# ═════════════════════════════════════════════════════════════════════════════
# CALCULATE SCALING
# ═════════════════════════════════════════════════════════════════════════════

# Available print area (accounting for margins)
available_width = A4_WIDTH_IN - (2 * MARGIN)
available_height = A4_HEIGHT_IN - (2 * MARGIN)

# Calculate scale factor to fit cargo area on A4 paper
# We need to fit 160" × 75" into available space
scale_x = available_width / CARGO_WIDTH
scale_y = available_height / CARGO_LENGTH

# Use the smaller scale to ensure it fits in both dimensions
scale = min(scale_x, scale_y)

# Scaled dimensions for drawing
scaled_width = CARGO_WIDTH * scale
scaled_length = CARGO_LENGTH * scale

print(f"Ford Transit Cargo Area: {CARGO_LENGTH}\" × {CARGO_WIDTH}\"")
print(f"A4 Paper: {A4_WIDTH_IN}\" × {A4_HEIGHT_IN}\"")
print(f"Scale factor: 1:{1/scale:.2f} (each {scale:.4f}\" on paper = 1\" in van)")
print(f"Scaled drawing size: {scaled_width:.2f}\" × {scaled_length:.2f}\"")

# ═════════════════════════════════════════════════════════════════════════════
# DRAWING FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def draw_grid_paper():
    """
    Generate grid paper with 1-inch squares scaled to fit A4 paper.
    """
    # Create figure with A4 dimensions
    fig, ax = plt.subplots(figsize=(A4_WIDTH_IN, A4_HEIGHT_IN), facecolor="white")
    ax.set_facecolor("white")
    ax.set_aspect("equal")

    # Set axis limits with margins
    ax.set_xlim(0, A4_WIDTH_IN)
    ax.set_ylim(0, A4_HEIGHT_IN)
    ax.axis("off")

    # Calculate starting position to center the grid
    start_x = (A4_WIDTH_IN - scaled_width) / 2
    start_y = (A4_HEIGHT_IN - scaled_length) / 2

    # Title
    title_y = start_y + scaled_length + 0.3
    ax.text(A4_WIDTH_IN / 2, title_y,
            "Ford Transit 148\" ELWB Cargo Area Grid Paper",
            fontsize=12, fontweight="bold", ha="center", va="bottom")
    ax.text(A4_WIDTH_IN / 2, title_y - 0.2,
            f"{int(CARGO_LENGTH)}\" Length × {int(CARGO_WIDTH)}\" Width • 1\" Grid Squares • Scale 1:{1/scale:.1f} • Origin (0,0) = Front Cab, Driver Side",
            fontsize=8, ha="center", va="top", color="#666666")

    # Draw outer border
    border = mpatches.Rectangle((start_x, start_y), scaled_width, scaled_length,
                                fill=False, edgecolor="#000000", linewidth=2, zorder=10)
    ax.add_patch(border)

    # Draw vertical grid lines (every 1 inch in actual space)
    num_vertical = int(CARGO_WIDTH / GRID_SIZE)
    for i in range(num_vertical + 1):
        x = start_x + (i * GRID_SIZE * scale)
        # Thicker line every 12 inches (1 foot)
        if i % 12 == 0:
            ax.plot([x, x], [start_y, start_y + scaled_length],
                   color="#333333", linewidth=0.8, zorder=5)
        else:
            ax.plot([x, x], [start_y, start_y + scaled_length],
                   color="#CCCCCC", linewidth=0.3, zorder=3)

    # Draw horizontal grid lines (every 1 inch in actual space)
    num_horizontal = int(CARGO_LENGTH / GRID_SIZE)
    for i in range(num_horizontal + 1):
        y = start_y + (i * GRID_SIZE * scale)
        # Thicker line every 12 inches (1 foot)
        if i % 12 == 0:
            ax.plot([start_x, start_x + scaled_width], [y, y],
                   color="#333333", linewidth=0.8, zorder=5)
        else:
            ax.plot([start_x, start_x + scaled_width], [y, y],
                   color="#CCCCCC", linewidth=0.3, zorder=3)

    # Add dimension labels on both sides
    # Origin (0,0) is at front cab, driver side (top-left corner)

    # Length labels (left and right sides) - 0 at top (front), increasing downward (toward rear)
    for i in range(0, int(CARGO_LENGTH) + 1, 12):  # Every foot
        y = start_y + scaled_length - (i * scale)  # Inverted: 0 at top, 160 at bottom
        # Left side (driver side)
        ax.text(start_x - 0.15, y, f'{i}"', fontsize=6, ha="right", va="center", color="#666666")
        # Right side (passenger side)
        ax.text(start_x + scaled_width + 0.15, y, f'{i}"', fontsize=6, ha="left", va="center", color="#666666")

    # Width labels (top and bottom) - 0 at left (driver), increasing rightward (toward passenger)
    for i in range(0, int(CARGO_WIDTH) + 1, 12):  # Every foot
        x = start_x + (i * scale)
        # Top (front)
        ax.text(x, start_y + scaled_length + 0.15, f'{i}"', fontsize=6, ha="center", va="bottom", color="#666666", rotation=0)
        # Bottom (rear)
        ax.text(x, start_y - 0.15, f'{i}"', fontsize=6, ha="center", va="top", color="#666666", rotation=0)

    # Add corner annotations and origin marker
    # Origin (0,0) at top-left: FRONT CAB, DRIVER SIDE
    ax.text(start_x - 0.05, start_y + scaled_length + 0.05, "ORIGIN\n(0,0)\nFRONT CAB",
           fontsize=7, ha="right", va="bottom", color="#CC0000", fontweight="bold")
    ax.text(start_x - 0.05, start_y - 0.05, f"REAR\nDOOR\n({int(CARGO_LENGTH)},0)",
           fontsize=7, ha="right", va="top", color="#333333", fontweight="bold")
    ax.text(start_x - 0.05, start_y + scaled_length / 2, "DRIVER\nSIDE",
           fontsize=7, ha="right", va="center", color="#666666", rotation=90)
    ax.text(start_x + scaled_width + 0.05, start_y + scaled_length / 2, "PASSENGER\nSIDE",
           fontsize=7, ha="left", va="center", color="#666666", rotation=90)

    # Add footer with instructions
    footer_text = (
        "Instructions: Each grid square = 1\" × 1\" of actual cargo space. "
        "Thick lines mark 12\" (1 foot) intervals. "
        "Draw your layout on this grid to visualize the van build at scale."
    )
    ax.text(A4_WIDTH_IN / 2, 0.2, footer_text,
           fontsize=6, ha="center", va="bottom", color="#666666", style="italic")

    # ══════════════════════════════════════════════════════════════════════════
    # SAVE OUTPUT
    # ══════════════════════════════════════════════════════════════════════════

    plt.tight_layout(pad=0)

    # Save PNG
    png_path = os.path.join(OUT_DIR, "ford-transit-grid-paper-a4.png")
    fig.savefig(png_path, dpi=DPI, facecolor="white", bbox_inches="tight", pad_inches=0.2)
    print(f"\n[PNG] Grid paper saved: {png_path}")

    # Save PDF for better printing quality
    pdf_path = os.path.join(OUT_DIR, "ford-transit-grid-paper-a4.pdf")
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, facecolor="white", bbox_inches="tight", pad_inches=0.2)
    print(f"[PDF] Grid paper saved: {pdf_path}")

    plt.close(fig)

    return png_path, pdf_path


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("Ford Transit 148\" ELWB – Grid Paper Generator")
    print("=" * 70)

    png_file, pdf_file = draw_grid_paper()

    print("-" * 70)
    print("✅ Grid paper generated successfully!")
    print(f"   PNG: {png_file}")
    print(f"   PDF: {pdf_file} (recommended for printing)")
    print("-" * 70)
    print("\nPrint the PDF at 100% scale (do not scale to fit) on A4 paper.")
    print("Use the grid to hand-draw your van layout ideas.")
    print("=" * 70)
